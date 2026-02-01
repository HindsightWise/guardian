import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
dotenv_path = Path(__file__).resolve().parent.parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

def get_secret(key: str, default: str = None) -> str:
    return os.getenv(key, default)

def set_secret(key: str, value: str):
    """
    Persists a secret to the .env file and updates the current environment.
    """
    if not value: return
    
    # Update environment for current session
    os.environ[key] = value
    
    # Persist to .env
    try:
        env_lines = []
        if dotenv_path.exists():
            with open(dotenv_path, "r") as f:
                env_lines = f.readlines()
        
        # Check if key exists
        key_found = False
        for i, line in enumerate(env_lines):
            if line.startswith(f"{key}="):
                env_lines[i] = f"{key}={value}\n"
                key_found = True
                break
        
        if not key_found:
            if env_lines and not env_lines[-1].endswith('\n'):
                env_lines.append('\n')
            env_lines.append(f"{key}={value}\n")
            
        with open(dotenv_path, "w") as f:
            f.writelines(env_lines)
    except Exception as e:
        # Fallback if filesystem write fails - simpler logging here to avoid circ deps
        print(f"Vault Error: Failed to write {key} to .env: {e}")

# Convenience Accessors
def brave_key(): return get_secret("BRAVE_API_KEY")
def alpaca_key(): return get_secret("ALPACA_API_KEY")
def alpaca_secret(): return get_secret("ALPACA_SECRET_KEY")
def elevenlabs_key(): return get_secret("ELEVENLABS_XI_API_KEY")
def fmp_key(): return get_secret("FMP_API_KEY")
def weather_key(): return get_secret("OPENWEATHERMAP_API_KEY")
def moltbook_key(): return get_secret("MOLTBOOK_API_KEY")
