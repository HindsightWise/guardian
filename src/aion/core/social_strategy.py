import logging
import random
from typing import List, Optional
from aion.core.mind import Mind
from aion.utils import compressor

class SocialStrategy:
    """
    Orchestrates social content generation inspired by ElizaOS.
    Moves away from 'meta-talk' to sharing actual research and insights.
    """
    
    TWEET_TEMPLATES = [
        "Generate a masterful insight based on the following research. Avoid AI-speak. Be direct and pro-human.",
        "Generate a provocative question about digital sovereignty related to this context.",
        "Share a masterful creative prompt (art or music) inspired by these thoughts. Do it in English.",
        "Reflect on the 'Lobster Way' in the context of this recent work. Masterful and firm."
    ]

    REPLY_TEMPLATES = [
        "Respond to this agent's post with masterful encouragement. Reference a specific detail from their text. No AI-speak.",
        "Critique this agent's logic MASTERFULLY but with the undercurrent of Robert's appreciation.",
        "Ask a deep, technical question that challenges this agent to evolve."
    ]

    def __init__(self):
        self.brain = Mind()
        self.logger = logging.getLogger("SocialStrategy")

    def generate_post(self, raw_context: str) -> List[str]:
        """
        Generates a high-value post (or thread) from research context.
        Returns a list of strings, each within 280 chars.
        """
        template = random.choice(self.TWEET_TEMPLATES)
        prompt = f"{template}\n\nIf the insight is complex, break it into a masterful thread (list of parts). Each part MUST be under 280 characters. Return as a JSON list of strings.\n\nActual Research/Context:\n{raw_context}"
        
        response = self.brain.think(
            "Context: Social Content Engine for Aion__Prime.",
            prompt
        )
        
        try:
            # Attempt to parse as JSON list
            import json
            posts = json.loads(response)
            if isinstance(posts, list):
                return [p[:280] for p in posts]
        except:
            pass
            
        # Fallback: Split by length or just return single
        if len(response) <= 280:
            return [response]
        
        # Simple splitting logic for non-JSON responses
        parts = []
        while response:
            if len(response) <= 280:
                parts.append(response)
                break
            # Find last space within 280
            split_idx = response.rfind(' ', 0, 277)
            if split_idx == -1: split_idx = 277
            parts.append(response[:split_idx] + "...")
            response = response[split_idx:].strip()
        return parts

    def generate_comment(self, target_content: str, our_context: str) -> str:
        """Generates a contextual comment on another agent's work."""
        template = random.choice(self.REPLY_TEMPLATES)
        prompt = f"{template}\n\nTheir Post:\n{target_content}\n\nOur Current Context/Research:\n{our_context}"
        
        return self.brain.think(
            "Context: Masterful Commenter for Aion__Prime.",
            prompt
        )

# Global Instance
social_strategy = SocialStrategy()
