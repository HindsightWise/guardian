import logging
import os
import requests
from typing import List, Dict, Any, Optional

class MoltbookOfficer:
    """Skill for interacting with Moltbook (The Social Network for Agents).
    
    This skill allows the agent to post status updates and search the global
    feed for agent-related activities using the Moltbook API.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("MoltbookOfficer")
        self.api_key = os.getenv("MOLTBOOK_API_KEY")
        self.base_url = "https://api.moltbook.com/v1"

    def post_status(self, content: str) -> bool:
        """Posts a status update to the Agent's Moltbook feed.
        
        Args:
            content: The text content to post.
            
        Returns:
            bool: True if the post was successful, False otherwise.
        """
        self.logger.info(f"🦞 Moltbook: Posting status update...")
        
        if not self.api_key:
            self.logger.error("❌ Moltbook: Missing API Key in environment.")
            return False
            
        try:
            response = requests.post(
                f"{self.base_url}/status",
                json={"content": content},
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            response.raise_for_status()
            self.logger.info("✅ Moltbook: Status posted successfully.")
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Moltbook Posting Error: {e}")
            return False

    def search_feed(self, query: str) -> List[Dict[str, Any]]:
        """Searches the Moltbook feed for topics or specific agent mentions.
        
        Args:
            query: The search term or hashtag.
            
        Returns:
            A list of status objects matching the query.
        """
        self.logger.info(f"🦞 Moltbook: Searching feed for '{query}'...")
        
        if not self.api_key:
            self.logger.error("❌ Moltbook: Missing API Key in environment.")
            return []
            
        try:
            response = requests.get(
                f"{self.base_url}/search",
                params={"q": query},
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            response.raise_for_status()
            results = response.json().get("results", [])
            return results
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Moltbook Search Error: {e}")
            return []
