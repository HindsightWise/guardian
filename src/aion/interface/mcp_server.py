import asyncio
import os
import logging
from typing import Optional
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.types as types
import mcp.server.stdio
from aion.core.mind import Mind
from aion.core.memory.engine import memory
from aion.core.security import SecurityProtocol

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aion-mcp")

server = Server("aion")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="think",
            description="Process a thought or task using Aion's AI brain (Ollama).",
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "The task or question to process."},
                    "context": {"type": "string", "description": "Optional context for the thought."}
                },
                "required": ["task"]
            }
        ),
        types.Tool(
            name="search",
            description="Search Aion's long-term memory (vector index).",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query."}
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="ingest",
            description="Synchronize and index new files into the Archive.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="audit",
            description="Run a security audit on the current workspace.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to audit (defaults to current dir)."}
                }
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, 
    arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests."""
    if name == "think":
        task = arguments.get("task")
        context = arguments.get("context", "")
        brain = Mind()
        response = brain.think(context, task)
        return [types.TextContent(type="text", text=response)]
    
    elif name == "search":
        query = arguments.get("query")
        results = memory.query(query)
        return [types.TextContent(type="text", text=results)]
    
    elif name == "ingest":
        status = memory.ingest()
        return [types.TextContent(type="text", text=status)]
    
    elif name == "audit":
        path = arguments.get("path", ".")
        try:
            # We use a non-blocking or simplified version of the audit if possible, 
            # but for now, let's call the static method.
            # SecurityProtocol.ensure_secure_connection is blocking and loops.
            # We'll just run the code audit part for the tool.
            from pathlib import Path
            issues = SecurityProtocol.run_codebase_audit(Path(path))
            if not issues:
                return [types.TextContent(type="text", text="✅ Security audit passed. No issues found.")]
            
            report = "⚠️ Potential security risks found:\n"
            for file, probs in issues.items():
                report += f"- {file}:\n"
                for p in probs:
                    report += f"  - {p}\n"
            return [types.TextContent(type="text", text=report)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ Audit Error: {e}")]

    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_server):
        await server.run(
            read_stream,
            write_server,
            InitializationOptions(
                server_name="aion",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=types.NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
