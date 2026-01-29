from typing import Any
import asyncio
from mcp.server import Server # Assuming standard import structure
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from guardian.brain import GuardianBrain
import guardian.daemon_logic as logic
from pathlib import Path

# Initialize
brain = GuardianBrain()
server = Server("guardian-mcp")

@server.tool()
async def review_migration(code: str) -> str:
    """Reviews a database migration script for safety issues."""
    return brain.review_migration(code)

@server.tool()
async def analyze_safety(context: str) -> str:
    """Analyzes a general coding context for safety implications."""
    return brain.think(context, "Analyze the safety of this context.")

# Entry point
def start_mcp_server():
    """Starts the MCP server over stdio."""
    print("Guardian MCP Server starting...", file=sys.stderr)
    server.run_stdio()

if __name__ == "__main__":
    import sys
    start_mcp_server()
