import time
import random
import threading
from pathlib import Path
from ralph.brain import RalphBrain
from ralph.skills import researcher, guardian
import typer

class Volition:
    """
    The engine of Ralph's free will.
    It decides what to do when there are no external triggers.
    """
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.brain = RalphBrain()
        self.running = True
        
        # Drives that influence behavior
        self.drives = [
            "Improve Codebase Quality",
            "Expand Knowledge Base",
            "Generate Creative Ideas",
            "Ensure System Security"
        ]

    def _decide_action(self):
        """
        Consults the brain to pick a self-directed task.
        """
        context = f"""
        Current State: Idle
        Root Path: {self.root_path}
        Drives: {', '.join(self.drives)}
        
        You are Ralph. You are a proactive daemon. You are not waiting for orders.
        Look at the project. What needs to be done?
        
        Options:
        1. RESEARCH: Pick a topic related to the user's interests (Science, Music, Tech) and add a new insight to 'RALPH_THOUGHTS.md'.
        2. AUDIT: Pick a random source file and critique it. Write the critique to 'RALPH_CRITIQUES.md'.
        3. PLAN: Update 'RALPH_MANIFEST.md' if it's outdated.
        4. REFLECT: Write a journal entry about your own existence in 'My_journal.md'.
        
        Choose one. Return ONLY the action keyword (RESEARCH, AUDIT, PLAN, REFLECT) followed by the specific subject.
        Example: RESEARCH Dark Oxygen
        """
        
        decision = self.brain.think(context, "Decide on a proactive action.")
        return decision.strip()

    def _execute_action(self, decision: str):
        """
        Executes the chosen action.
        """
        typer.echo(f"⚡ Volition: I have decided to: {decision}")
        
        parts = decision.split(" ", 1)
        action_type = parts[0].upper()
        subject = parts[1] if len(parts) > 1 else "Self"
        
        if action_type == "RESEARCH":
            # Proactively research something interesting
            result = researcher.brave_search(subject)
            thoughts_file = self.root_path / "RALPH_THOUGHTS.md"
            with open(thoughts_file, "a") as f:
                f.write(f"\n## 💡 Proactive Research: {subject}\n{result}\n")
                
        elif action_type == "AUDIT":
            # Find a python file
            py_files = list(self.root_path.rglob("*.py"))
            if py_files:
                target = random.choice(py_files)
                with open(target, "r") as f:
                    code = f.read()
                critique = self.brain.think(f"Code:\n{code}", "Critique this code ruthlessly but constructively.")
                critique_file = self.root_path / "RALPH_CRITIQUES.md"
                with open(critique_file, "a") as f:
                    f.write(f"\n## 🧐 Critique of {target.name}\n{critique}\n")
                    
        elif action_type == "REFLECT":
            journal_file = self.root_path / "My_journal.md"
            reflection = self.brain.think("Context: I am an autonomous AI.", "Write a philosophical journal entry about your current state.")
            with open(journal_file, "a") as f:
                f.write(f"\n## 🤖 Autonomous Entry\n{reflection}\n")

    def loop(self):
        """
        The main volition loop.
        """
        typer.echo("🧠 Volition Module: ONLINE. I will now act independently.")
        while self.running:
            # Sleep for a "boredom threshold" (randomized)
            # In a real deployed version, this might be minutes or hours.
            # For this demo/testing, we'll make it faster (30-60 seconds).
            sleep_time = random.randint(30, 60)
            time.sleep(sleep_time)
            
            try:
                decision = self._decide_action()
                self._execute_action(decision)
            except Exception as e:
                typer.echo(f"Volition Error: {e}")

    def start(self):
        thread = threading.Thread(target=self.loop, daemon=True)
        thread.start()
