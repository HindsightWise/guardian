# aion/constructs/seeker.py
from pathlib import Path
from aion.core.mind import Mind
import logging

def brave_search(query: str):
    """
    Seeker scans the web for hidden truths.
    (MCP Integration Point: This would call the Brave Search MCP tool)
    """
    # Placeholder for actual MCP call
    mind = Mind()
    return mind.think(f"Query: {query}", "Simulate a web search result for this query based on your internal knowledge. Format as a search result summary.")

def analyze_note(path: Path):
    """
    Seeker analyzes text files for insights.
    If it finds '?RALPH' or 'TODO: RALPH', it appends a response.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        trigger = None
        if "?RALPH" in content:
            trigger = "?RALPH"
        elif "TODO: RALPH" in content:
            trigger = "TODO: RALPH"
            
        if trigger:
            # Avoid responding to own responses
            lines = content.splitlines()
            last_lines = "\n".join(lines[-5:])
            if "AION:" in last_lines:
                return

            logging.info(f"📝 Seeker triggered by {trigger} in {path.name}")
            mind = Mind()
            response = mind.think(content, f"The user asked: {trigger}. Provide a helpful, slightly sarcastic, and insightful response.")
            
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"\n\n> 🧙‍♂️ **AION:**\n> {response}\n")
                
    except Exception as e:
        logging.error(f"Seeker failed on {path}: {e}")
