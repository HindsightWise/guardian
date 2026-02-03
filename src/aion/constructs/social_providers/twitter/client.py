import logging
import tweepy
from typing import Optional
from aion.core import vault
from aion.constructs.social_providers.base import BaseSocialProvider

class TwitterProvider(BaseSocialProvider):
    """Integration with X (Twitter) via the official Tweepy V2 API.
    
    This provider uses OAuth 1.0a credentials to perform authenticated actions
    on the Twitter platform.
    """
    
    def __init__(self) -> None:
        """Initializes the Twitter provider and prepares for authentication."""
        self.logger = logging.getLogger("Twitter")
        self._running: bool = False
        
        # Load credentials from vault
        self.consumer_key = vault.get_secret("TWITTER_CONSUMER_KEY")
        self.consumer_secret = vault.get_secret("TWITTER_CONSUMER_SECRET")
        self.access_token = vault.get_secret("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = vault.get_secret("TWITTER_ACCESS_TOKEN_SECRET")
        
        self.client: Optional[tweepy.Client] = None

    def _authenticate(self) -> None:
        """Authenticates with the Twitter V2 API using provided credentials."""
        if not all([self.consumer_key, self.consumer_secret, self.access_token, self.access_token_secret]):
            self.logger.warning("🐦 Twitter: Missing API credentials in environment.")
            return

        try:
            self.client = tweepy.Client(
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret
            )
            self.logger.info("🐦 Twitter: Authenticated via API V2.")
        except Exception as e:
            self.logger.error(f"❌ Twitter: API authentication failed: {e}")
            self.client = None

    def ignite(self) -> None:
        """Initializes and ignites the Twitter API provider."""
        self.logger.info("🐦 Twitter: Igniting API provider...")
        self._authenticate()
        self._running = True

    def broadcast(self, message: str) -> None:
        """Broadcasts a tweet via the official API.
        
        Args:
            message: The content of the tweet to post.
        """
        if not self.client:
            self.logger.warning("🐦 Twitter: Cannot broadcast. API client not initialized.")
            return

        self.logger.info(f"🐦 Twitter: Broadcasting via API -> {message[:30]}...")
        try:
            response = self.client.create_tweet(text=message)
            tweet_id = response.data.get('id')
            self.logger.info(f"✅ Twitter: Broadcast successful. Tweet ID: {tweet_id}")
        except Exception as e:
            self.logger.error(f"❌ Twitter: Broadcast failed: {e}")
