import logging
from pathlib import Path
from typing import Dict, Any, Optional
from textblob import TextBlob

class CriticOfficer:
    """The Critic: Analyzes textual content for sentiment, subjectivity, and tone.
    
    This officer provides quantitative analysis of text files or strings to
    assess the emotional and objective qualities of the content.
    """
    
    def __init__(self) -> None:
        """Initializes the Critic officer and its logger."""
        self.logger = logging.getLogger("Critic")

    def analyze_file(self, file_path: str) -> str:
        """Reads a file and provides a detailed critique of its sentiment and composition.
        
        Args:
            file_path: The filesystem path to the file for analysis.
            
        Returns:
            A formatted string report containing the critique.
        """
        self.logger.info(f"🧐 Critic: Analyzing file -> {file_path}")
        try:
            path = Path(file_path).resolve()
            if not path.exists():
                return "❌ Critic: File not found."
            
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            if not content.strip():
                return "❌ Critic: File is empty."

            blob = TextBlob(content)
            sentiment = blob.sentiment
            
            report = (
                f"--- 🧐 Critic's Report: {path.name} ---\n"
                f"Word Count: {len(blob.words)}\n"
                f"Sentiment (Polarity): {sentiment.polarity:.2f} (-1.0 Negative to 1.0 Positive)\n"
                f"Subjectivity: {sentiment.subjectivity:.2f} (0.0 Objective to 1.0 Subjective)\n\n"
                f"Top Noun Phrases:\n"
                f"{', '.join(blob.noun_phrases[:5]) if blob.noun_phrases else 'None detected.'}\n"
                f"---------------------------------------"
            )
            return report
        except Exception as e:
            self.logger.error(f"❌ Critic: Analysis failed: {e}")
            return f"❌ Critic: Error analyzing file: {e}"

    def quick_check(self, text: str) -> Dict[str, float]:
        """Performs a rapid sentiment and subjectivity check on a string.
        
        Args:
            text: The text string to analyze.
            
        Returns:
            A dictionary containing the polarity and subjectivity scores.
        """
        blob = TextBlob(text)
        return {
            "polarity": float(blob.sentiment.polarity), 
            "subjectivity": float(blob.sentiment.subjectivity)
        }
