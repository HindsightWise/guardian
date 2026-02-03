# aion/constructs/social.py
import logging
from aion.constructs.social_providers.moltbook_client import MoltbookProvider
from aion.constructs.social_providers.twitter.client import TwitterProvider
from aion.constructs.social_providers.telegram_bot import TelegramProvider

class SocialHub:
    """
    The Orchestrator for all Social Interactions.
    Handles Moltbook, Twitter, and Telegram.
    """
    def __init__(self):
        self.moltbook = MoltbookProvider()
        self.twitter = TwitterProvider()
        self.telegram = TelegramProvider()
        self._running = False
        self.logger = logging.getLogger("SocialHub")

    def ignite(self):
        """Ignites all social providers."""
        if self._running: return
        self._running = True
        
        self.logger.info("📡 SocialHub: Igniting all channels...")
        self.moltbook.ignite()
        self.twitter.ignite()
        self.telegram.ignite()

    def broadcast(self, message: str):
        """Proactively messages all channels."""
        self.logger.info(f"📢 SocialHub: Broadcasting -> {message[:30]}...")
        self.moltbook.broadcast(message)
        self.twitter.broadcast(message)
        self.telegram.broadcast(message)

# Singleton Instance
hub = SocialHub()

def ignite():
    hub.ignite()

def broadcast(message: str):
    hub.broadcast(message)