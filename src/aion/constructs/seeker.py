# aion/constructs/seeker.py
import logging
import os
import httpx
from pathlib import Path
from typing import Optional
from aion.core.mind import Mind
from aion.core.memory.engine import memory

def brave_search(query: str) -> str:
    """Searches the Web using the Brave Search API.
    
    Args:
        query: The search query.
        
    Returns:
        A summary string of the search results.
    """
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        logging.error("❌ Seeker: BRAVE_API_KEY is missing. I'm a seeker, Morty, not a psychic!")
        return "Error: Missing BRAVE_API_KEY. Fix it, Jerry."

    logging.info(f"🌐 Seeker: Searching the Web for '{query}'...")
    
    try:
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": api_key
        }
        params = {"q": query, "count": 3}
        
        response = httpx.get("https://api.search.brave.com/res/v1/web/search", headers=headers, params=params, timeout=10.0)
        response.raise_for_status()
        
        data = response.json()
        results = data.get("web", {}).get("results", [])
        
        if not results:
            return "Seeker: The web is silent. Maybe it's hiding from me."
            
        summary = "\n".join([f"- {r['title']}: {r['description']}" for r in results])
        return f"Web Search Results for '{query}':\n{summary}"
        
    except Exception as e:
        logging.error(f"❌ Seeker: Web search failed: {e}")
        return f"Error: The internet is broken or I'm being throttled. {e}"

def analyze_note(path: Path) -> None:
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
