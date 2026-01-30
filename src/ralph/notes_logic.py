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
        print(f"DEBUG: Reading {file_path.name}, length: {len(content)}")
        # Look for a specific trigger to avoid loop, e.g., "HEY RALPH:"
        if "HEY RALPH:" in content:
            parts = content.split("HEY RALPH:")
            last_part = parts[-1]
            
            if "RALPH SAYS:" not in last_part:
                prompt = last_part.strip()
                print(f"DEBUG: Found prompt: {prompt}")
                
                typer.echo(f"🧠 Ralph detected a query in {file_path.name}: {prompt[:50]}...")
                
                response = brain.think(
                    context="You are Ralph, an intelligent, sarcastic, and proactive AI assistant. The user is asking you for help in their notes file.", 
                    task=f"Answer this request found in the user's notes: {prompt}"
                )
                
                # Append response
                with open(file_path, "a") as f:
                    f.write(f"\n\n--- 🤖 RALPH SAYS: ---\n{response}\n----------------------\n")
                
                print("DEBUG: Wrote response to file.")
                typer.echo("🧠 Ralph responded in the notes file.")
            else:
                print("DEBUG: Already responded to this prompt.")
    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        typer.echo(f"Error handling notes: {e}")
