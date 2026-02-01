from pathlib import Path
import os

class PathGuard:
    """
    Enforces filesystem boundaries.
    "You don't go outside the sandbox, Morty. Outside is where the bugs live."
    """
    
    def __init__(self, root_dir: Path):
        self.root = root_dir.resolve()

    def validate_path(self, target_path: str | Path) -> Path:
        """
        Validates that target_path is within the root directory.
        Returns the resolved absolute path if valid.
        Throws SecurityException if invalid.
        """
        target = (self.root / target_path).resolve()
        
        # Check if target is relative to root (is_relative_to is Python 3.9+)
        try:
            target.relative_to(self.root)
        except ValueError:
            raise PermissionError(f"🥒 PATH VIOLATION: '{target}' tries to escape the sandbox ({self.root}). Nice try, Jerry.")
            
        return target
