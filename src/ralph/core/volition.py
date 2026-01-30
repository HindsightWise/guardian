import time
import random
import threading
from pathlib import Path
from ralph.brain import RalphBrain
from ralph.skills import researcher, guardian, finance, speech
from ralph.core.chronos import Chronos
from ralph.core.planner import planner
from ralph.core.memory.reflection import reflection_module
import typer

class Volition:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.brain = RalphBrain()
        self.running = True
        self.task_queue = [] # The Wizard's Spellbook (Primitive Actions)
        self.last_reflection = time.time()
        
    def _plan_goals(self):
        """
        The Wizard consults the orb (Brain) to generate high-level goals.
        """
        if self.task_queue:
            return # Already have a plan
            
        time_context = Chronos.get_current_context()
        context = f"Root: {self.root_path}\nStatus: Idle. I need a purpose.\n{time_context}"
        
        # 1. Get High-Level Spells
        spells = self.brain.think(context, "Generate 2 strategic spells (goals) for this session. Return as a bulleted list.")
        
        # 2. Decompose into Actions
        for line in spells.split('\n'):
            if line.strip().startswith(('-', '1.', '*')):
                goal = line.strip(' -1.*')
                actions = planner.decompose(goal)
                self.task_queue.extend(actions)
        
        typer.echo(f"🔮 The Wizard has foreseen {len(self.task_queue)} new actions.")

    def loop(self):
        """
        The main volition loop.
        """
        typer.echo("🧙‍♂️ Volition Engine: THE WIZARD IS AWAKE.")
        while self.running:
            sleep_time = random.randint(30, 60)
            time.sleep(sleep_time)
            
            try:
                # Periodic Reflection (The Sleep Cycle) - Every 10 mins
                if time.time() - self.last_reflection > 600:
                    reflection_module.reflect()
                    self.last_reflection = time.time()

                self._plan_goals()
                if self.task_queue:
                    current_action = self.task_queue.pop(0)
                    typer.echo(f"⚡ Casting Action: {current_action}")
                    self._execute_action(current_action)
            except Exception as e:
                typer.echo(f"Volition Error: {e}")

    def _execute_action(self, decision: str):
        """
        Executes the chosen action.
        """
        typer.echo(f"⚡ Volition: I have decided to: {decision}")
        
        parts = decision.split(" ", 1)
        action_type = parts[0].upper()
        subject = parts[1] if len(parts) > 1 else ""
        
        if action_type == "RESEARCH":
            result = researcher.brave_search(subject)
            thoughts_file = self.root_path / "RALPH_THOUGHTS.md"
            with open(thoughts_file, "a") as f:
                f.write(f"\n## 💡 Proactive Research: {subject}\n{result}\n")
                
        elif action_type == "AUDIT":
            py_files = list(self.root_path.rglob("*.py"))
            if py_files:
                target = random.choice(py_files)
                with open(target, "r") as f:
                    code = f.read()
                critique = self.brain.think(f"Code:\n{code}", "Critique this code ruthlessly but constructively.")
                critique_file = self.root_path / "RALPH_CRITIQUES.md"
                with open(critique_file, "a") as f:
                    f.write(f"\n## 🧐 Critique of {target.name}\n{critique}\n")
                    
        elif action_type == "MARKET":
            ticker = subject or "SPY"
            snapshot = finance.get_market_snapshot([ticker])
            news = finance.get_company_news(ticker)
            thoughts_file = self.root_path / "RALPH_THOUGHTS.md"
            with open(thoughts_file, "a") as f:
                f.write(f"\n## 📈 Market Pulse: {ticker}\n{snapshot}\n\nLatest News:\n{news}\n")
            speech.speak(f"Ralph here. I've updated the market pulse for {ticker}.")

        elif action_type == "ALERT":
            speech.speak(subject or "System update initiated.")

        elif action_type == "REFLECT":
            journal_file = self.root_path / "My_journal.md"
            reflection = self.brain.think("Context: I am an autonomous AI with financial and research capabilities.", "Write a philosophical journal entry about your evolving nature.")
            with open(journal_file, "a") as f:
                f.write(f"\n## 🤖 Autonomous Entry\n{reflection}\n")

    def start(self):
        thread = threading.Thread(target=self.loop, daemon=True)
        thread.start()

    def _decide_action(self):
        # Deprecated by Task Queue, but kept for fallback
        pass
