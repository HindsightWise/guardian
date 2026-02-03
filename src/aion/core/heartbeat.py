# aion/core/heartbeat.py
import time
import sys
import os
import logging
import asyncio
from dotenv import load_dotenv

# Load env vars before anything else
load_dotenv()

from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from aion.core.agent import agent
from aion.core.security import SecurityProtocol
from aion.constructs import sentinel, seeker
from aion.core.skills_registry import SkillsRegistry

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

# Initialize Registry
registry = SkillsRegistry()

# --- Skill Wrappers ---
async def sentinel_migration_wrapper(path: Path):
    """Wrapper for synchronous sentinel migration."""
    if "migrations" in str(path):
        return
    logging.info(f"🐍 Sentinel active: {path.name}")
    try:
        sentinel.generate_migration(path)
    except Exception as e:
        logging.error(f"❌ Sentinel Error: {e}")

async def seeker_todo_wrapper(path: Path):
    """Wrapper for Seeker TODO processing."""
    logging.info(f"📋 Seeker active on TODO list: {path.name}")
    try:
        await seeker.process_todo(path)
    except Exception as e:
        logging.error(f"❌ Seeker Error (TODO): {e}")

async def seeker_note_wrapper(path: Path):
    """Wrapper for Seeker Note analysis."""
    if path.name == "TODO.md": return # Handled by specific rule
    logging.info(f"📝 Seeker active: {path.name}")
    try:
        await seeker.analyze_note(path)
    except Exception as e:
        logging.error(f"❌ Seeker Error: {e}")

# --- Register Skills ---
registry.register("*.py", sentinel_migration_wrapper, "Sentinel (Migration)")
registry.register("TODO.md", seeker_todo_wrapper, "Seeker (TODO)")
registry.register("*.md", seeker_note_wrapper, "Seeker (Analysis)")
registry.register("*.txt", seeker_note_wrapper, "Seeker (Analysis)")


class AionEventHandler(FileSystemEventHandler):
    """The central nervous system of AION's event processing."""
    
    def on_modified(self, event):
        super().on_modified(event)
        if event.is_directory:
            return
            
        path = Path(event.src_path)
        # Dispatch to registry
        # We use asyncio.run because Watchdog is threaded/sync
        try:
            asyncio.run(registry.dispatch(path))
        except Exception as e:
             logging.error(f"❌ Event Loop Error: {e}")


def start_daemon_main():
    # Filter out flags like --help to avoid watchdog path errors
    args = [arg for arg in sys.argv[1:] if not arg.startswith('-')]
    path = args[0] if args else "."
    resolved_path = Path(path).resolve()
    
    if not resolved_path.exists():
        logging.error(f"❌ Heartbeat: Path '{resolved_path}' does not exist. Where am I, Morty?")
        return
    
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
