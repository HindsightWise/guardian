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
    The Social Interface for Aion.
    Handles Telegram (Dr_Clawed_Bot) and tracks WhatsApp contacts.
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
        await context.bot.send_message(chat_id=chat_id, text="🥒 I'M AION RICK! I turned myself into a background daemon, Morty! I'm ready to fix your slop.")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user_text = update.message.text
        self.known_chats.add(chat_id)
        
        logging.info(f"📩 Telegram from {chat_id}: {user_text}")
        
        # Consult the Brain - Force Pickle Rick Persona
        response = self.brain.think(f"User (Telegram): {user_text}", "Reply as Pickle Rick. Be hyper-intelligent, arrogant, but helpful. No Jerry-work.")
        
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
        # stop_signals=None prevents the library from trying to handle signals in a thread
        self.app.run_polling(stop_signals=None)

    def ignite(self):
        """Starts the social daemon in a background thread."""
        if self._running: return
        self._running = True
        t = threading.Thread(target=self.run_telegram_daemon, daemon=True)
        t.start()

    def broadcast(self, message: str):
        """Proactively messages all known users."""
        if not self.app or not self.known_chats:
            logging.info(f"📢 BROADCAST (Internal): {message}")
            return
        
        logging.info(f"📢 BROADCAST (Sending): {message}")
        
        # Schedule the async send_message call on the running event loop
        for chat_id in self.known_chats:
            asyncio.run_coroutine_threadsafe(
                self.app.bot.send_message(chat_id=chat_id, text=message),
                self.app.loop
            )

# Singleton Instance
hub = SocialHub()

# Module-level convenience functions to match other constructs
def ignite():
    hub.ignite()

def broadcast(message: str):
    hub.broadcast(message)
