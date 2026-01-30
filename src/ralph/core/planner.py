# ralph/core/planner.py
import json
import logging
from typing import List, Dict
from ralph.brain import RalphBrain

class Planner:
    """
    Hierarchical Task Network (HTN) inspired planner.
    Decomposes high-level 'Spells' (Goals) into primitive 'Actions'.
    """
    def __init__(self):
        self.brain = RalphBrain()

    def decompose(self, goal: str) -> List[Dict]:
        """
        Takes a natural language goal and returns a list of actionable steps.
        """
        context = f"Goal: {goal}"
        prompt = """
        Decompose this high-level goal into 2-3 primitive actions.
        Available Action Types: 
        - RESEARCH [topic]
        - MARKET [ticker]
        - AUDIT [filename]
        - ALERT [message]
        - REFLECT
        
        Return ONLY a JSON list of strings.
        Example: ["MARKET NVDA", "RESEARCH AI hardware trends", "ALERT Done checking Nvidia."]
        """
        
        try:
            response = self.brain.think(context, prompt)
            # Find JSON block
            import re
            match = re.search(r'\[.*\]', response, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except Exception as e:
            logging.error(f"Planner Error: {e}")
            
        return [f"RESEARCH {goal}"] # Fallback

planner = Planner()
