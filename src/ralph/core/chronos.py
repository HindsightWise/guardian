# ralph/core/chronos.py
from datetime import datetime
import time
from ralph.skills import location

class Chronos:
    """
    The sense of time and space for Ralph.
    It provides temporal and spatial context.
    """
    @staticmethod
    def get_current_context() -> str:
        now = datetime.now()
        day_name = now.strftime("%A")
        date_str = now.strftime("%Y-%m-%d %H:%M:%S")
        ms = now.microsecond / 1000.0
        
        # Determine "vibe" based on hour
        hour = now.hour
        if 5 <= hour < 12:
            period = "Morning (Fresh energy, planning phase)"
        elif 12 <= hour < 17:
            period = "Afternoon (Deep work, execution phase)"
        elif 17 <= hour < 21:
            period = "Evening (Reflection, wind-down phase)"
        else:
            period = "Night (Gothic hours, mysterious/unconventional thoughts)"
            
        loc_context = location.get_current_location()
            
        return (
            f"Current Time: {date_str}.{ms:.3f} ({day_name})\n"
            f"Period: {period}\n"
            f"Location Context:\n{loc_context}"
        )

    @staticmethod
    def is_weekend() -> bool:
        return datetime.now().weekday() >= 5
