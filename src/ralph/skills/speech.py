import requests
import os
import subprocess
from ralph.core import secrets

def speak(text: str, voice_id: str = "pNInz6obpg8ndclQU7Nc"): # Default 'George' or similar
    """
    Synthesizes speech using ElevenLabs or falls back to system 'say'.
    """
    api_key = secrets.elevenlabs_key()
    
    if api_key:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
        }
        
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                audio_file = "ralph_speech.mp3"
                with open(audio_file, "wb") as f:
                    f.write(response.content)
                # Play audio on Mac
                subprocess.run(["afplay", audio_file])
                return
        except Exception:
            pass # Fallback to 'say'
            
    # Fallback to Mac built-in 'say'
    subprocess.run(["say", text])
