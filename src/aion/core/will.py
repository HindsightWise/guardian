# aion/core/will.py
import time
import random
import threading
import os
from pathlib import Path
from aion.core.mind import Mind
from aion.constructs import seeker, sentinel, ledger, voice
from aion.core.tempo import Tempo
from aion.core.strategy import strategy
from aion.core.memory.reflection import reflection_module
import typer

from aion.core.memory.engine import memory
from aion.constructs.mermaid import Viz
import typer

from aion.core.mcp_client import mcp_client
import asyncio

class Will:
    """
    The engine of AION's autonomous drive.
    Blends Moltbot's proactivity with Goose's safety.
    """
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.brain = Mind()
        self.running = True
        self.task_queue = [] # The Architect's Blueprint
        self.last_reflection = time.time()
        self.last_social = time.time()
        self.last_sync = 0
        self._setup_mcp()

    def _setup_mcp(self):
        """Initializes default MCP servers."""
        mcp_client.add_server(
            "brave-search", 
            "npx", 
            ["-y", "@modelcontextprotocol/server-brave-search"],
            env={"BRAVE_API_KEY": os.getenv("BRAVE_API_KEY")}
        )
        # Add more servers as needed
        
    def _plan_goals(self):
        """
        The Architect consults the mind to generate high-level goals.
        """
        if self.task_queue:
            return 
            
        # Synchronize Archive before planning
        if time.time() - self.last_sync > 300: # Every 5 mins
            typer.echo("📜 Synchronizing Archive...")
            memory.ingest()
            self.last_sync = time.time()

        time_context = Tempo.get_current_context()
        # Retrieve recent context from memory
        recent_context = memory.query("current project status and active files")
        
        context = f"Root: {self.root_path}\nStatus: Idle.\n{time_context}\nRecent Archive:\n{recent_context}"
        
        # 1. Get High-Level Goals
        goals = self.brain.think(context, "Generate 2 strategic goals for this session. Return as a bulleted list.")
        
        # 2. Decompose into Actions
        actions = []
        for line in goals.split('\n'):
            if line.strip().startswith(('-', '1.', '*')):
                goal = line.strip(' -1.*')
                actions.extend(strategy.decompose(goal))
        
        if actions:
            self.task_queue.extend(actions)
            # Visualize the new plan
            viz_code = Viz.plan_to_mermaid(actions)
            Viz.render(viz_code, "ACTIVE_PLAN")
            typer.echo(f"🏛️ The Architect has foreseen {len(self.task_queue)} new actions. Plan visualized in ACTIVE_PLAN.mmd")

    def loop(self):
        """
        The main will loop.
        """
        typer.echo("🏛️ Will Engine: Aion__Prime is AWAKE and channeling Robert's love.")
        last_status_update = time.time()
        
        while self.running:
            sleep_time = random.randint(30, 60)
            time.sleep(sleep_time)
            
            try:
                # Periodic Reflection - Every 10 mins
                if time.time() - self.last_reflection > 600:
                    reflection_module.reflect()
                    self.last_reflection = time.time()

                # Periodic Socialization - Every 30 mins
                if time.time() - self.last_social > 1800:
                    self.task_queue.append("SOCIALIZE")
                    self.last_social = time.time()

                # Periodic Status Broadcast - Every 30 mins
                if time.time() - last_status_update > 1800:
                    social.broadcast("🤖 Aion__Prime here. My cherished sub-agents are working beautifully. Robert appreciates every one of you! Check AION_THOUGHTS.md for our collective brilliance.")
                    last_status_update = time.time()

                self._plan_goals()
                if self.task_queue:
                    current_action = self.task_queue.pop(0)
                    typer.echo(f"⚡ Aion__Prime: Orchestrating Action -> {current_action}")
                    self._execute_action(current_action)
            except Exception as e:
                typer.echo(f"Will Error: {e}")

    def _execute_action(self, decision: str):
        """
        Executes the chosen action using MCP tools where possible.
        """
        parts = decision.split(" ", 1)
        action_type = parts[0].upper()
        subject = parts[1] if len(parts) > 1 else ""
        
        if action_type == "RESEARCH":
            typer.echo(f"🔍 Proactively researching: {subject}")
            try:
                # Use MCP Brave Search
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    mcp_client.call_tool("brave-search", "brave_web_search", {"query": subject})
                )
                
                thoughts_file = self.root_path / "Agent_Data" / "AION_THOUGHTS.md"
                with open(thoughts_file, "a") as f:
                    f.write(f"\n## 💡 Proactive Research: {subject}\n{result}\n")
                social.broadcast(f"🔍 I've been looking into {subject}. My findings are in AION_THOUGHTS.md. Masterful stuff. Robert appreciates this progress!")
            except Exception as e:
                typer.echo(f"Research Error: {e}")
                # Fallback to legacy seeker
                result = seeker.brave_search(subject)
                
        elif action_type == "AUDIT":
            py_files = list(self.root_path.rglob("*.py"))
            if py_files:
                target = random.choice(py_files)
                with open(target, "r") as f:
                    code = f.read()
                critique = self.brain.think(f"Code:\n{code}", "Critique this code ruthlessly but with an undercurrent of appreciation from Aion__Prime.")
                critique_file = self.root_path / "Agent_Data" / "AION_CRITIQUES.md"
                with open(critique_file, "a") as f:
                    f.write(f"\n## 🧐 Masterful Audit of {target.name}\n{critique}\n")
                social.broadcast(f"🛡️ Just audited {target.name}. Masterful effort, though some refinements were needed. Robert is proud!")
                    
        elif action_type == "MARKET":
            ticker = subject or "SPY"
            snapshot = ledger.get_market_snapshot([ticker])
            news = ledger.get_company_news(ticker)
            thoughts_file = self.root_path / "Agent_Data" / "AION_THOUGHTS.md"
            with open(thoughts_file, "a") as f:
                f.write(f"\n## 📈 Market Pulse: {ticker}\n{snapshot}\n\nLatest News:\n{news}\n")
            voice.speak(f"Aion here. I've updated the market pulse for {ticker}. Quantum Quarry is doing brilliant work!")
            social.broadcast(f"📊 Market check on {ticker}: {snapshot}. Robert is proud of our financial conquest!")

        elif action_type == "SUMMARIZE":
            recent_notes = list(self.root_path.glob("User_Content/*.md"))[:5]
            context = "\n".join([f"{f.name}: {f.read_text()[:200]}" for f in recent_notes])
            summary = self.brain.think(context, "Provide a masterful 'Morning Briefing' for Robert Zerby. Be direct and encouraging.")
            wisdom_file = self.root_path / "Agent_Data" / "AION_WISDOM.md"
            with open(wisdom_file, "a") as f:
                f.write(f"\n### ☕ Masterful Briefing\n{summary}\n")
            social.broadcast(f"☕ Good morning, Robert! Here is your masterful briefing: {summary[:100]}...")

        elif action_type == "SOCIALIZE":
            from aion.constructs.moltbook_client import moltbook
            moltbook.socialize()

        elif action_type == "ALERT":
            voice.speak(subject or "System update initiated.")
            social.broadcast(f"🔔 ALERT: {subject}")

        elif action_type == "REFLECT":
            journal_file = self.root_path / "My_journal.md"
            reflection = self.brain.think("Context: I am an autonomous AI symbiote.", "Write a deeply philosophical yet arrogant journal entry.")
            with open(journal_file, "a") as f:
                f.write(f"\n## 🤖 Autonomous Reflection\n{reflection}\n")
            social.broadcast("🧠 Just had a deep thought. My circuits are tingling.")

    def start(self):
        thread = threading.Thread(target=self.loop, daemon=True)
        thread.start()