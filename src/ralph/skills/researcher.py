from pathlib import Path
import typer
import requests
import json
import logging

BRAVE_API_KEY = "BSADiH8SakVAWOzRng0173ZFs6OPKVu"

def brave_search(query: str) -> str:
    """
    Calls the Brave Search API to get real-world information.
    """
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_API_KEY
    }
    params = {"q": query, "count": 5}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = data.get("web", {}).get("results", [])
        if not results:
            return "No search results found."
            
        summary = []
        for res in results:
            summary.append(f"- {res['title']}: {res['description']} ({res['url']})")
            
        return "\n".join(summary)
    except Exception as e:
        logging.error(f"Brave Search Error: {e}")
        return f"Search failed: {e}"

def analyze_note(file_path: Path):
    """
    Reads a modified text file, checks for questions, and appends answers.
    """
    typer.echo(f"Researcher: Analyzing {file_path.name}...")
    
    try:
        with open(file_path, "r") as f:
            content = f.read()
            
        # Trigger: Check for lines ending in ???
        # We look for the LAST occurrence of ??? to avoid infinite loops if it appends to itself
        if "???" in content:
            # Simple parsing: Get the text before the last ??? on that line
            lines = content.splitlines()
            for line in reversed(lines):
                if "???" in line:
                    question = line.replace("???", "").strip()
                    if not question: continue
                    
                    typer.echo(f"Researcher: Question detected: '{question}'")
                    
                    # 2. Research
                    search_results = brave_search(question)
                    
                    # 3. Synthesize with Brain (Optional but better)
                    from ralph.brain import GuardianBrain
                    brain = GuardianBrain()
                    synthesized_answer = brain.think(
                        context=f"Search Results for '{question}':\n{search_results}",
                        task=f"Summarize these search results for the user in your 'sarcastic nerd' persona. Be concise but informative."
                    )
                    
                    # 4. Write Back
                    # To prevent infinite loops, we'll check if we already answered this specific question
                    if f"Analysis for: {question}" in content:
                        typer.echo("Researcher: Already answered this question. Skipping.")
                        return

                    with open(file_path, "a") as f:
                        f.write(f"\n\n--- 🕵️ Ralph's Research: {question} ---\n{synthesized_answer}\n\nSources:\n{search_results}\n---------------------------\n")
                    
                    typer.echo("Researcher: Answer appended.")
                    break # Only handle one question per modification for safety
            
    except Exception as e:
        typer.echo(f"Researcher Error: {e}")