# aion/interface/comm_link.py
from rich.console import Console
from rich.panel import Panel
from aion.core.mind import Mind
from aion.constructs import seeker, ledger, voice

console = Console()

def start_chat():
    brain = Mind()
    console.print(Panel("🏛️ [bold]AION COMM LINK ESTABLISHED[/bold]", subtitle="The Architect is listening"))
    
    while True:
        user_input = console.input("[bold blue]Query:[/bold blue] ")
        if user_input.lower() in ["exit", "quit"]: break
        
        response = brain.think("", user_input)
        console.print(f"\n[bold green]Aion:[/bold green] {response}\n")