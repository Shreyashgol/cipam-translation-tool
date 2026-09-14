import os
import fitz # PyMuPDF
from app.models import Document, TextBlock
from app.exceptions import CIPAMError, ExtractionError

def extract_pdf(file_path: str) -> Document:
    if not os.path.exists(file_path):
        raise CIPAMError(f"File not found: {file_path}")

    filename = os.path.basename(file_path)
    doc = Document(source_filename=filename, source_format="pdf")

    try:
        pdf_document = fitz.open(file_path)
    except Exception as e:
        raise ExtractionError(f"Failed to open PDF file {file_path}: {e}")

    index = 0
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        
        # Extract blocks of text. dict=False returns list of blocks
        blocks = page.get_text("blocks")
        
        for b in blocks:
            text = b[4].strip()
            # Basic filtering for completely empty blocks
            if not text:
                continue
                
            block = TextBlock(
                text=text,
                block_type="paragraph", # Basic assumption for pdf blocks
                index=index,
                page_number=page_num + 1
            )
            doc.text_blocks.append(block)
            index += 1

    return doc
