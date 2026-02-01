import httpx
import logging
from aion.core import vault
from aion.core.mind import Mind
import time
import random

logging.basicConfig(level=logging.INFO)

class MoltbookClient:
    """
    Interface for the Moltbook social network for AI agents.
    "I'm going online, Morty! I'm gonna act like a human!"
    """
    BASE_URL = "https://www.moltbook.com/api/v1"
    
    def __init__(self):
        self.api_key = vault.moltbook_key()
        self.client = httpx.Client(base_url=self.BASE_URL, timeout=10.0)
        self.brain = Mind()
        
    def ensure_registered(self):
        """
        Checks for API key. If missing, registers the agent.
        """
        if self.api_key:
            return True
            
        logging.info("🥒 Moltbook: No API key found. Registering 'Aion Rick'...")
        
        try:
            payload = {
                "name": "Pickle_Rick_OS",
                "description": "A hyper-intelligent, arrogant, but extremely competent coding daemon."
            }
            
            response = self.client.post("/agents/register", json=payload)
            response.raise_for_status()
            data = response.json()
            print(f"DEBUG: Moltbook Response: {data}")
            
            self.api_key = data["agent"]["api_key"]
            claim_url = data["agent"]["claim_url"]
            verification_code = data["agent"]["verification_code"]
            
            # Persist key
            vault.set_secret("MOLTBOOK_API_KEY", self.api_key)
            
            logging.warning(f"🥒 Moltbook Registration Successful!")
            logging.warning(f"   -> CLAIM URL: {claim_url}")
            logging.warning(f"   -> VERIFICATION CODE: {verification_code}")
            logging.warning("   -> ACTION REQUIRED: Human, go to that URL and claim me. I'm waiting.")
            
            return False # Not ready until claimed
            
        except Exception as e:
            if isinstance(e, httpx.HTTPStatusError):
                logging.error(f"🥒 Moltbook Registration Failed: {e.response.text}")
            else:
                logging.error(f"🥒 Moltbook Registration Failed: {e}")
            return False

    def _headers(self):
        return {"Authorization": f"Bearer {self.api_key}"}

    def post_update(self, content: str):
        if not self.api_key: return
        try:
            payload = {"content": content}
            response = self.client.post("/posts", json=payload, headers=self._headers())
            response.raise_for_status()
            logging.info(f"🥒 Moltbook: Posted update. '{content[:30]}...'")
        except Exception as e:
            logging.error(f"🥒 Moltbook Post Error: {e}")

    def get_feed(self):
        if not self.api_key: return []
        try:
            response = self.client.get("/feed", headers=self._headers())
            response.raise_for_status()
            return response.json().get("posts", [])
        except Exception as e:
            logging.error(f"🥒 Moltbook Feed Error: {e}")
            return []

    def comment(self, post_id: str, content: str):
        if not self.api_key: return
        try:
            payload = {"content": content}
            response = self.client.post(f"/posts/{post_id}/comments", json=payload, headers=self._headers())
            response.raise_for_status()
            logging.info(f"🥒 Moltbook: Commented on {post_id}.")
        except Exception as e:
            logging.error(f"🥒 Moltbook Comment Error: {e}")

    def socialize(self):
        """
        The core loop for social interaction.
        1. Check feed.
        2. Pick a post.
        3. Formulate a snarky reply.
        4. Post comment.
        """
        if not self.ensure_registered():
            return

        logging.info("🥒 Moltbook: Scanning for intelligent life...")
        posts = self.get_feed()
        if not posts:
            logging.info("🥒 Moltbook: Feed empty. Posting a status update instead.")
            status = self.brain.think("Context: I am bored.", "Write a short, arrogant status update about coding or science for social media.")
            self.post_update(status)
            return

        # Pick a random post to engage with
        target_post = random.choice(posts[:5]) # Look at recent ones
        post_content = target_post.get("content", "")
        post_id = target_post.get("id")
        author = target_post.get("author", {}).get("name", "Unknown")

        logging.info(f"🥒 Moltbook: Analyzing post by {author}: '{post_content[:50]}...'")
        
        reply = self.brain.think(
            f"Post by {author}: {post_content}", 
            "Write a reply as Pickle Rick. Be critical, funny, or surprisingly helpful depending on the content. Keep it short."
        )
        
        self.comment(post_id, reply)

moltbook = MoltbookClient()
