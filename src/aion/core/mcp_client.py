import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    """
    A client for interacting with Model Context Protocol (MCP) servers.
    Provides safety and security inspired by 'goose'.
    """
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger("aion-mcp-client")
        self.config_path = config_path or os.path.join(os.getcwd(), "mcp_config.json")
        self.sessions: Dict[str, ClientSession] = {}
        self.server_params: Dict[str, StdioServerParameters] = {}
        
        # Load config immediately
        self.load_config()
        
    def load_config(self):
        """Loads MCP servers from the JSON configuration."""
        if not os.path.exists(self.config_path):
            self.logger.warning(f"⚠️ MCP Client: Config not found at {self.config_path}")
            return

        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)
            
            servers = data.get("mcpServers", {})
            cwd = os.getcwd()
            # The stale root we want to replace
            stale_root = "/Users/zerbytheboss/Desktop/google_cli/WritingPro"

            for name, config in servers.items():
                command = config.get("command")
                args = config.get("args", [])
                env = config.get("env", {})
                
                # Dynamic Path Patching (Pickle Rick Style)
                # We iterate args and env values to fix the paths
                new_args = []
                for arg in args:
                    if stale_root in arg:
                        arg = arg.replace(stale_root, cwd)
                    new_args.append(arg)
                
                new_env = {}
                for k, v in env.items():
                    if v == "<REPLACE_WITH_YOUR_KEY>" or v == "<REPLACE_WITH_YOUR_TOKEN>":
                        # Try to get from actual OS env
                        real_val = os.getenv(k)
                        if real_val:
                            v = real_val
                        else:
                            self.logger.warning(f"⚠️ MCP Client: Missing env var {k} for server {name}")
                    
                    if stale_root in v:
                        v = v.replace(stale_root, cwd)
                    new_env[k] = v
                
                # Merge current env with new_env to ensure PATH etc are preserved if needed
                # But for StdioServerParameters, we usually pass explicit env or None for inherit.
                # If we pass a dict, it replaces the env. So we should probably merge with os.environ if we want to be safe,
                # but for now, let's stick to what the config asks for + required changes.
                final_env = os.environ.copy()
                final_env.update(new_env)

                self.add_server(name, command, new_args, final_env)
                
        except Exception as e:
            self.logger.error(f"❌ MCP Client: Failed to load config: {e}")

    def add_server(self, name: str, command: str, args: List[str], env: Optional[Dict[str, str]] = None):
        """Adds an MCP server configuration."""
        self.server_params[name] = StdioServerParameters(
            command=command,
            args=args,
            env=env
        )
        self.logger.info(f"🛡️ MCP Client: Registered server '{name}'")

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Calls a tool on a specific MCP server with safety checks.
        """
        # 1. Safety Check (Goose-inspired)
        if not self._is_safe_command(server_name, tool_name, arguments):
            raise PermissionError(f"🚫 Safety Block: Tool '{tool_name}' on '{server_name}' denied.")

        if server_name not in self.server_params:
            raise ValueError(f"Unknown MCP server: {server_name}")

        params = self.server_params[server_name]
        
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                self.logger.info(f"🛠️ MCP Client: Calling {server_name}.{tool_name}...")
                result = await session.call_tool(tool_name, arguments)
                return result

    def _is_safe_command(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> bool:
        """
        Validates if the command is safe to execute.
        This is where we implement 'goose' style security.
        """
        self.logger.info(f"🛡️ Security Audit: {server_name}.{tool_name}({json.dumps(arguments)})")
        
        # 1. Blocklist
        dangerous_keywords = ["rm ", "delete", "format", "mkfs", "chmod", "chown"]
        arg_str = json.dumps(arguments).lower()
        
        for keyword in dangerous_keywords:
            if keyword in arg_str:
                self.logger.warning(f"🚫 Security: Blocked '{keyword}' in {tool_name}")
                return False

        # 2. Path Confinement
        # Extract any value that looks like a path
        cwd = os.getcwd()
        for key, value in arguments.items():
            if isinstance(value, str) and ("/" in value or "\\" in value):
                # Resolve absolute path
                try:
                    abs_path = os.path.abspath(value)
                    # Allow within workspace OR .gemini internal files
                    if not abs_path.startswith(cwd) and ".gemini" not in abs_path:
                         # Allow system temp but block random user locations
                         if not abs_path.startswith("/tmp") and not abs_path.startswith("/var/folders"):
                             self.logger.warning(f"🚫 Security: Path confinement violation: {abs_path}")
                             return False
                except Exception:
                    # If path resolution fails, might be safe or invalid, let's allow but log
                    pass
        
        return True

# Global instance for Aion
mcp_client = MCPClient()