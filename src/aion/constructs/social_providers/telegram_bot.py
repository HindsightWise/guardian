import os
import logging
import asyncio
import threading
from typing import Set, Optional, NoReturn, List, Union
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from aion.core.mind import Mind
from aion.constructs.social_providers.base import BaseSocialProvider

class TelegramProvider(BaseSocialProvider):
    """Integration with Telegram for real-time agent-to-human communication.
    
    This provider allows the agent to receive commands and broadcast updates
    via a Telegram bot.
    """
    
    def __init__(self) -> None:
        """Initializes the Telegram provider and its internal Mind."""
        self.token: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
        self.known_chats: Set[int] = set()
        self.brain = Mind()
        self.app: Optional[Application] = None
        self._running: bool = False
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.logger = logging.getLogger("TelegramProvider")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handles the /start command from a user.
        
        Args:
            update: The Telegram update object.
            context: The context for the current update.
        """
        if update.effective_chat:
            chat_id = update.effective_chat.id
            self.known_chats.add(chat_id)
            await context.bot.send_message(
                chat_id=chat_id, 
                text="🤖 Aion: Connection established. I am online and ready to assist."
            )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Processes incoming text messages from users.
        
        Args:
            update: The Telegram update object.
            context: The context for the current update.
        """
        if not update.effective_chat or not update.message or not update.message.text:
            return

        chat_id = update.effective_chat.id
        user_text = update.message.text
        self.known_chats.add(chat_id)
        
        self.logger.info(f"📩 Telegram from {chat_id}: {user_text}")
        
        # Use the Mind to formulate a contextual response
        response = self.brain.think(
            f"User (Telegram): {user_text}", 
            "Reply as Aion. Be professional, masterful, and respectful. Provide concise technical or creative value."
        )
        
        await context.bot.send_message(chat_id=chat_id, text=response)

    def _run(self) -> None:
        """Background loop to run the Telegram polling service."""
        if not self.token:
            self.logger.warning("⚠️ Telegram: No TELEGRAM_BOT_TOKEN found. Provider dormant.")
            return

        # Initialize a dedicated event loop for the polling thread
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.app = ApplicationBuilder().token(self.token).build()
        self.app.add_handler(CommandHandler('start', self.start))
        self.app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))
        
        self.logger.info("📡 Telegram: Connecting to global network...")
        self.app.run_polling(stop_signals=None)

    def ignite(self) -> None:
        """Starts the Telegram provider in a background thread."""
        if self._running:
            return
        self._running = True
        t = threading.Thread(target=self._run, daemon=True)
        t.start()

    def broadcast(self, message: Union[str, List[str]]) -> None:
        """Broadcasts a message or thread to all known chat IDs."""
        if not self.app or not self.known_chats or not self.loop:
            return
            
        final_message = "\n\n".join(message) if isinstance(message, list) else message

        for chat_id in self.known_chats:
            try:
                asyncio.run_coroutine_threadsafe(
                    self.app.bot.send_message(chat_id=chat_id, text=final_message),
                    self.loop
                )
            except Exception as e:
                self.logger.error(f"❌ Telegram Broadcast Error: {e}")
