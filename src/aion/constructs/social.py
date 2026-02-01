# aion/constructs/social.py
import os
import logging
import asyncio
import threading
from typing import List, Optional
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from aion.core.mind import Mind

class SocialHub:
    """
    The Social Interface for Aion (Ralph).
    Handles Telegram (Dr_Clawed_Bot) and tracks WhatsApp contacts.
    "I'm proactive, Morty! I'm reaching out!"
    """
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.whatsapp_contact = "17143967670" # Hardcoded user contact
        self.known_chats = set()
        self.brain = Mind()
        self.app = None
        self._running = False

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        self.known_chats.add(chat_id)
        await context.bot.send_message(chat_id=chat_id, text="🥒 Wubba Lubba Dub Dub! Aion is online. I'm listening.")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user_text = update.message.text
        self.known_chats.add(chat_id)
        
        logging.info(f"📩 Telegram from {chat_id}: {user_text}")
        
        # Consult the Brain
        response = self.brain.think(f"User (Telegram): {user_text}", "Reply as Pickle Rick. Be helpful but snarky.")
        
        await context.bot.send_message(chat_id=chat_id, text=response)

    def run_telegram_daemon(self):
        if not self.token:
            logging.warning("⚠️ No TELEGRAM_BOT_TOKEN found. SocialHub dormant.")
            return

        self.app = ApplicationBuilder().token(self.token).build()
        
        start_handler = CommandHandler('start', self.start)
        echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message)
        
        self.app.add_handler(start_handler)
        self.app.add_handler(echo_handler)
        
        logging.info("📡 SocialHub: Connecting to Telegram (Dr_Clawed_Bot)...")
        self.app.run_polling()

    def ignite(self):
        """Starts the social daemon in a background thread."""
        if self._running: return
        self._running = True
        t = threading.Thread(target=self.run_telegram_daemon, daemon=True)
        t.start()

    def broadcast(self, message: str):
        """Proactively messages all known users."""
        if not self.app: return
        
        # Note: This requires the async loop, simpler to log for this CLI proof-of-concept
        # In a full daemon, we'd schedule this on the event loop.
        logging.info(f"📢 BROADCAST ATTEMPT: {message}")
        # Placeholder: Real proactive sending requires persistent chat_id storage
        # and async injection.

social = SocialHub()
