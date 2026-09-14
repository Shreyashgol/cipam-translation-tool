import os
import re
from app.models import Document, TextBlock
from app.exceptions import CIPAMError, ExtractionError

def extract_txt(file_path: str) -> Document:
    if not os.path.exists(file_path):
        raise CIPAMError(f"File not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            content = f.read()
    except Exception as e:
        raise ExtractionError(f"Failed to read file {file_path}: {e}")

    filename = os.path.basename(file_path)
    doc = Document(source_filename=filename, source_format="txt")

    # Split by double newlines or more to separate paragraphs
    raw_paragraphs = re.split(r'\n\s*\n', content)

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
