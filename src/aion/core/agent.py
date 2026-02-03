import logging
from typing import Optional

from aion.core.mind import Mind
from aion.constructs import social
from aion.core.skills_registry import SkillRegistry
from aion.core.will import Will
from pathlib import Path
import os

class AionAgent:
    """The Unified Agent Entity: The core persona of AION__PRIME.
    Blends Moltbot's proactivity with Goose's safety.
    """
    
    def __init__(self, root_path: Optional[Path] = None):
        """Initializes the agent with its primary subsystems."""
        self.root_path = root_path or Path(os.getcwd())
        self.logger = logging.getLogger("AionAgent")
        self.mind = Mind()
        self.skills = SkillRegistry()
        self.social = social.hub
        self.will = Will(self.root_path)
        
    def wake_up(self) -> None:
        """Initializes and activates all agent subsystems."""
        self.logger.info("🤖 Aion__Prime: Waking up...")
        
        # Load Skills
        self.skills.load_skills()
        
        # Ignite Social
        self.social.ignite()
        
        # Start the Will loop in background
        self.will.start()
        
        self.logger.info("🤖 Aion__Prime: ONLINE and MASTERFUL.")
        self.social.broadcast("🤖 Aion__Prime is ONLINE. I am watching, learning, and optimizing. Masterful work awaits.")

    def think(self, observation: str) -> str:
        """Processes an observation through the agent's internal Mind.
        
        Args:
            observation: The raw input or event detected by the agent.
            
        Returns:
            A string containing the agent's reasoned response or decision.
        """
        return self.mind.think(observation, "Process this observation and decide on a strategy.")

    def act(self, action: str) -> None:
        """Executes a determined action.
        
        Args:
            action: The action string or command to be executed.
            
        Note:
            Current implementation is a placeholder for the future action
            execution loop.
        """
        self.logger.info(f"🤖 Aion Agent: Activating action -> {action}")
        # TODO: Implement actual action dispatch logic
        pass

# Global Singleton for system-wide access
agent = AionAgent()
