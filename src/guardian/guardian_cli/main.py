# guardian_cli/main.py
import typer
import importlib.util
import sys
from pathlib import Path
from . import init_logic
from . import migration_logic

app = typer.Typer()

@app.command()
def init():
    """
    Initializes the Guardian migration environment.
    """
    init_logic.initialize_environment()

@app.command()
def status():
    """
    Checks the status of database migrations.
    """
    migration_logic.show_status()

@app.command()
def up():
    """
    Applies the next pending migration.
    """
    migration_logic.upgrade_database()

@app.command()
def initial(message: str = typer.Argument("Initial migration", help="Message for the initial migration.")):
    """
    Creates the first migration script.
    """
    migration_logic.create_initial_migration(message)

@app.command()
def history(): # NEW COMMAND
    """
    Shows the migration history.
    """
    migration_logic.show_history()

@app.command()
def run(protocol_name: str):
    """
    Runs a specified MCP protocol.
    """
    protocol_path = Path(__file__).parent.parent / "protocols" / f"{protocol_name}.py"
    if not protocol_path.exists():
        typer.echo(f"Error: Protocol '{protocol_name}' not found at {protocol_path}")
        raise typer.Exit(code=1)

    try:
        spec = importlib.util.spec_from_file_location(protocol_name, protocol_path)
        if spec is None:
            typer.echo(f"Error: Could not load spec for protocol '{protocol_name}'")
            raise typer.Exit(code=1)
        module = importlib.util.module_from_spec(spec)
        sys.modules[protocol_name] = module
        if spec.loader is None:
            typer.echo(f"Error: Could not load module for protocol '{protocol_name}'")
            raise typer.Exit(code=1)
        spec.loader.exec_module(module)

        if hasattr(module, "execute_protocol"):
            typer.echo(f"Running protocol: {protocol_name}...")
            module.execute_protocol()
            typer.echo(f"Protocol '{protocol_name}' completed.")
        else:
            typer.echo(f"Error: Protocol '{protocol_name}' must have an 'execute_protocol' function.")
            raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"An error occurred while running protocol '{protocol_name}': {e}")
        raise typer.Exit(code=1)


def main():
    app()

if __name__ == "__main__":
    main()
