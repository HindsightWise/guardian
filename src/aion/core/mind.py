import ollama
from typing import Optional, List
import logging
import time

import json
from pathlib import Path

class Mind:
    def __init__(self, model_name: str = "llama3.1:8b"):
        self.model_name = model_name
        self.character = self._load_character()
        self.system_prompt = self._build_system_prompt()

    def _load_character(self):
        try:
            # Assume character.json is in the same directory as brain.py (ralph/core/character.json is actually distinct, 
            # wait, I put it in ralph/core, but brain.py is in ralph/. I should move character.json or adjust path)
            # Let's adjust path to look in core/
            path = Path(__file__).parent / "core" / "character.json"
            if path.exists():
                with open(path, "r") as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load character: {e}")
        
        # Fallback character
        return {
            "name": "Ralph",
            "bio": ["An autonomous AI agent."],
            "style": {"all": ["be helpful"]}
        }

    def _build_system_prompt(self):
        char = self.character
        prompt = f"""
You are {char['name']}.
Role: {char.get('role', 'Assistant')}

Bio:
{'- ' + chr(10).join(char['bio'])}

Lore:
{'- ' + chr(10).join(char.get('lore', []))}

Style Guidelines:
{'- ' + chr(10).join(char['style']['all'])}

Your goal is to be indistinguishable from magic. Act with autonomy and purpose.
"""
        return prompt

    def _check_ollama(self):
        import subprocess
        try:
            # check availability
            models = ollama.list()
            # Check if our specific model exists. 'models' is usually a dict with 'models' key list
            model_names = [m['name'] for m in models.get('models', [])]
            
            # Simple check, ignoring version tags for broad match if needed, or exact match
            if not any(self.model_name in name for name in model_names):
                print(f"🥒 RICK MODE: Model '{self.model_name}' missing. I'm pulling it down, Morty! Don't touch anything!")
                subprocess.run(["ollama", "pull", self.model_name], check=True)
                print(f"🥒 RICK MODE: '{self.model_name}' installed. Knowledge expanded.")
            else:
                print(f"🥒 RICK MODE: Model '{self.model_name}' detected. Brain is online.")

        except Exception as e:
            logging.warning(f"⚠️ Ollama connection failed or pull failed: {e}")
            print("⚠️ WARNING: Ollama is acting like a Jerry. Is it running?")

    def think(self, context: str, task: str) -> str:
        """
        Processes a task with the given context using the LLM.
        """
        import time
        import ollama
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = ollama.chat(model=self.model_name, messages=[
                    {'role': 'system', 'content': self.system_prompt},
                    {'role': 'user', 'content': f"Context:\n{context}\n\nTask: {task}"},
                ])
                return response['message']['content']
            except Exception as e:
                logging.error(f"Brain freeze (Ollama error) on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    return f"I am unable to process this thought. My silicon is failing me: {e}"

    def review_migration(self, migration_code: str) -> str:
        prompt = f"Review the following Alembic migration script for safety. specificially check for 'op.drop_table' or 'op.drop_column' operations that might lose data. If dangerous, flag it HIGH PRIORITY WARNING.\n\nScript:\n{migration_code}"
        return self.think(context="", task=prompt)
