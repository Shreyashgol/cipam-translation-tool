import os
import docx as python_docx
from typing import List
from app.models import TranslationResult
from app.exceptions import CIPAMError, OutputError

def write_docx(results: List[TranslationResult], output_path: str) -> None:
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        doc = python_docx.Document()
        for result in results:
            doc.add_paragraph(result.translated_text)

        doc.save(output_path)
    except Exception as e:
        raise OutputError(f"Failed to write DOCX output to {output_path}: {e}")
