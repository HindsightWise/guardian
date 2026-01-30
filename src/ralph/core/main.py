# ralph/core/main.py
import time
import sys
import os
import random
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from ralph.brain import GuardianBrain
from ralph.skills import guardian, researcher # Import skills

# Use the project root for logging
LOG_FILE = Path(os.getcwd()) / "ralph_debug.log"
brain = GuardianBrain()

class RalphEventHandler(FileSystemEventHandler):
    """The central nervous system of Ralph's event processing."""
    def __init__(self, log_file):
        self.log_file = log_file
        super().__init__()

    def _log_event(self, message):
        try:
            with open(self.log_file, "a") as f:
                f.write(f"[{time.ctime()}] {message}\n")
        except Exception as e:
            print(f"ERROR WRITING TO LOG FILE {self.log_file}: {e}")
        print(message)

    def on_modified(self, event):
        super().on_modified(event)
        path = Path(event.src_path)
        
        # --- SKILL DISPATCHER ---
        
        # Skill 1: Guardian (Database Migrations)
        if path.suffix == ".py" and "migrations" not in str(path):
            self._log_event(f"🐍 Python file modified: {path.name}. Activating Guardian Skill.")
            try:
                guardian.generate_migration(path)
            except Exception as e:
                self._log_event(f"❌ Guardian Skill Failed: {e}")

        # Skill 2: Researcher (Notes & Questions)
        elif path.suffix in [".md", ".txt"]:
            self._log_event(f"📝 Text file modified: {path.name}. Activating Researcher Skill.")
            try:
                researcher.analyze_note(path)
            except Exception as e:
                self._log_event(f"❌ Researcher Skill Failed: {e}")

def start_daemon_main():
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    print(f"⚡ RALPH DAEMON: Online and watching '{path}'")
    print("   - Guardian Skill: READY (Python/SQL)")
    print("   - Researcher Skill: READY (Markdown/Text)")
    
    event_handler = RalphEventHandler(LOG_FILE)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    
    # Brain Heartbeat
    last_reflection = time.time()
    reflection_interval = 300 
    
    try:
        while True:
            time.sleep(1)
            # Periodic Reflection
            if time.time() - last_reflection > reflection_interval:
                if random.random() > 0.5:
                    thought = brain.think(context=f"Watching {path}. System nominal.", task="Generate a proactive, 'always-on' thought about your dual role as a Coder and a Researcher.")
                    event_handler._log_event(f"🧠 Ralph Thought: {thought}")
                last_reflection = time.time()

    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    print("Ralph Daemon: Shutting down.")