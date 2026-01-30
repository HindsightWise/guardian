import time
import random
import threading
from pathlib import Path
from ralph.brain import RalphBrain
from ralph.skills import researcher, guardian, finance, speech
import typer

class Volition:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.brain = RalphBrain()
        self.running = True
        self.task_queue = [] # The Wizard's Spellbook (To-Do List)
        
    def _plan_goals(self):
        """
        The Wizard consults the orb (Brain) to generate high-level goals.
        """
        if self.task_queue:
            return # Already have a plan
            
        context = f"Root: {self.root_path}\nStatus: Idle. I need a purpose."
        new_goals = self.brain.think(context, "Generate 3 strategic goals for this session (e.g., Research X, Secure Y). Return as a list.")
        
        # Simple parsing of the list (naive but effective for now)
        for line in new_goals.split('\n'):
            if line.strip().startswith(('-', '1.', '*')):
                self.task_queue.append(line.strip(' -1.*'))
        
        typer.echo(f"🔮 The Wizard has foreseen {len(self.task_queue)} new paths.")

    def loop(self):
        """
        The main volition loop.
        """
        typer.echo("🧙‍♂️ Volition Engine: THE WIZARD IS AWAKE.")
        while self.running:
            sleep_time = random.randint(30, 60)
            time.sleep(sleep_time)
            
            try:
                self._plan_goals()
                if self.task_queue:
                    current_task = self.task_queue.pop(0)
                    typer.echo(f"⚡ Casting Spell: {current_task}")
                    # Here we would map the natural language task to a skill.
                    # For now, we fallback to the old 'decide_action' logic but seeded with the task.
                    # In the future: True Agentic Planning via ElizaOS patterns.
                    self._execute_action(f"RESEARCH {current_task}") # Defaulting to research for abstract goals
            except Exception as e:
                typer.echo(f"Volition Error: {e}")

    def _decide_action():
        # Deprecated by Task Queue, but kept for fallback
        pass
