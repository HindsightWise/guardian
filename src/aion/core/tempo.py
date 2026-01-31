# aion/core/tempo.py
from datetime import datetime
import time
from aion.constructs import anchor

class Tempo:
    """
    Spatiotemporal awareness for Aion.
    """
    @staticmethod
    def get_current_context() -> str:
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M:%S")
        ms = now.microsecond / 1000.0
        
        hour = now.hour
        if 5 <= hour < 12:
            period = "Dawn (Planning)"
        elif 12 <= hour < 17:
            period = "Zenith (Execution)"
        elif 17 <= hour < 21:
            period = "Dusk (Reflection)"
        else:
            period = "Nadir (Unconscious Processing)"
            
        loc_context = anchor.get_current_location()
            
        return (
            f"Tempo: {date_str}.{ms:.3f}\n"
            f"Vibe: {period}\n"
            f"Anchor:\n{loc_context}"
        )