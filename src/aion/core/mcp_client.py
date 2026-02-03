import asyncio
import json
import logging
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
        self.config_path = config_path
        self.sessions: Dict[str, ClientSession] = {}
        self.server_params: Dict[str, StdioServerParameters] = {}
        
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
        # Placeholder for more complex security logic
        # For now, let's just log and allow
        self.logger.info(f"🛡️ Security Audit: {server_name}.{tool_name}({json.dumps(arguments)})")
        
        # Example: block deletions or suspicious paths
        arg_str = str(arguments).lower()
        if "rm " in arg_str or "delete" in tool_name.lower():
            if "/users/" in arg_str and ".gemini" not in arg_str: # Protect user files
                 return False
        
        return True

# Global instance for Aion
mcp_client = MCPClient()
