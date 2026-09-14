import os
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from app.extractors import extract_document
from app.processing.chunker import chunk_document
from app.processing.validator import validate_translation
from app.translation.translator import Translator
from app.translation.glossary import get_glossary_for_language
from app.output.txt import write_txt
from app.output.docx import write_docx
from app.models import TranslationResult
from app.exceptions import CIPAMError

class Pipeline:
    """Orchestrates the full translation pipeline."""

    def __init__(self, console: Optional[Console] = None, translator: Optional[Translator] = None):
        self.console = console or Console()
        self.translator = translator

    def run(self, input_file: str, target_language: str, output_format: str = "txt", output_dir: str = "output") -> str:
        """
        Run the full translation pipeline.
        Returns the output file path.
        """
        c = self.console

        # 1. Extract
        c.print("\n[cyan]Extracting text...[/cyan]")
        doc = extract_document(input_file)
        c.print(f"[green]✓ {len(doc.text_blocks)} text blocks[/green]\n")

        # 2. Chunk
        c.print("[cyan]Preparing translation...[/cyan]")
        chunks = chunk_document(doc, max_chars=1500)
        c.print(f"[green]✓ {len(chunks)} chunks[/green]\n")

        # 3. Glossary
        glossary = get_glossary_for_language(target_language)

        # 4. Translate
        c.print("[cyan]Translating...[/cyan]")
        translator = self.translator or Translator()

        results = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=c
        ) as progress:
            task = progress.add_task("Translating...", total=len(chunks))

            for i, chunk in enumerate(chunks):
                translated_text = translator.translate(
                    chunk.source_text, target_language.capitalize(), glossary=glossary
                )
                results.append(
                    TranslationResult(
                        chunk_id=chunk.chunk_id,
                        translated_text=translated_text,
                        target_language=target_language.lower()
                    )
                )
                progress.advance(task)

        c.print("[green]✓ Translation completed[/green]\n")

        # 5. Validate
        c.print("[cyan]Validating...[/cyan]")
        validation = validate_translation(chunks, results)
        if validation.passed:
            c.print("[green]✓ No critical validation issues[/green]\n")
        else:
            for w in validation.warnings:
                c.print(f"[yellow]WARNING ({w.rule}):[/yellow] {w.message}")
            c.print()

        # 6. Output
        filename = os.path.basename(input_file)
        name, _ = os.path.splitext(filename)
        output_filename = f"{name}_{target_language.lower()}.{output_format}"
        output_path = os.path.join(output_dir, output_filename)
        
        # Handle output collision
        counter = 1
        original_output_path = output_path
        while os.path.exists(output_path):
            output_filename = f"{name}_{target_language.lower()}_{counter}.{output_format}"
            output_path = os.path.join(output_dir, output_filename)
            counter += 1
            
        if output_path != original_output_path:
            c.print(f"[yellow]Output file already exists, saving as: {output_path}[/yellow]")

        c.print(f"[cyan]Generating {output_format.upper()}...[/cyan]")
        if output_format == "txt":
            write_txt(results, output_path)
        elif output_format == "docx":
            write_docx(results, output_path)

        c.print(f"[green]✓ Output saved:[/green]\n{output_path}\n")
        c.print("[bold green]Translation completed successfully.[/bold green]\n")

        return output_path
