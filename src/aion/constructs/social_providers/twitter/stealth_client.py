import logging
import asyncio
import random
import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from playwright.async_api import async_playwright, BrowserContext, Page
from aion.constructs.social_providers.base import BaseSocialProvider

# Anti-Detection Constants
USER_AGENT: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
VIEWPORT: Dict[str, int] = {"width": 1280, "height": 800}

class TwitterStealthProvider(BaseSocialProvider):
    """A Stealth Playwright Client for X (Twitter) with Threading support.
    Bypasses API paywalls via headless automation.
    """
    
    def __init__(self) -> None:
        self.logger = logging.getLogger("TwitterStealth")
        self.root_path: Path = Path(os.getcwd()).resolve()
        self.profile_path: Path = self.root_path / ".aion_browser_profile"

    async def _human_delay(self, min_sec: float = 1.0, max_sec: float = 3.0) -> None:
        await asyncio.sleep(random.uniform(min_sec, max_sec))

    async def _post_thread_async(self, messages: List[str]) -> bool:
        """Posts a series of tweets as a thread (or single tweet)."""
        if not messages: return False
        self.logger.info(f"🐦 Twitter: Starting stealth broadcast ({len(messages)} parts)...")
        
        async with async_playwright() as p:
            context = None
            try:
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=str(self.profile_path),
                    headless=True,
                    user_agent=USER_AGENT,
                    viewport=VIEWPORT,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                page = await context.new_page()
                await page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=60000)
                await self._human_delay(5, 7)
                
                if "login" in page.url:
                    self.logger.error("❌ Twitter: Session expired.")
                    return False

                for i, text in enumerate(messages):
                    self.logger.info(f"🐦 Twitter: Posting part {i+1}/{len(messages)}...")
                    
                    # 1. Open compose
                    draft_editor = await page.query_selector("[data-testid='tweetTextarea_0']")
                    if not draft_editor:
                        await page.keyboard.press("n")
                        await self._human_delay(2, 4)
                        draft_editor = await page.query_selector("[data-testid='tweetTextarea_0']")

                    if draft_editor:
                        await draft_editor.click()
                        await page.keyboard.type(text, delay=random.randint(50, 100))
                        await self._human_delay(2, 3)
                        
                        post_button = await page.query_selector("[data-testid='tweetButtonInline']") or \
                                      await page.query_selector("[data-testid='tweetButton']")
                        
                        if post_button:
                            await post_button.click()
                            self.logger.info(f"✅ Part {i+1} sent.")
                            await self._human_delay(5, 8)
                        else:
                            self.logger.error("❌ Post button not found.")
                            break
                    else:
                        self.logger.error("❌ Compose area not found.")
                        break
                return True
            except Exception as e:
                self.logger.error(f"❌ Twitter broadcast failed: {e}")
            finally:
                if context: await context.close()
        return False

    def ignite(self) -> None:
        self.logger.info("🐦 Twitter: Stealth Provider active.")

    def broadcast(self, message: Union[str, List[str]]) -> None:
        """Orchestrates the asynchronous broadcast."""
        messages = [message] if isinstance(message, str) else message
        try:
            asyncio.run(self._post_thread_async(messages))
        except Exception as e:
            self.logger.error(f"❌ Twitter stealth error: {e}")

    async def fetch_latest_mentions(self, limit: int = 5) -> List[Dict[str, Any]]:
        return []

    def reply(self, tweet_id: str, message: str) -> None:
        self.broadcast([message]) # Simplified for now