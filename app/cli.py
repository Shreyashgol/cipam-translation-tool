import os
import sys
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt

from app.pipeline import Pipeline
from app.exceptions import CIPAMError

app = typer.Typer(help="CIPAM Translation Tool")
console = Console()

SUPPORTED_LANGUAGES = ["hindi", "marathi", "bengali", "gujarati", "tamil", "telugu"]
SUPPORTED_EXTENSIONS = [".txt", ".pdf", ".docx", ".png", ".jpg", ".jpeg"]

def _validate_inputs(input_file: str, to: str):
    if to.lower() not in SUPPORTED_LANGUAGES:
        console.print(f"[red]Error:[/red] Unsupported target language '{to}'. Supported: {', '.join(SUPPORTED_LANGUAGES)}")
        raise typer.Exit(code=1)
    if not os.path.exists(input_file):
        console.print(f"[red]Error:[/red] File not found '{input_file}'")
        raise typer.Exit(code=1)
    ext = os.path.splitext(input_file)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        console.print(f"[red]Error:[/red] Unsupported file type '{ext}'. Supported: {', '.join(SUPPORTED_EXTENSIONS)}")
        raise typer.Exit(code=1)

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    CIPAM Translation Tool
    English -> Indian Languages
    """
    if ctx.invoked_subcommand is None:
        console.print(
            Panel.fit(
                "       CIPAM Translation Tool       \n        English → Indian Languages  ",
                title="Welcome",
                border_style="blue",
            )
        )

        try:
            input_file = Prompt.ask("\nSelect input file")

            if not os.path.exists(input_file):
                console.print(f"[red]Error:[/red] File not found '{input_file}'")
                raise typer.Exit(code=1)

            ext = os.path.splitext(input_file)[1].lower()
            ext_name = ext[1:].upper() if ext else "UNKNOWN"
            if ext not in SUPPORTED_EXTENSIONS:
                console.print(f"[red]Error:[/red] Unsupported file type '{ext}'. Supported: {', '.join(SUPPORTED_EXTENSIONS)}")
                raise typer.Exit(code=1)

            console.print(f"\nDetected file type: {ext_name} ✓\n")

            console.print("Select target language:\n")
            for i, lang in enumerate(SUPPORTED_LANGUAGES, 1):
                console.print(f"{i}. {lang.capitalize()}")
            console.print()

            lang_idx = IntPrompt.ask(">", choices=[str(i) for i in range(1, len(SUPPORTED_LANGUAGES) + 1)])
            target_lang = SUPPORTED_LANGUAGES[lang_idx - 1]

            console.print("\nSelect output format:\n")
            console.print("1. TXT")
            console.print("2. DOCX")
            console.print()

            format_idx = IntPrompt.ask(">", choices=["1", "2"])
            output_format = "txt" if format_idx == 1 else "docx"

            console.print("\nStarting translation...")

            pipeline = Pipeline(console=console)
            pipeline.run(input_file, target_lang, output_format)

        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled by user.[/yellow]")
            sys.exit(0)

@app.command()
def languages():
    """List supported target languages."""
    console.print("[bold]Supported Target Languages:[/bold]")
    for i, lang in enumerate(SUPPORTED_LANGUAGES, 1):
        console.print(f"{i}. {lang.capitalize()}")
    console.print()

@app.command()
def translate(
    input_file: str = typer.Argument(..., help="Path to input file"),
    to: str = typer.Option(..., "--to", help="Target language"),
    format: str = typer.Option("txt", "--format", help="Output format (txt or docx)"),
):
    """Translate a document from English to a regional language."""

    console.print(
        Panel.fit(
            "       CIPAM Translation Tool       \n        English → Indian Languages  ",
            border_style="blue",
        )
    )

    console.print(f"\n[bold]Input:[/bold]\n{input_file}\n")
    console.print(f"[bold]Target:[/bold]\n{to.capitalize()}\n")

    _validate_inputs(input_file, to)

    try:
        pipeline = Pipeline(console=console)
        pipeline.run(input_file, to, format)
    except CIPAMError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Unexpected Error:[/red] {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
