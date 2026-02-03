import logging
import music21
from typing import Dict, Any, List, Optional

class BardOfficer:
    """The Bard: Analyzes music theory and constructs harmonic structures.
    
    This officer utilizes the 'music21' toolkit to provide deep musicological
    insights, scale generation, and chord identification for the Aion system.
    """
    
    def __init__(self) -> None:
        """Initializes the Bard officer and its logger."""
        self.logger = logging.getLogger("Bard")

    def analyze_note(self, note_name: str) -> Dict[str, Any]:
        """Analyzes a specific musical note for its frequency and MIDI properties.
        
        Args:
            note_name: The name of the note (e.g., 'C4', 'Eb3').
            
        Returns:
            A dictionary containing the pitch name, frequency (Hz), and MIDI value.
        """
        self.logger.info(f"🎵 Bard: Analyzing note -> {note_name}")
        try:
            n = music21.note.Note(note_name)
            return {
                "name": n.nameWithOctave,
                "frequency": round(n.pitch.frequency, 2),
                "midi": n.pitch.midi
            }
        except Exception as e:
            self.logger.error(f"❌ Bard: Note analysis failed: {e}")
            return {"error": str(e)}

    def get_scale(self, tonic: str, scale_type: str = "major") -> List[str]:
        """Generates a musical scale based on a tonic note and scale type.
        
        Args:
            tonic: The starting note of the scale.
            scale_type: The type of scale ('major', 'minor').
            
        Returns:
            A list of note names representing the scale.
        """
        self.logger.info(f"🎹 Bard: Constructing {tonic} {scale_type} scale...")
        try:
            if scale_type.lower() == "major":
                s = music21.scale.MajorScale(tonic)
            elif scale_type.lower() == "minor":
                s = music21.scale.MinorScale(tonic)
            else:
                return ["Error: Unsupported scale type"]
            
            return [str(p.nameWithOctave) for p in s.getPitches()]
        except Exception as e:
            self.logger.error(f"❌ Bard: Scale generation failed: {e}")
            return []

    def analyze_chord(self, notes: List[str]) -> str:
        """Identifies the common name of a chord based on a list of notes.
        
        Args:
            notes: A list of note names (e.g., ['C4', 'E4', 'G4']).
            
        Returns:
            The common name of the identified chord (e.g., 'major triad').
        """
        self.logger.info(f"🎼 Bard: Analyzing chord structure -> {notes}")
        try:
            c = music21.chord.Chord(notes)
            return str(c.commonName)
        except Exception as e:
            self.logger.error(f"❌ Bard: Chord analysis failed: {e}")
            return "Unknown Chord"
