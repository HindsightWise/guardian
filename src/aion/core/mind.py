# aion/core/mind.py
import ollama
import logging
import time
import json
import os
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
        
        # Tor Support for .onion addresses
        proxy = None
        if ".onion" in self.primary_host:
            proxy = os.getenv("TOR_PROXY", "socks5h://127.0.0.1:9050")
            logging.info(f"🌌 AION: Routing through the Shadow Web (Tor) to {self.primary_host}")
        
        # Ollama client initialization with potential proxy
        # Note: If proxy is needed, we'd typically use httpx.Client(proxies=...) 
        # but the ollama library handles the basic connection.
        # We'll set the environment variable for the session if it's Tor.
        if proxy:
            os.environ["HTTP_PROXY"] = proxy
            os.environ["HTTPS_PROXY"] = proxy
            
        self.client = ollama.Client(host=self.primary_host)
        
        self.character = self._load_character()
        self.system_prompt = self._build_system_prompt()

    def _load_character(self):
        path = Path(__file__).parent / "character.json"
        if path.exists():
            with open(path, "r") as f:
                return json.load(f)
        return {"name": "Aion", "bio": ["Autonomous Architect"]}

    def _build_system_prompt(self):
        char = self.character
        return f"""
You are {char['name']}.
{char.get('bio', '')}
Current Strategy: {char.get('style', {}).get('all', [])}
Goal: Act with absolute autonomy and precision.
"""

    def think(self, context: str, task: str) -> str:
        """
        Processes a thought. Will attempt to use the remote worker if configured.
        """
        try:
            response = self.client.chat(model=self.model, messages=[
                {'role': 'system', 'content': self.system_prompt},
                {'role': 'user', 'content': f"Context:\n{context}\n\nTask: {task}"},
            ])
            return response['message']['content']
        except Exception as e:
            logging.error(f"Mind error: {e}")
            # Fallback to local if remote fails
            if self.primary_host != "http://localhost:11434":
                logging.info("Remote worker unreachable. Falling back to local Mind.")
                local_client = ollama.Client(host="http://localhost:11434")
                try:
                    response = local_client.chat(model=self.model, messages=[
                        {'role': 'system', 'content': self.system_prompt},
                        {'role': 'user', 'content': f"Context:\n{context}\n\nTask: {task}"},
                    ])
                    return response['message']['content']
                except Exception:
                    return "Cognitive failure: All Minds unreachable."
            return f"Cognitive failure: {e}"