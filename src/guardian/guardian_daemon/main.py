# guardian_daemon/main.py
import time
import sys
import os
from watchdog.observers.polling import PollingObserver as Observer # Explicitly use PollingObserver
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from guardian import daemon_logic # Corrected import
from guardian.brain import GuardianBrain
import random

# Use the project root for logging
LOG_FILE = Path(os.getcwd()) / "daemon_debug.log"
brain = GuardianBrain()

class ChangeEventHandler(FileSystemEventHandler):
    """Logs all the events captured to a file."""
    def __init__(self, log_file):
        self.log_file = log_file
        super().__init__()

    def _log_event(self, message):
        print(f"Attempting to write to log file: {self.log_file}") # ADDED DEBUG PRINT
        try:
            with open(self.log_file, "a") as f:
                f.write(f"[{time.ctime()}] {message}\n")
            print(f"Successfully wrote to log file: {self.log_file}") # ADDED DEBUG PRINT
        except Exception as e:
            print(f"ERROR WRITING TO LOG FILE {self.log_file}: {e}") # ADDED ERROR PRINT
        print(message) # Keep printing to stdout for direct feedback too

    def on_moved(self, event):
        super().on_moved(event)
        self._log_event(f"Moved: {event.src_path} to {event.dest_path}")

    def on_created(self, event):
        super().on_created(event)
        self._log_event(f"Created: {event.src_path}")

    def on_deleted(self, event):
        super().on_deleted(event)
        self._log_event(f"Deleted: {event.src_path}")

    def on_modified(self, event):
        super().on_modified(event)
        # Check if the modified file is a Python file
        if Path(event.src_path).suffix == ".py":
            self._log_event(f"Python file modified: {event.src_path}. Triggering migration generation.")
            # Call daemon_logic to generate migration
            daemon_logic.generate_migration(Path(event.src_path)) # Re-enabled
        else:
            self._log_event(f"Modified: {event.src_path}")

def start_daemon_main(): # No arguments here
    # Manually parse path argument
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    print(f"Guardian Daemon: Standing watch over '{path}' using POLLING observer...")
    event_handler = ChangeEventHandler(LOG_FILE) # Pass log file
    observer = Observer() # This is now PollingObserver
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    
    # Brain Heartbeat
    last_reflection = time.time()
    reflection_interval = 300 # Reflect every 5 minutes
    
    try:
        while True:
            time.sleep(1)
            # Periodic Reflection
            if time.time() - last_reflection > reflection_interval:
                # Proactive Status Check
                try:
                    from guardian.guardian_cli import migration_logic
                    # Capture stdout to see status
                    import io
                    from contextlib import redirect_stdout
                    f = io.StringIO()
                    with redirect_stdout(f):
                        migration_logic.show_status()
                    db_status = f.getvalue().strip()
                except Exception as e:
                    db_status = f"Error checking DB status: {e}"

                if random.random() > 0.5: # increased chance to speak for 'always-on' feel
                    thought = brain.think(context=f"Watching {path}. Database Status: {db_status}", task="Generate a short, proactive, 'always-on' status update. Mention the database status if relevant. Be a bit philosophical about safety.")
                    event_handler._log_event(f"🧠 Guardian Thought: {thought}")
                last_reflection = time.time()

    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    print("Guardian Daemon: Shutting down.")

if __name__ == "__main__":
    start_daemon_main()