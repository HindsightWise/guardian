import logging
import random
import os
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw

class ArtistOfficer:
    """The Artist: Generates visual assets and generative art for Aion.
    
    This officer handles the creation of unique abstract sigils and text-based
    image cards for social media and documentation.
    """
    
    def __init__(self) -> None:
        """Initializes the Artist officer and its logger."""
        self.logger = logging.getLogger("Artist")

    def generate_sigil(self, seed_text: str, filename: str = "sigil.png") -> str:
        """Generates a unique abstract 'sigil' based on a deterministic text seed.
        
        Args:
            seed_text: The text string to seed the generation (e.g., a goal or name).
            filename: The desired filename for the output image.
            
        Returns:
            The absolute path to the generated sigil image.
        """
        self.logger.info(f"🎨 Artist: Generating sigil for: '{seed_text}'")
        
        # Seed random with the text to make generation deterministic
        random.seed(seed_text)
        
        width, height = 512, 512
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Generate complex abstract patterns
        for _ in range(75):
            shape_type = random.choice(['rectangle', 'ellipse', 'line', 'polygon'])
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            
            if shape_type == 'rectangle':
                draw.rectangle([x1, y1, x2, y2], fill=color + (128,))
            elif shape_type == 'ellipse':
                draw.ellipse([x1, y1, x2, y2], fill=color + (128,))
            elif shape_type == 'line':
                draw.line([x1, y1, x2, y2], fill=color, width=random.randint(2, 8))
            elif shape_type == 'polygon':
                # Create a small random triangle
                draw.polygon([(x1, y1), (x2, y2), (random.randint(0, width), random.randint(0, height))], fill=color + (100,))

        # Ensure output directory exists
        output_dir = Path(os.getcwd()) / "User_Content"
        output_dir.mkdir(exist_ok=True)
        
        output_path = output_dir / filename
        image.save(output_path)
        return str(output_path.absolute())

    def create_text_card(self, text: str, filename: str = "quote.png") -> str:
        """Creates an image card with centered text for social sharing.
        
        Args:
            text: The text content to display on the card.
            filename: The desired filename for the output image.
            
        Returns:
            The absolute path to the generated text card.
        """
        self.logger.info(f"🎨 Artist: Creating text card for -> {text[:20]}...")
        img = Image.new('RGB', (800, 400), color=(20, 20, 20))
        draw = ImageDraw.Draw(img)
        
        # Simple text rendering fallback (centered)
        draw.text((100, 180), text[:80], fill=(240, 240, 240))
        
        output_dir = Path(os.getcwd()) / "User_Content"
        output_dir.mkdir(exist_ok=True)
        
        output_path = output_dir / filename
        img.save(output_path)
        return str(output_path.absolute())
