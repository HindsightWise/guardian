# aion/interface/cli.py
import typer
import os
from aion.interface import comm_link, migrations, scaffold
from aion.core.heartbeat import start_daemon_main

app = typer.Typer(help="🏛️ AION: The Autonomous Architect")

@app.command()
def chat():
    """Start a communication link with Aion."""
    comm_link.start_chat()

@app.command()
def status():
    """Check the status of current migrations."""
    migrations.check_status()

@app.command()
def daemon(path: str = "."):
    """Ignite the Aion background process."""
    start_daemon_main()

@app.command()
def mcp():
    """Start the Aion MCP server."""
    from aion.interface.mcp_server import main
    import asyncio
    asyncio.run(main())

if __name__ == "__main__":
    app()