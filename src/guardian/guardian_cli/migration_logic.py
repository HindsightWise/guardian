import os
import sys
import typer
from pathlib import Path
from guardian.utils import run_alembic_command

def show_status():
    """
    Shows the current migration status by running 'alembic current'.
    """
    typer.echo("Checking migration status...")
    cwd = Path(os.getcwd())
    output = run_alembic_command(["current"], cwd)
    typer.echo(f"Result: {output or 'None (database not stamped)'}")

def upgrade_database():
    """
    Applies all pending migrations by running 'alembic upgrade head'.
    """
    typer.echo("Applying migrations...")
    cwd = Path(os.getcwd())
    run_alembic_command(["upgrade", "head"], cwd)
    typer.echo("\nMigration process complete.")

def create_initial_migration(message: str):
    """
    Creates the first migration script using 'alembic revision --autogenerate'.
    """
    typer.echo(f"Creating initial migration: '{message}'...")
    cwd = Path(os.getcwd())
    run_alembic_command(["revision", "--autogenerate", "-m", message], cwd)
    typer.echo("\nInitial migration script created. Run 'guardian-cli up' to apply it.")

def show_history():
    """
    Shows the migration history.
    """
    typer.echo("Showing migration history...")
    cwd = Path(os.getcwd())
    output = run_alembic_command(["history"], cwd)
    typer.echo(output)