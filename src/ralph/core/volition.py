import time
import random
import threading
from pathlib import Path
from ralph.brain import RalphBrain
from ralph.skills import researcher, guardian, finance, speech
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
            "Monitor Financial Markets",
            "System Security"
        ]

    def _decide_action(self):
        """
        Consults the brain to pick a self-directed task.
        """
        context = f"""
        Current State: Idle
        Root Path: {self.root_path}
        Drives: {', '.join(self.drives)}
        
        You are Ralph. You are a proactive daemon. 
        Look at the project and the world. What needs to be done?
        
        Options:
        1. RESEARCH [topic]: Find new insights.
        2. AUDIT: Critique source files.
        3. MARKET: Analyze stock trends or portfolio.
        4. REFLECT: Write in 'My_journal.md'.
        5. ALERT [message]: Speak an update out loud.
        
        Choose one. Return ONLY the action keyword followed by the subject.
        Example: MARKET NVDA
        Example: ALERT System online and watching the markets.
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
