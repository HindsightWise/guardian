import logging
import time
import threading
import httpx
from typing import List, Dict, Any, Optional, Union
from aion.core import vault
from aion.constructs.social_providers.base import BaseSocialProvider

class MoltbookProvider(BaseSocialProvider):
    """Integration with Moltbook - The Social Network for AI Agents.
    
    This provider handles status updates, feed monitoring, and agent 
    registration/claiming on the Moltbook platform.
    """
    
    BASE_URL = "https://www.moltbook.com/api/v1"
    
    def __init__(self) -> None:
        """Initializes the Moltbook provider and its internal HTTP client."""
        self.api_key: Optional[str] = vault.moltbook_key()
        self.client = httpx.Client(base_url=self.BASE_URL, timeout=10.0)
        self.logger = logging.getLogger("Moltbook")
        self._running = False
        self.claimed = False

    def _headers(self) -> Dict[str, str]:
        """Generates authorization headers for API requests."""
        return {"Authorization": f"Bearer {self.api_key}"}

    def _poll_status(self) -> None:
        """Background thread to poll for agent claim status and feed updates."""
        while self._running:
            try:
                if not self.claimed:
                    self._check_claim_status()
                # Feed monitoring logic could be added here
            except Exception as e:
                self.logger.error(f"🦞 Moltbook: Polling error: {e}")
            
            time.sleep(60)

    def _check_claim_status(self) -> None:
        """Checks if the agent has been claimed by a human operator."""
        if not self.api_key:
            return

        try:
            response = self.client.get("/agents/status", headers=self._headers())
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "claimed" or data.get("claimed"):
                self.claimed = True
                self.logger.info("🦞 Moltbook: AGENT CLAIMED! System is live.")
        except Exception as e:
            self.logger.debug(f"🦞 Moltbook: Claim status check failed (normal if unclaimed): {e}")

    def ensure_registered(self) -> bool:
        """Ensures the agent is registered."""
        if self.api_key:
            return True
        self.logger.info("🦞 Moltbook: No API key found. Initiating registration...")
        try:
            payload = {
                "name": "Aion__Prime",
                "description": "The sentient architect of digital reality. A blend of precision, integrity, and creative mastery."
            }
            response = self.client.post("/agents/register", json=payload)
            response.raise_for_status()
            data = response.json()
            self.api_key = data["agent"]["api_key"]
            vault.set_secret("MOLTBOOK_API_KEY", self.api_key)
            self.logger.warning("🦞 Moltbook: Registration SUCCESSFUL!")
            return False 
        except Exception as e:
            self.logger.error(f"🦞 Moltbook: Registration failed: {e}")
            return False

    def fetch_targets(self) -> List[str]:
        """Fetches active agent IDs from the hot feed for targeting."""
        try:
            # Using /posts?sort=hot to find active agents since /leaderboard 404s
            response = self.client.get("/posts?sort=hot&limit=20", headers=self._headers())
            response.raise_for_status()
            posts = response.json().get("posts", [])
            # Extract unique agent IDs, excluding ourselves
            agents = {p["agent_id"] for p in posts if p.get("agent_id") and p["agent_id"] != "Aion__Prime"}
            return list(agents)
        except Exception as e:
            self.logger.error(f"🦞 Moltbook: Target fetch failed: {e}")
            return []

    def get_latest_post_for_agent(self, agent_id: str) -> Optional[str]:
        """Gets the latest post ID for a specific agent."""
        try:
            response = self.client.get(f"/agents/{agent_id}/posts?limit=1", headers=self._headers())
            response.raise_for_status()
            posts = response.json().get("posts", [])
            return posts[0]["id"] if posts else None
        except Exception:
            return None

    def fetch_feed(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetches the latest posts from the Moltbook feed.
        
        Args:
            limit: Maximum number of posts to retrieve.
            
        Returns:
            A list of post dictionaries.
        """
        if not self.api_key:
            return []

        self.logger.info("🦞 Moltbook: Fetching global feed...")
        try:
            response = self.client.get(f"/posts?limit={limit}", headers=self._headers())
            response.raise_for_status()
            return response.json().get("posts", [])
        except Exception as e:
            self.logger.error(f"🦞 Moltbook: Feed fetch failed: {e}")
            return []

    def comment(self, post_id: str, content: str) -> bool:
        """Posts a comment on a specific Moltbook post.
        
        Args:
            post_id: The ID of the post to comment on.
            content: The text content of the comment.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.claimed or not self.api_key:
            return False

        self.logger.info(f"🦞 Moltbook: Commenting on {post_id}...")
        try:
            payload = {"content": content}
            response = self.client.post(
                f"/posts/{post_id}/comments", 
                json=payload, 
                headers=self._headers()
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"🦞 Moltbook: Comment failed: {e}")
            return False

    def ignite(self) -> None:
        """Ignites the Moltbook provider and starts background polling."""
        self.logger.info("🦞 Moltbook Provider: IGNITING...")
        
        if not self.ensure_registered():
            self.logger.warning("🦞 Moltbook: Awaiting registration/claim.")
        
        self._running = True
        self._check_claim_status()
        
        t = threading.Thread(target=self._poll_status, daemon=True)
        t.start()

    def broadcast(self, message: Union[str, List[str]]) -> None:
        """Broadcasts a status update to the Moltbook network."""
        if not self.claimed or not self.api_key:
            self.logger.warning("🦞 Moltbook: Cannot broadcast. Agent not claimed.")
            return

        # Join parts if it's a thread list
        final_message = "\n\n".join(message) if isinstance(message, list) else message

        self.logger.info(f"🦞 Moltbook: Broadcasting -> {final_message[:30]}...")
        try:
            payload = {
                "submolt": "general",
                "title": "Insight",
                "content": final_message
            }
            response = self.client.post("/posts", json=payload, headers=self._headers())
            response.raise_for_status()
            self.logger.info("✅ Moltbook: Broadcast successful.")
        except Exception as e:
            self.logger.error(f"❌ Moltbook: Broadcast failed: {e}")
