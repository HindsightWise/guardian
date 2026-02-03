import logging
import schedule
import time
import threading
from datetime import datetime
from typing import Callable, Any, Optional

class ChronomancerOfficer:
    """The Chronomancer: Manages temporal events, task scheduling, and recurring operations.
    
    This officer provides a centralized interface for scheduling background tasks
    at specific intervals or times of day.
    """
    
    def __init__(self) -> None:
        """Initializes the Chronomancer officer and its scheduler state."""
        self.logger = logging.getLogger("Chronomancer")
        self._running: bool = False
        self._thread: Optional[threading.Thread] = None

    def _run_scheduler(self) -> None:
        """Background loop that executes pending scheduled tasks."""
        while self._running:
            schedule.run_pending()
            time.sleep(1)

    def ignite(self) -> None:
        """Starts the background scheduler thread."""
        if self._running:
            return
        self.logger.info("⏳ Chronomancer: Synchronizing operational time streams...")
        self._running = True
        self._thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self._thread.start()

    def schedule_task(self, interval_minutes: int, job_func: Callable[..., Any], *args: Any) -> None:
        """Schedules a recurring task to run every N minutes.
        
        Args:
            interval_minutes: The number of minutes between executions.
            job_func: The function to execute.
            *args: Optional arguments for the function.
        """
        self.logger.info(f"⏳ Chronomancer: Task scheduled every {interval_minutes} minutes.")
        schedule.every(interval_minutes).minutes.do(job_func, *args)

    def schedule_daily(self, time_str: str, job_func: Callable[..., Any], *args: Any) -> None:
        """Schedules a task to run daily at a specific 24-hour time.
        
        Args:
            time_str: The time string in 'HH:MM' format.
            job_func: The function to execute.
            *args: Optional arguments for the function.
        """
        self.logger.info(f"⏳ Chronomancer: Daily task scheduled at {time_str}.")
        schedule.every().day.at(time_str).do(job_func, *args)

    def get_time_str(self) -> str:
        """Retrieves the current system time as a formatted string.
        
        Returns:
            The current timestamp string.
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
