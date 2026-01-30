# ralph/core/memory/reflection.py
import os
import json
import logging
from pathlib import Path
from ralph.brain import RalphBrain
from ralph.core.memory.engine import memory as memory_engine

class ReflectionModule:
    """
    The 'Sleep' cycle of Ralph.
    It periodically reviews recent thoughts and journals to extract
    high-level insights and update the long-term memory.
    """
    def __init__(self):
        self.root_path = Path(os.getcwd())
        self.brain = RalphBrain()
        self.thoughts_file = self.root_path / "RALPH_THOUGHTS.md"
        self.journal_file = self.root_path / "My_journal.md"

    def reflect(self):
        """
        Processes the raw data stream into synthesized wisdom.
        """
        logging.info("🔮 Ralph is entering a state of reflection...")
        
        # 1. Read recent data
        data = ""
        if self.thoughts_file.exists():
            with open(self.thoughts_file, "r") as f:
                data += f"\n--- RECENT THOUGHTS ---\n{f.read()[-5000:]}" # Last 5k chars
        if self.journal_file.exists():
            with open(self.journal_file, "r") as f:
                data += f"\n--- RECENT JOURNAL ---\n{f.read()[-5000:]}"

        if not data.strip():
            return

        # 2. Extract Insights
        context = f"System Context: Reflecting on recent experiences.\n{data}"
        insight = self.brain.think(context, "Extract 3-5 'Gems of Wisdom' or strategic shifts based on these logs. Be profound and concise.")
        
        # 3. Store in Long-Term Memory (Vector)
        # In a real implementation, we would insert a new Document into LlamaIndex
        # For now, we'll append to a WISDOM file and re-index next time
        wisdom_file = self.root_path / "RALPH_WISDOM.md"
        with open(wisdom_file, "a") as f:
            f.write(f"\n## 🌌 Insight: {insight[:50]}...\n{insight}\n")
            
        logging.info("✨ Reflection complete. Wisdom distilled.")

# Singleton
reflection_module = ReflectionModule()
