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
            
        # heuristic to detect model changes
        if re.search(r'class\s+\w+\(.*\):', content):
            logging.info(f"🐍 Sentinel detected potential model change in {file_path.name}")
            
            mind = Mind()
            review = mind.think(content, "Review this Python code for potential database schema changes or safety issues. Be brief and critical.")
            
            log_path = file_path.parent / "SAFETY_LOG.md"
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"\n## 🛡️ Sentinel Review: {file_path.name}\n{review}\n")
                
    except Exception as e:
        logging.error(f"Sentinel failed on {file_path}: {e}")
