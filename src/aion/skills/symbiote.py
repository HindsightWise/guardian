import logging
import os
from pathlib import Path
from aion.core.mind import Mind

class SymbioteSkill:
    """
    The Always-On Proactive Skill. 
    Scans the environment for opportunities to be helpful without being asked.
    Inspired by Moltbot.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("SymbioteSkill")
        self.brain = Mind()
        self.root_path = Path(os.getcwd())
        
    def scan_for_tasks(self):
        """
        Scans User_Content for TODOs or questions in markdown files.
        """
        user_content_path = self.root_path / "User_Content"
        if not user_content_path.exists():
            return []
            
        tasks = []
        for md_file in user_content_path.glob("*.md"):
            content = md_file.read_text()
            if "TODO" in content or "?" in content:
                self.logger.info(f"💡 Found potential task in {md_file.name}")
                # Ask the brain if we should do something
                decision = self.brain.think(
                    content[:1000], 
                    f"In the file {md_file.name}, I found some potential tasks or questions. Should I proactively help? If yes, suggest an action like 'RESEARCH <topic>' or 'SUMMARIZE <file>'. If no, return 'IDLE'."
                )
                if decision != "IDLE":
                    tasks.append(decision)
        return tasks

    def check_system_health(self):
        """
        Proactively checks if everything is running smoothly.
        """
        # Example: check if Ollama is responsive
        if not self.brain.is_active():
            return "ALARM: Brain is offline! I need to restart my cognitive core."
        return "Everything is optimal. I am MASTERFUL."
