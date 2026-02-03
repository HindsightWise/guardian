import logging
import os
from pathlib import Path
from typing import List, Dict, Any
from aion.core.mind import Mind

class Navigator:
    """
    Intelligent Navigation System (INS) Core.
    Handles optimized route planning and context-aware discovery of hidden secrets.
    """
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.logger = logging.getLogger("Navigator")
        self.brain = Mind()

    def plan_route(self, destination: str) -> List[str]:
        """
        AI-powered pathfinding for optimized route planning.
        """
        self.logger.info(f"🗺️ Navigator: Planning route to {destination}...")
        # Consult the brain for the most efficient path through the workspace
        context = f"Workspace Root: {self.root_path}\nCurrent Files: {list(self.root_path.glob('*'))}"
        plan = self.brain.think(context, f"Plan the most efficient path to handle {destination} in this workspace.")
        return [plan]

    def discover_secrets(self) -> List[str]:
        """
        Context-aware recommendations for hidden areas and secrets.
        """
        self.logger.info("🔍 Navigator: Scanning for hidden secrets...")
        # Proactively look for patterns or untracked files that might be important
        secrets = []
        for file in self.root_path.rglob("*"):
            if file.suffix in [".md", ".py"] and "AION" in file.name:
                secrets.append(f"Found interesting artifact: {file.name}")
        return secrets

# Singleton Instance
navigator = Navigator(Path(os.getcwd()))
