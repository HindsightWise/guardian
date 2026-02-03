import fnmatch
import logging
from typing import Callable, List, Dict, Any, Awaitable
from pathlib import Path

HandlerFunc = Callable[[Any], Awaitable[None]]

class SkillsRegistry:
    def __init__(self):
        self._registry: List[Dict[str, Any]] = []

    def register(self, pattern: str, handler: HandlerFunc, name: str = "Unknown"):
        """Registers a handler for a specific file pattern."""
        self._registry.append({
            "pattern": pattern,
            "handler": handler,
            "name": name
        })
        logging.info(f"✅ Skill Registered: {name} ({pattern})")

    async def dispatch(self, file_path: str, event_type: str = "modified"):
        """Dispatches event to all matching handlers."""
        path_obj = Path(file_path)
        name = path_obj.name
        
        matched = False
        for skill in self._registry:
            if fnmatch.fnmatch(name, skill["pattern"]):
                try:
                    logging.info(f"⚡ Skill Triggered: {skill['name']} on {name}")
                    await skill["handler"](path_obj)
                    matched = True
                except Exception as e:
                    logging.error(f"❌ Skill Error ({skill['name']}): {e}")
        
        return matched