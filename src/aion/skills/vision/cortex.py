# aion/skills/vision/cortex.py
from aion.core.mind import Mind
import base64
from pathlib import Path
import logging

class VisualCortex:
    """
    Gives Aion the ability to 'see' images using a local Vision-Language Model (Llava).
    """
    def __init__(self):
        self.logger = logging.getLogger("VisualCortex")
        self.model = "llava" # Must be pulled via 'ollama pull llava'

    def analyze_image(self, image_path: Path, prompt: str = "Describe this image in detail.") -> str:
        """
        Analyzes an image file and returns a text description.
        """
        if not image_path.exists():
            return "Error: Image file not found."

        try:
            # Encode image to base64
            with open(image_path, "rb") as img_file:
                b64_image = base64.b64encode(img_file.read()).decode('utf-8')

            # We interact directly with Ollama API structure for multimodal
            # Since the Mind class wraps simple text, we'll use a direct payload here 
            # or extend Mind. For simplicity/robustness, let's call Ollama via the Mind's underlying connection if possible,
            # but standard 'generate' endpoint supports 'images'.
            
            import requests
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [b64_image],
                "stream": False
            }
            
            response = requests.post("http://localhost:11434/api/generate", json=payload)
            if response.status_code == 200:
                return response.json().get("response", "No response from vision model.")
            else:
                return f"Vision Error: {response.text}"
                
        except Exception as e:
            self.logger.error(f"Vision failed: {e}")
            return f"Vision System Failure: {e}"

# Singleton
cortex = VisualCortex()
