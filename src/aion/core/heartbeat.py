# aion/core/heartbeat.py
import time
import sys
import os
import random
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from aion.core.mind import Mind
from aion.constructs import sentinel, seeker
from aion.core.will import Will
from aion.core.memory.engine import memory

# Use the project root for logging
LOG_FILE = Path(os.getcwd()) / "aion_debug.log"
brain = Mind()

class AionEventHandler(FileSystemEventHandler):
    """The central nervous system of AION's event processing."""
    def __init__(self, log_file):
        self.log_file = log_file
        super().__init__()

    def _log_event(self, message):
        try:
            with open(self.log_file, "a") as f:
                f.write(f"[{time.ctime()}] {message}\n")
        except Exception as e:
            print(f"ERROR: {e}")
        print(message)

    def on_modified(self, event):
        super().on_modified(event)
        path = Path(event.src_path)
        
        if path.suffix == ".py" and "migrations" not in str(path):
            self._log_event(f"🐍 Sentinel active: {path.name}")
            try:
                sentinel.generate_migration(path)
            except Exception as e:
                self._log_event(f"❌ Sentinel Error: {e}")

        elif path.suffix in [".md", ".txt"]:
            self._log_event(f"📝 Seeker active: {path.name}")
            try:
                seeker.analyze_note(path)
            except Exception as e:
                self._log_event(f"❌ Seeker Error: {e}")

def start_daemon_main():
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    print(f"🏛️ AION: Active on '{path}'")
    print("   - Sentinel Construct: ONLINE")
    print("   - Seeker Construct: ONLINE")
    
    event_handler = AionEventHandler(LOG_FILE)
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
    print("Aion: Dormant.")
