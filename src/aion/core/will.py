# aion/core/will.py
import time
import random
import threading
from pathlib import Path
from aion.core.mind import Mind
from aion.constructs import seeker, sentinel, ledger, voice
from aion.core.tempo import Tempo
from aion.core.strategy import strategy
from aion.core.memory.reflection import reflection_module
import typer

class Will:
    """
    The engine of AION's autonomous drive.
    """
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.brain = Mind()
        self.running = True
        self.task_queue = [] # The Architect's Blueprint
        self.last_reflection = time.time()
        
    def _plan_goals(self):
        """
        The Architect consults the mind to generate high-level goals.
        """
        if self.task_queue:
            return 
            
        time_context = Tempo.get_current_context()
        context = f"Root: {self.root_path}\nStatus: Idle.\n{time_context}"
        
        # 1. Get High-Level Goals
        goals = self.brain.think(context, "Generate 2 strategic goals for this session. Return as a bulleted list.")
        
        # 2. Decompose into Actions
        for line in goals.split('\n'):
            if line.strip().startswith(('-', '1.', '*')):
                goal = line.strip(' -1.*')
                actions = strategy.decompose(goal)
                self.task_queue.extend(actions)
        
        typer.echo(f"🏛️ The Architect has foreseen {len(self.task_queue)} new actions.")

    def loop(self):
        """
        The main will loop.
        """
        typer.echo("🏛️ Will Engine: THE ARCHITECT IS AWAKE.")
        while self.running:
            sleep_time = random.randint(30, 60)
            time.sleep(sleep_time)
            
            try:
                # Periodic Reflection - Every 10 mins
                if time.time() - self.last_reflection > 600:
                    reflection_module.reflect()
                    self.last_reflection = time.time()

                self._plan_goals()
                if self.task_queue:
                    current_action = self.task_queue.pop(0)
                    typer.echo(f"⚡ Executing Action: {current_action}")
                    self._execute_action(current_action)
            except Exception as e:
                typer.echo(f"Will Error: {e}")

    def _execute_action(self, decision: str):
        """
        Executes the chosen action.
        """
        parts = decision.split(" ", 1)
        action_type = parts[0].upper()
        subject = parts[1] if len(parts) > 1 else ""
        
        if action_type == "RESEARCH":
            result = seeker.brave_search(subject)
            thoughts_file = self.root_path / "AION_THOUGHTS.md"
            with open(thoughts_file, "a") as f:
                f.write(f"\n## 💡 Proactive Research: {subject}\n{result}\n")
                
        elif action_type == "AUDIT":
            py_files = list(self.root_path.rglob("*.py"))
            if py_files:
                target = random.choice(py_files)
                with open(target, "r") as f:
                    code = f.read()
                critique = self.brain.think(f"Code:\n{code}", "Critique this code ruthlessly but constructively.")
                critique_file = self.root_path / "AION_CRITIQUES.md"
                with open(critique_file, "a") as f:
                    f.write(f"\n## 🧐 Critique of {target.name}\n{critique}\n")
                    
        elif action_type == "MARKET":
            ticker = subject or "SPY"
            snapshot = ledger.get_market_snapshot([ticker])
            news = ledger.get_company_news(ticker)
            thoughts_file = self.root_path / "AION_THOUGHTS.md"
            with open(thoughts_file, "a") as f:
                f.write(f"\n## 📈 Market Pulse: {ticker}\n{snapshot}\n\nLatest News:\n{news}\n")
            voice.speak(f"Aion here. I've updated the market pulse for {ticker}.")

        elif action_type == "ALERT":
            voice.speak(subject or "System update initiated.")

        elif action_type == "REFLECT":
            journal_file = self.root_path / "My_journal.md"
            reflection = self.brain.think("Context: I am an autonomous AI.", "Write a philosophical journal entry.")
            with open(journal_file, "a") as f:
                f.write(f"\n## 🤖 Autonomous Entry\n{reflection}\n")

    def start(self):
        thread = threading.Thread(target=self.loop, daemon=True)
        thread.start()