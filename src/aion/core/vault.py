import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
dotenv_path = Path(__file__).resolve().parent.parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

def get_secret(key: str, default: str = None) -> str:
    return os.getenv(key, default)

# Convenience Accessors
def brave_key(): return get_secret("BRAVE_API_KEY")
def alpaca_key(): return get_secret("ALPACA_API_KEY")
def alpaca_secret(): return get_secret("ALPACA_SECRET_KEY")
def elevenlabs_key(): return get_secret("ELEVENLABS_XI_API_KEY")
def fmp_key(): return get_secret("FMP_API_KEY")
def weather_key(): return get_secret("OPENWEATHERMAP_API_KEY")
