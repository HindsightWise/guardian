import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown
from ralph.brain import RalphBrain
from ralph.skills import researcher, finance, speech

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
            
        # 1. Handle special triggers
        context = ""
        
        # Financial context trigger
        if any(keyword in user_input.lower() for keyword in ["stock", "market", "portfolio", "price"]):
            with console.status("[bold yellow]Checking Markets...[/bold yellow]"):
                # If they mention a ticker, check it. Otherwise check portfolio.
                ticker_match = [word for word in user_input.split() if word.isupper() and 1 <= len(word) <= 5]
                if ticker_match:
                    market_info = finance.get_market_snapshot(ticker_match)
                else:
                    market_info = finance.analyze_portfolio()
                context += f"Financial Context:\n{market_info}\n\n"

        # Research trigger
        if "?" in user_input or "search" in user_input.lower():
            with console.status("[bold blue]Researching...[/bold blue]"):
                search_results = researcher.brave_search(user_input)
                context += f"Search Results from Brave:\n{search_results}\n\n"
        
        # 2. Think
        with console.status("[bold green]Thinking...[/bold green]"):
            response = brain.think(
                context=context + "User is chatting directly via CLI.",
                task=user_input
            )
            
        # 3. Output
        console.print(Panel(Markdown(response), title="[bold magenta]Ralph[/bold magenta]", border_style="magenta"))
        
        # 4. Speak (Optional: only if asked or for short responses)
        if "speak" in user_input.lower() or "say" in user_input.lower() or len(response) < 200:
            speech.speak(response)
