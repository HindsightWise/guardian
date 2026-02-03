# aion/core/heartbeat.py
import time
import sys
import os
import logging
from dotenv import load_dotenv

# Load env vars before anything else
load_dotenv()

from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from aion.core.agent import agent
from aion.core.security import SecurityProtocol
from aion.constructs import sentinel, seeker

# Configure Logging
LOG_FILE = Path(os.getcwd()) / "Agent_Data" / "aion_debug.log"
if not LOG_FILE.parent.exists():
    LOG_FILE.parent.mkdir(parents=True)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%a %b %d %H:%M:%S %Y",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

# brain = Mind() # Moved to lazy init

class AionEventHandler(FileSystemEventHandler):
    """The central nervous system of AION's event processing."""
    
    def on_modified(self, event):
        super().on_modified(event)
        path = Path(event.src_path)
        
        if path.suffix == ".py" and "migrations" not in str(path):
            logging.info(f"🐍 Sentinel active: {path.name}")
            try:
                sentinel.generate_migration(path)
            except Exception as e:
                logging.error(f"❌ Sentinel Error: {e}")

        elif path.suffix in [".md", ".txt"]:
            logging.info(f"📝 Seeker active: {path.name}")
            try:
                seeker.analyze_note(path)
            except Exception as e:
                logging.error(f"❌ Seeker Error: {e}")

def start_daemon_main():
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    resolved_path = Path(path).resolve()
    
    # 0. SECURITY CHECK & AUDIT
    SecurityProtocol.ensure_secure_connection(resolved_path)
    
    logging.info(f"🏛️ AION__PRIME: Active on '{path}'")
    
    # Initialize and Wake Up the Agent
    agent.root_path = resolved_path
    agent.wake_up()
    
    event_handler = AionEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    logging.info("Aion__Prime: Dormant.")

if __name__ == "__main__":
    start_daemon_main()
