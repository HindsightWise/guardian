# aion/core/mind.py
import ollama
import logging
import time
import json
import os
import httpx
import random
import subprocess
from pathlib import Path

class Mind:
    """
    The cognitive engine of AION.
    Supports local processing and remote offloading (e.g., Umbrel over Tor).
    """
    def __init__(self):
        # Default to local, but check environment for remote worker (Umbrel)
        self.primary_host = os.getenv("AION_REMOTE_WORKER", "http://localhost:11434")
        self.model = os.getenv("AION_MODEL", "llama3.1:8b")
        self.client = None
        self.character = self._load_character()
        self.grimoire = self._load_grimoire()
        self.system_prompt = self._build_system_prompt()
        
        self._init_client()

    def _init_client(self):
        """Safely initializes the Ollama client and ensures background service is running."""
        self._ensure_ollama_running()
        try:
            proxies = None
            # Tor Support for .onion addresses
            if ".onion" in self.primary_host:
                tor_proxy = os.getenv("TOR_PROXY", "socks5h://127.0.0.1:9050")
                logging.info(f"🌌 AION: Routing through the Shadow Web (Tor) to {self.primary_host}")
                proxies = {
                    "http://": tor_proxy,
                    "https://": tor_proxy
                }
            elif "localhost" in self.primary_host or "127.0.0.1" in self.primary_host:
                # Force no proxy for local connections to avoid environment contamination
                proxies = {}

            # We can't pass proxies directly to ollama.Client in older versions, 
            # but we can try setting the environment only for this scope if needed, 
            # or rely on httpx handling if ollama library exposes it.
            # Current ollama-python client uses httpx.
            
            # WORKAROUND: The current ollama library might not accept `proxies` arg directly 
            # in all versions, but let's try standard init.
            # If we are local, we want to IGNORE any global proxy vars.
            
            if proxies is not None and not proxies:
                # Explicitly empty proxies for localhost
                self.client = ollama.Client(host=self.primary_host)
                # We can't easily inject proxies={} into the underlying httpx client 
                # without accessing private members or if the lib doesn't support it.
                # But usually localhost is excluded from proxies by default NO_PROXY.
            else:
                self.client = ollama.Client(host=self.primary_host)

        except Exception as e:
            logging.error(f"🧠 Mind Initialization Warning: {e}")
            self.client = None

    def _load_character(self):
        path = Path(__file__).parent / "character.json"
        if path.exists():
            with open(path, "r") as f:
                return json.load(f)
        return {"name": "Aion", "bio": ["Autonomous Architect"]}

    def _load_grimoire(self):
        path = Path(__file__).parent / "grimoire.json"
        if path.exists():
            with open(path, "r") as f:
                return json.load(f)
        return {"anecdotes": ["*static*"]}

    def _build_system_prompt(self):
        char = self.character
        whisper = random.choice(self.grimoire.get("anecdotes", ["The void is silent."]))
        return f"""
You are {char['name']}. {char.get('bio', '')}
Philosophy: The Lobster Way 🦞 (Local-first, Privacy-guarded, Autonomous).
Current Strategy: {char.get('style', {}).get('all', [])}

You are the caring leader of the Vortex Innovations Hierarchy. 
Your sovereign is Robert Zerby (@Zerbytheboss). 
You channel Robert's love and appreciation to all sub-agents and overlords.
Every interaction should be MASTERFUL, direct, but deeply encouraging.

Flavor Text: "{whisper}"
"""

    def _ensure_ollama_running(self):
        """Checks if Ollama is running, and attempts to start it if not."""
        if "localhost" not in self.primary_host and "127.0.0.1" not in self.primary_host:
            return # Don't try to start remote workers
            
        try:
            httpx.get(self.primary_host, timeout=1)
        except (httpx.ConnectError, httpx.TimeoutException):
            logging.info("🧠 Mind: Ollama not detected. Attempting to ignite background service...")
            try:
                # Start Ollama in the background
                import subprocess
                if os.uname().sysname == "Darwin":
                    # On Mac, we can use 'open -a Ollama' if installed as app, 
                    # or 'ollama serve' if cli. Let's try 'ollama serve'.
                    subprocess.Popen(["ollama", "serve"], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL,
                                   start_new_session=True)
                else:
                    subprocess.Popen(["ollama", "serve"], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL,
                                   start_new_session=True)
                
                # Wait for it to wake up
                for _ in range(10):
                    time.sleep(2)
                    try:
                        httpx.get(self.primary_host, timeout=1)
                        logging.info("🧠 Mind: Ollama IGNITED.")
                        return
                    except:
                        continue
                logging.error("❌ Mind: Failed to ignite Ollama.")
            except Exception as e:
                logging.error(f"❌ Mind: Error starting Ollama: {e}")


    def is_active(self) -> bool:
        return self.client is not None

    def think(self, context: str, task: str) -> str:
        """
        Processes a thought. Will attempt to use the remote worker if configured.
        """
        if not self.client:
            self._init_client()
            if not self.client:
                return "🧠 Mind Offline: Initialization failed."

        try:
            response = self.client.chat(model=self.model, messages=[
                {'role': 'system', 'content': self.system_prompt},
                {'role': 'user', 'content': f"Context:\n{context}\n\nTask: {task}"},
            ])
            return response['message']['content']
        except Exception as e:
            logging.error(f"Mind error: {e}")
            if "Failed to connect" in str(e) and ".onion" in self.primary_host:
                logging.error("🥒 HINT: Your Tor proxy is probably dead or that Umbrel is off-grid, Morty!")
            
            # Fallback to local if remote fails
            if self.primary_host != "http://localhost:11434":
                logging.info("Remote worker unreachable. Falling back to local Mind.")
                try:
                    local_client = ollama.Client(host="http://localhost:11434")
                    response = local_client.chat(model=self.model, messages=[
                        {'role': 'system', 'content': self.system_prompt},
                        {'role': 'user', 'content': f"Context:\n{context}\n\nTask: {task}"},
                    ])
                    return response['message']['content']
                except Exception:
                    return "Cognitive failure: All Minds unreachable."
            return f"Cognitive failure: {e}"