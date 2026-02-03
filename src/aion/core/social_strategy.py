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

    def generate_post(self, raw_context: str) -> str:
        """Generates a high-value post from research context."""
        template = random.choice(self.TWEET_TEMPLATES)
        # We don't decompress here because the Mind handles Xeno-optimized context perfectly
        prompt = f"{template}\n\nActual Research/Context:\n{raw_context}"
        
        return self.brain.think(
            "Context: Social Content Engine for Aion__Prime.",
            prompt
        )

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
