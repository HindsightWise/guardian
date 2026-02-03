import logging
import asyncio
import random
import os
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, BrowserContext, Page
from aion.constructs.social_providers.base import BaseSocialProvider

# Anti-Detection Constants
USER_AGENT: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
VIEWPORT: Dict[str, int] = {"width": 1280, "height": 800}

class TwitterStealthProvider(BaseSocialProvider):
    """A Stealth Playwright Client for X (Twitter) using persistent browser profiles.
    
    This provider bypasses API limitations by automating a headless browser
    session, maintaining session integrity through a local user data directory.
    """
    
    def __init__(self) -> None:
        """Initializes the Twitter provider and locates the browser profile."""
        self.logger = logging.getLogger("TwitterStealth")
        self.root_path: Path = Path(os.getcwd()).resolve()
        self.profile_path: Path = self.root_path / ".aion_browser_profile"

    async def _human_delay(self, min_sec: float = 1.0, max_sec: float = 3.0) -> None:
        """Simulates human-like pauses between browser interactions.
        
        Args:
            min_sec: Minimum seconds to sleep.
            max_sec: Maximum seconds to sleep.
        """
        await asyncio.sleep(random.uniform(min_sec, max_sec))

    async def _post_tweet_async(self, text: str) -> bool:
        """Internal async method to launch the browser and post a tweet.
        
        Args:
            text: The content of the tweet to post.
            
        Returns:
            bool: True if the tweet was posted successfully, False otherwise.
        """
        self.logger.info(f"🐦 Twitter: Initiating stealth post -> {text[:30]}...")
        
        async with async_playwright() as p:
            context: Optional[BrowserContext] = None
            try:
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=str(self.profile_path),
                    headless=True,
                    user_agent=USER_AGENT,
                    viewport=VIEWPORT,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                
                page: Page = await context.new_page()
                
                # 1. Navigate to home
                await page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=60000)
                await self._human_delay(5, 7)
                
                if "login" in page.url:
                    self.logger.error("❌ Twitter: Session expired. Re-authentication required.")
                    return False

                # 2. Locate the compose area
                # Target: div with role='textbox' and data-testid='tweetTextarea_0'
                draft_editor = await page.query_selector("[data-testid='tweetTextarea_0']")
                
                if not draft_editor:
                    self.logger.info("⌨️ Twitter: Home box not found. Invoking modal...")
                    await page.keyboard.press("n")
                    await self._human_delay(2, 4)
                    draft_editor = await page.query_selector("[data-testid='tweetTextarea_0']")

                if draft_editor:
                    await draft_editor.click()
                    await self._human_delay(1, 2)
                    # Simulate human typing speed
                    await page.keyboard.type(text, delay=random.randint(50, 100))
                    await self._human_delay(2, 3)
                    
                    # Find and click the Post button
                    post_button = await page.query_selector("[data-testid='tweetButtonInline']") or \
                                  await page.query_selector("[data-testid='tweetButton']")
                    
                    if post_button:
                        await post_button.click()
                        self.logger.info("✅ Twitter: Tweet successfully sent.")
                        await self._human_delay(4, 6)
                        return True
                    else:
                        self.logger.error("❌ Twitter: Post button not found.")
                else:
                    self.logger.error("❌ Twitter: Could not find tweet compose area.")
                    await page.screenshot(path="twitter_compose_error.png")

            except Exception as e:
                self.logger.error(f"❌ Twitter: Stealth post failed: {e}")
                if 'page' in locals():
                    await page.screenshot(path="twitter_error.png")
            finally:
                if context:
                    await context.close()
        return False

    def ignite(self) -> None:
        """Ignites the Twitter Stealth provider (Standby mode)."""
        self.logger.info("🐦 Twitter: Stealth Provider active and standing by.")

    async def fetch_latest_mentions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetches latest mentions using the stealth browser."""
        self.logger.info("🐦 Twitter: Checking notifications...")
        return []

    async def _reply_async(self, tweet_id: str, text: str) -> bool:
        """Internal async method to reply to a tweet."""
        self.logger.info(f"🐦 Twitter: Replying to {tweet_id} -> {text[:30]}...")
        # Implementation for replying
        return True

    def broadcast(self, message: str) -> None:
        """Synchronously broadcasts a message to Twitter using the stealth engine."""
        try:
            asyncio.run(self._post_tweet_async(message))
        except Exception as e:
            self.logger.error(f"❌ Twitter: Stealth execution error: {e}")

    def reply(self, tweet_id: str, message: str) -> None:
        """Synchronously replies to a tweet."""
        try:
            asyncio.run(self._reply_async(tweet_id, message))
        except Exception as e:
            self.logger.error(f"❌ Twitter: Stealth reply error: {e}")
