import os
import shutil
import re
from PIL import Image
import pytesseract
from app.models import Document, TextBlock
from app.exceptions import CIPAMError, ExtractionError

class TesseractNotFoundError(CIPAMError):
    """Raised when Tesseract OCR is not installed."""
    pass

def _check_tesseract():
    """Check if Tesseract is available on the system."""
    if shutil.which("tesseract") is None:
        raise TesseractNotFoundError(
            "Tesseract OCR is not installed or not found in PATH.\n"
            "Install it:\n"
            "  macOS:   brew install tesseract\n"
            "  Ubuntu:  sudo apt-get install tesseract-ocr\n"
            "  Windows: https://github.com/UB-Mannheim/tesseract/wiki"
        )

def extract_image(file_path: str) -> Document:
    if not os.path.exists(file_path):
        raise CIPAMError(f"File not found: {file_path}")

    _check_tesseract()

    filename = os.path.basename(file_path)
    doc = Document(source_filename=filename, source_format="image")

    try:
        image = Image.open(file_path)
    except Exception as e:
        raise ExtractionError(f"Failed to open image {file_path}: {e}")

    try:
        text = pytesseract.image_to_string(image)
    except Exception as e:
        raise ExtractionError(f"OCR failed on {file_path}: {e}")

    if not text or not text.strip():
        return doc  # Return empty document

    # Split into paragraphs by double newlines
    raw_paragraphs = re.split(r'\n\s*\n', text)

    index = 0
    for para in raw_paragraphs:
        para = para.strip()
        if not para:
            continue

        block = TextBlock(
            text=para,
            block_type="paragraph",
            index=index
        )
        doc.text_blocks.append(block)
        index += 1

    return doc
