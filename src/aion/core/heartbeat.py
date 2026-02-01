# aion/core/heartbeat.py
import time
import sys
import os
import logging
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from aion.core.mind import Mind
from aion.core.security import SecurityProtocol
from aion.constructs import sentinel, seeker, social
from aion.core.will import Will
from aion.core.memory.engine import memory

# Configure Logging
LOG_FILE = Path(os.getcwd()) / "aion_debug.log"
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
    
    logging.info(f"🏛️ AION: Active on '{path}'")
    logging.info("   - Sentinel Construct: ONLINE")
    logging.info("   - Seeker Construct: ONLINE")
    
    # Ignite Social Hub
    social.ignite()
    logging.info("   - Social Hub: IGNITED (Telegram: Dr_Clawed_Bot)")
    
    event_handler = AionEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    
    will_engine = Will(Path(path).resolve())
    will_engine.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    logging.info("Aion: Dormant.")

if __name__ == "__main__":
    start_daemon_main()
