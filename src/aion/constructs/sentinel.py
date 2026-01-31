# aion/constructs/sentinel.py
from pathlib import Path
from aion.core.mind import Mind
import logging
import re

def generate_migration(file_path: Path):
    """
    Sentinel monitors code changes and guards data integrity.
    Triggers a safety review if it detects data model changes.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Heuristic: Only trigger if it looks like a database model (SQLAlchemy/Pydantic)
        # Checks for: 'sqlalchemy' import, class inheriting from Base/Model, or mapped_column usage
        if (
            "sqlalchemy" in content 
            or re.search(r'class\s+\w+\((?:.*Base|.*Model)\):', content)
            or "mapped_column" in content
        ):
            logging.info(f"🐍 Sentinel detected DB model change in {file_path.name}")
            
            mind = Mind()
            review = mind.think(content, "Review this Python code for potential database schema changes or safety issues. Be brief and critical.")
            
            log_path = file_path.parent / "SAFETY_LOG.md"
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"\n## 🛡️ Sentinel Review: {file_path.name}\n{review}\n")
                
    except Exception as e:
        logging.error(f"Sentinel failed on {file_path}: {e}")
