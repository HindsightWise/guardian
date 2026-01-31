# aion/constructs/mermaid.py
import subprocess
import os
from pathlib import Path

class Viz:
    """
    Visualizes AION's internal states and flows using Mermaid.
    """
    @staticmethod
    def render(mermaid_code: str, output_name: str = "AION_FLOW"):
        """
        Saves Mermaid code to a file. 
        In a full UI environment, this would render to SVG.
        """
        path = Path(os.getcwd()) / f"{output_name}.mmd"
        with open(path, "w") as f:
            f.write(mermaid_code)
        return f"Visualization saved to {path}"

    @staticmethod
    def plan_to_mermaid(steps: list) -> str:
        """
        Converts a sequence of tactical actions into a Mermaid diagram.
        """
        mmd = "graph TD\n"
        mmd += "  Start((Architect)) --> S1\n"
        for i, step in enumerate(steps):
            mmd += f"  S{i+1}[{step}]"
            if i < len(steps) - 1:
                mmd += f" --> S{i+2}\n"
            else:
                mmd += " --> End((Goal Met))\n"
        return mmd
