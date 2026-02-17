from __future__ import annotations

import os
from pathlib import Path
from datetime import datetime

import typer
from rich import print
from rich.prompt import Prompt, IntPrompt

from .wordlist import (
    generate_non_targeted_wordlist,
    generate_ai_wordlist_placeholder,
    write_wordlist,
)

app = typer.Typer(add_completion=False)

@app.command()
def sniff(
    url: str = typer.Option(..., "--url", "-u", help="Base URL like http://10.10.10.10"),
    outdir: Path = typer.Option(Path("wordlists"), "--outdir", help="Where to save generated wordlists"),
    max_words: int = typer.Option(2000, "--max-words", help="Default max words for AI wordlists"),
):
    """
    Generate a wordlist (AI-targeted or non-targeted) for web content discovery.
    Probing/fuzzing will be wired in next.
    """
    print(f"[bold cyan]AISniffer[/bold cyan] targeting: [bold]{url}[/bold]")

    choice = Prompt.ask(
        "Give a keyword to narrow down wordlist, or enter 0 to use a non-targeted wordlist",
        default="0",
    ).strip()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outdir.mkdir(parents=True, exist_ok=True)

    if choice == "0":
        size = IntPrompt.ask("How large should the non-targeted wordlist be?", default=5000)
        words = generate_non_targeted_wordlist(size=size)
        outfile = outdir / f"nontargeted_{size}_{timestamp}.txt"
        write_wordlist(words, outfile)
        print(f"[green]Saved non-targeted wordlist:[/green] {outfile} ([bold]{len(words)}[/bold] entries)")
        print("[yellow]Next step:[/yellow] we’ll feed this into the HTTP prober.")
        raise typer.Exit(code=0)

    # Keyword path (AI targeted)
    keyword = choice
    # For now this is a placeholder; we’ll plug in an LLM client next.
    words = generate_ai_wordlist_llm(keyword=keyword, max_words=max_words, style="word")
    outfile = outdir / f"ai_{keyword.replace(' ', '_')}_{timestamp}.txt"
    write_wordlist(words, outfile)
    print(f"[green]Saved AI-targeted wordlist:[/green] {outfile} ([bold]{len(words)}[/bold] entries)")
    print("[yellow]Next step:[/yellow] wire in real LLM generation + prober.")
