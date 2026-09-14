import os
from typing import List
from app.models import TranslationResult
from app.exceptions import CIPAMError, OutputError

def write_txt(results: List[TranslationResult], output_path: str) -> None:
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            for result in results:
                f.write(result.translated_text + "\n\n")
    except Exception as e:
        raise OutputError(f"Failed to write TXT output to {output_path}: {e}")
