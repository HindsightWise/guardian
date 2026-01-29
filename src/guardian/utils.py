# guardian/src/guardian/utils.py
import os
import sys
import subprocess
import typer
from pathlib import Path

def run_alembic_command(args: list[str], cwd: Path):
    """
    Runs an alembic command using subprocess, ensuring it uses the
    correct executable from the project's virtual environment.
    """
    # Define project_root based on the location of this utils.py file
    script_dir = Path(__file__).parent # guardian/src/guardian
    project_root = script_dir.parent.parent.parent # /Users/zerbytheboss/Desktop/google_cli/WritingPro
    alembic_exe = project_root / "venv" / "bin" / "alembic"

    if not alembic_exe.exists():
        typer.echo(f"Error: Could not find 'alembic' executable at {alembic_exe}")
        typer.echo(f"  (Calculated project root: {project_root})")
        raise typer.Exit(1)
    
    # Find alembic.ini in the current directory or parents
    alembic_ini_path = None
    current_dir = cwd
    while current_dir != current_dir.parent: # Loop up to find alembic.ini
        if (current_dir / "alembic.ini").exists():
            alembic_ini_path = current_dir / "alembic.ini"
            break
        current_dir = current_dir.parent
    
    if not alembic_ini_path:
        typer.echo(f"Error: alembic.ini not found in current directory or parent directories from {cwd}")
        raise typer.Exit(1)

    # --- DIAGNOSTIC START ---
    typer.echo(f"--- Alembic Config Diagnostic for '{alembic_ini_path.name}' ---")
    diagnostic_command = [str(alembic_exe), "-c", alembic_ini_path.name, "show", "config"] # Corrected -c flag
    try:
        diagnostic_result = subprocess.run(diagnostic_command, capture_output=True, text=True, check=False, cwd=cwd)
        typer.echo(f"Diagnostic command: {' '.join(diagnostic_command)}")
        typer.echo(f"Diagnostic STDOUT: {diagnostic_result.stdout.strip() if diagnostic_result.stdout else '[EMPTY]'}")
        typer.echo(f"Diagnostic STDERR: {diagnostic_result.stderr.strip() if diagnostic_result.stderr else '[EMPTY]'}")
        if diagnostic_result.returncode != 0:
            typer.echo(f"Diagnostic failed with exit code {diagnostic_result.returncode}")
            # Don't exit here, let the main command try, but this info is crucial
    except Exception as e:
        typer.echo(f"Error during config diagnostic: {e}")
    typer.echo("-----------------------------------------------")
    # --- DIAGNOSTIC END ---

    command = [str(alembic_exe), "-c", alembic_ini_path.name] + args # Corrected -c flag
    typer.echo(f"Running command: {' '.join(command)}")

    try:
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True,
            check=False, # Don't raise error, we'll handle it
            cwd=cwd
        )

        typer.echo("--- Alembic STDOUT ---")
        typer.echo(result.stdout.strip() if result.stdout else "[EMPTY]")
        typer.echo("--- Alembic STDERR ---")
        typer.echo(result.stderr.strip() if result.stderr else "[EMPTY]")

        if result.returncode != 0:
            typer.echo(f"Alembic command failed with exit code {result.returncode}")
            raise typer.Exit(1)
            
        return result.stdout.strip()

    except FileNotFoundError:
        typer.echo(f"Error: Could not execute alembic command. Is '{alembic_exe}' correct?")
        raise typer.Exit(1)