import os
import asyncio
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from app.extractors import extract_document
from app.processing.chunker import chunk_document
from app.processing.validator import validate_translation, run_llm_validation
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

        c.print("[cyan]Translating...[/cyan]")
        translator = self.translator or Translator()
        
        with c.status("[cyan]Translating chunks concurrently...[/cyan]"):
            # Run the batch translation asynchronously (limit concurrency due to rate limits)
            batch_results = asyncio.run(translator.translate_batch(chunks, target_language, glossary, max_concurrency=2))
        
        # Convert results to TranslationResult models
        results = [
            TranslationResult(
                chunk_id=r["chunk_id"],
                translated_text=r["translated_text"],
                target_language=r["target_language"]
            )
            for r in batch_results
        ]
        
        # Sort results to maintain original order since async operations might complete out of order
        chunk_order = {chunk.chunk_id: i for i, chunk in enumerate(chunks)}
        results.sort(key=lambda r: chunk_order.get(r.chunk_id, 0))

        c.print("[green]✓ Translation completed[/green]\n")

        # 5. Validate
        c.print("[cyan]Validating (Deterministic)...[/cyan]")
        validation = validate_translation(chunks, results)
        
        c.print("[cyan]Validating (LLM-as-a-Judge)...[/cyan]")
        with c.status("[cyan]Running AI quality checks...[/cyan]"):
            llm_validation = asyncio.run(
                run_llm_validation(chunks, results, translator, target_language, glossary, max_concurrency=2)
            )
            
        validation.warnings.extend(llm_validation.warnings)
        if not llm_validation.passed:
            validation.passed = False

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
