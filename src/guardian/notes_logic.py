from guardian.brain import GuardianBrain
import typer
from pathlib import Path

def handle_notes_update(file_path: Path):
    """
    Analyzes the notes file for questions or commands.
    """
    brain = GuardianBrain()
    
    try:
        content = file_path.read_text()
        # Look for a specific trigger to avoid loop, e.g., "HEY RALPH:"
        if "HEY RALPH:" in content and "RALPH SAYS:" not in content.split("HEY RALPH:")[-1]:
            # Get the last prompt
            prompt = content.split("HEY RALPH:")[-1].strip()
            
            typer.echo(f"🧠 Ralph detected a query in {file_path.name}: {prompt[:50]}...")
            
            response = brain.think(
                context="You are Ralph, an intelligent, sarcastic, and proactive AI assistant. The user is asking you for help in their notes file.", 
                task=f"Answer this request found in the user's notes: {prompt}"
            )
            
            # Append response
            with open(file_path, "a") as f:
                f.write(f"\n\n--- 🤖 RALPH SAYS: ---\n{response}\n----------------------\n")
            
            typer.echo("🧠 Ralph responded in the notes file.")
            
    except Exception as e:
        typer.echo(f"Error handling notes: {e}")
