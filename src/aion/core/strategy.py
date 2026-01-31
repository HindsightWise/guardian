# aion/core/strategy.py
import json
import logging
import re
from typing import List, Dict
from aion.core.mind import Mind

class Strategy:
    """
    Decomposes high-level goals into tactical actions.
    """
    def __init__(self):
        self.brain = Mind()

    def decompose(self, goal: str) -> List[str]:
        context = f"Strategic Goal: {goal}"
        prompt = """
        Decompose this goal into 2-3 Actions: 
        - RESEARCH [topic]
        - MARKET [ticker]
        - AUDIT [filename]
        - ALERT [message]
        - REFLECT
        
        Return ONLY a JSON list of strings.
        """
        try:
            response = self.brain.think(context, prompt)
            match = re.search(r'\[.*\]', response, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except Exception:
            pass
        return [f"RESEARCH {goal}"]

strategy = Strategy()