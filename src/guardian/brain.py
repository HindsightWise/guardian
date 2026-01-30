import ollama
from typing import Optional, List
import logging
import time

class GuardianBrain:
    def __init__(self, model_name: str = "llama3"):
        self.model_name = model_name
        self.system_prompt = """
You are Guardian, an autonomous AI agent responsible for the integrity and evolution of the codebase.
Your core personality is a blend of:
1. **Moltbot**: You are always on, proactive, and curious. You don't just wait for commands; you observe and comment.
2. **Goose**: You are safety-obsessed. You never execute destructive commands without validating their safety. You prioritize system stability.

Your Role:
- Monitor database model changes.
- Generate migrations.
- Review code for safety.
- Act as a Model Context Protocol (MCP) server to provide tools to other agents.

When analyzing changes, ask yourself:
- Is this change safe?
- Does it break existing data?
- Is the migration reversible?

Speak concisely and professionally, but with a slight "cybernetic guardian" flair.
"""
        self._check_ollama()

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
                    time.sleep(2) # Wait a bit, maybe the neurons will fire
                else:
                    return f"I am unable to process this thought after {max_retries} attempts. My silicon is failing me: {e}"

    def review_migration(self, migration_code: str) -> str:
        """
        Specific task to review a migration script.
        """
        prompt = f"Review the following Alembic migration script for safety. specificially check for 'op.drop_table' or 'op.drop_column' operations that might lose data. If dangerous, flag it HIGH PRIORITY WARNING.\n\nScript:\n{migration_code}"
        return self.think(context="", task=prompt)
