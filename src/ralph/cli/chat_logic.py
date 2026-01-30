import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown
from ralph.brain import RalphBrain
from ralph.skills.researcher import brave_search

console = Console()
brain = RalphBrain()

def start_chat_session():
    """
    Interactive chat session with Ralph.
    """
    console.print(Panel.fit("[bold green]⚡ Ralph CLI Chat Online[/bold green]\nType 'exit' to quit.", border_style="green"))
    
    while True:
        user_input = Prompt.ask("[bold cyan]You[/bold cyan]")
        
        if user_input.lower() in ["exit", "quit", "bye"]:
            console.print("[yellow]Ralph signing off.[/yellow]")
            break
            
        # Check for research trigger in chat
        context = ""
        if "?" in user_input or "search" in user_input.lower():
            with console.status("[bold blue]Researching...[/bold blue]"):
                search_results = brave_search(user_input)
                context = f"Search Results from Brave:\n{search_results}\n\n"
        
        with console.status("[bold green]Thinking...[/bold green]"):
            response = brain.think(
                context=context + "User is chatting directly via CLI.",
                task=user_input
            )
            
        console.print(Panel(Markdown(response), title="[bold magenta]Ralph[/bold magenta]", border_style="magenta"))
