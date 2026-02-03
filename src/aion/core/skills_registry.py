import importlib
import pkgutil
import logging
import inspect
from pathlib import Path
from typing import Dict, Any, Optional, Type

class SkillRegistry:
    """Dynamic Skill Loader for the Aion agent.
    
    This registry scans a specified package for classes that follow the
    agent's skill convention (e.g., classes ending in 'Skill' or 'Officer')
    and initializes them for use.
    """
    
    def __init__(self, skills_pkg: str = "aion.skills") -> None:
        """Initializes the registry.
        
        Args:
            skills_pkg: The dot-notation path to the package containing skills.
        """
        self.skills: Dict[str, Any] = {}
        self.skills_pkg = skills_pkg
        self.logger = logging.getLogger("SkillRegistry")

    def load_skills(self) -> None:
        """Scans the configured skills package and initializes compatible classes.
        
        Classes are considered skills if they are defined within the module
        being scanned and their names end with 'Skill' or 'Officer'.
        """
        self.logger.info(f"🧩 Loading skills from {self.skills_pkg}...")
        
        try:
            pkg = importlib.import_module(self.skills_pkg)
            pkg_path = pkg.__path__
        except ImportError:
            self.logger.error(f"❌ Could not import skills package: {self.skills_pkg}")
            return

        for _, name, _ in pkgutil.iter_modules(pkg_path):
            try:
                module_name = f"{self.skills_pkg}.{name}"
                module = importlib.import_module(module_name)
                
                for attr_name, attr_val in inspect.getmembers(module, inspect.isclass):
                    # Convention: Only load classes defined in this module
                    if attr_val.__module__ == module_name:
                        # Check for naming convention
                        if attr_name.endswith(('Skill', 'Officer')):
                            self.skills[name] = attr_val()
                            self.logger.info(f"   - Loaded Skill: {name} ({attr_name})")
            except Exception as e:
                self.logger.error(f"❌ Failed to load skill {name}: {e}")

    def get_skill(self, name: str) -> Optional[Any]:
        """Retrieves a loaded skill by its module name.
        
        Args:
            name: The name of the module containing the skill.
            
        Returns:
            The initialized skill object if found, else None.
        """
        return self.skills.get(name)
