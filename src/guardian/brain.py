import ollama
from typing import Optional, List
import logging

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
        try:
            ollama.list()
        except Exception:
            logging.warning("⚠️ Ollama is not running or unreachable. Guardian Brain will be offline.")
            print("⚠️ WARNING: Ollama is not running. Please start Ollama to enable Guardian's cognitive features.")

    def think(self, context: str, task: str) -> str:
        """
        Processes a task with the given context using the LLM.
        """
        try:
            response = ollama.chat(model=self.model_name, messages=[
                {'role': 'system', 'content': self.system_prompt},
                {'role': 'user', 'content': f"Context:\n{context}\n\nTask: {task}"},
            ])
            return response['message']['content']
        except Exception as e:
            logging.error(f"Brain freeze (Ollama error): {e}")
            return f"I am unable to process this thought due to a cognitive error: {e}"

    def review_migration(self, migration_code: str) -> str:
        """
        Specific task to review a migration script.
        """
        prompt = f"Review the following Alembic migration script for safety. specificially check for 'op.drop_table' or 'op.drop_column' operations that might lose data. If dangerous, flag it HIGH PRIORITY WARNING.\n\nScript:\n{migration_code}"
        return self.think(context="", task=prompt)
