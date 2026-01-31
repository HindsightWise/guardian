# aion/core/memory/reflection.py
import os
from pathlib import Path
from aion.core.mind import Mind

class Reflection:
    """
    Distills experiences into wisdom.
    """
    def __init__(self):
        self.root_path = Path(os.getcwd())
        self.brain = Mind()

    def reflect(self):
        thoughts_file = self.root_path / "AION_THOUGHTS.md"
        if not thoughts_file.exists(): return

        with open(thoughts_file, "r") as f:
            data = f.read()[-5000:]

        insight = self.brain.think(data, "Extract the core tactical insight from these logs.")
        wisdom_file = self.root_path / "AION_WISDOM.md"
        with open(wisdom_file, "a") as f:
            f.write(f"\n### {insight[:30]}\n{insight}\n")

reflection_module = Reflection()