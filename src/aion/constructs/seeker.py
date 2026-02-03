# aion/constructs/seeker.py
import logging
import os
import asyncio
from pathlib import Path
from typing import Optional
from aion.core.mind import Mind
from aion.core.memory.engine import memory
from aion.core.mcp_client import mcp_client

async def brave_search(query: str) -> str:
    """Searches the Web using the Brave Search API via MCP.
    
    Args:
        query: The search query.
        
    Returns:
        A summary string of the search results.
    """
    logging.info(f"🌐 Seeker: Searching the Web for '{query}' (via MCP)...")
    
    try:
        # Use the MCP Client to call the brave-search server
        result = await mcp_client.call_tool(
            server_name="brave-search",
            tool_name="brave_web_search", 
            arguments={"query": query, "count": 3}
        )
        
        # The result from brave-search MCP is likely a list of content or a string.
        # We need to format it for the user.
        # Assuming result is a string (JSON) or a list of TextContent
        # For now, let's just convert to string
        return str(result)
        
    except Exception as e:
        logging.error(f"❌ Seeker: Web search failed: {e}")
        return f"Error: The internet is broken or I'm being throttled. {e}"

async def process_todo(path: Path) -> None:
    """
    Handles TODO.md specifically.
    If it finds 'TODO: BREAKDOWN', it asks the Mind to break it down.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        if "TODO: BREAKDOWN" in content:
            # Check if we already did it to avoid loops
            lines = content.splitlines()
            if any("AION BREAKDOWN" in l for l in lines[-10:]):
                return

            logging.info(f"📝 Seeker: Breaking down tasks in {path.name}")
            mind = Mind()
            response = mind.think(content, "The user wants a breakdown of these tasks. specific, atomic, and actionable subtasks.")
            
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"\n\n> 🥒 **AION BREAKDOWN:**\n{response}\n")

    except Exception as e:
        logging.error(f"❌ Seeker failed on TODO: {e}")

async def analyze_note(path: Path) -> None:
    """
    Seeker analyzes text files for insights.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        trigger = None
        query = None
        
        if "?RALPH" in content:
            trigger = "?RALPH"
        elif "TODO: RALPH" in content:
            trigger = "TODO: RALPH"
        elif "?SEARCH" in content:
            trigger = "?SEARCH"
            # Extract query: "?SEARCH <query>"
            # Find the line with ?SEARCH
            for line in content.splitlines():
                if "?SEARCH" in line:
                    parts = line.split("?SEARCH", 1)
                    if len(parts) > 1:
                        query = parts[1].strip()
                    break
            
        if trigger:
            # Avoid responding to own responses
            lines = content.splitlines()
            last_lines = "\n".join(lines[-5:])
            if "AION:" in last_lines or "Web Search Results" in last_lines:
                return

            logging.info(f"📝 Seeker triggered by {trigger} in {path.name}")
            
            response = ""
            if trigger == "?SEARCH" and query:
                response = await brave_search(query)
            else:
                mind = Mind()
                response = mind.think(content, f"The user asked: {trigger}. Provide a helpful, slightly sarcastic, and insightful response.")
                response = f"> 🧙‍♂️ **AION:**\n> {response}"
            
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"\n\n{response}\n")
                
    except Exception as e:
        logging.error(f"Seeker failed on {path}: {e}")