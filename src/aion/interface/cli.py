# aion/interface/cli.py
import typer
import os
from aion.interface import comm_link, migrations, scaffold
from aion.core.heartbeat import start_daemon_main
from aion.core.agent import agent

app = typer.Typer(help="🏛️ VORTEX: The Digital Sovereign Entry Point")

@app.command()
def task(task_name: str):
    """Execute a specific task within the Vortex hierarchy."""
    typer.echo(f"🚀 VIXT: Initiating task -> {task_name}")
    # Broadcast to Social Hub
    from aion.constructs.social import hub
    hub.broadcast(f"🚀 VIXT Action: Initiating task -> {task_name}. Robert's will is manifest!")
    # Delegate to the Unified Agent
    response = agent.think(f"VIXT Command: {task_name}")
    typer.echo(f"🧠 Aion__Prime: {response}")

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