from app.extractors.txt import extract_txt
from app.extractors.pdf import extract_pdf
from app.extractors.docx import extract_docx
from app.extractors.image import extract_image
from app.exceptions import CIPAMError
import os

def extract_document(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".txt":
        return extract_txt(file_path)
    elif ext == ".pdf":
        return extract_pdf(file_path)
    elif ext == ".docx":
        return extract_docx(file_path)
    elif ext in [".png", ".jpg", ".jpeg"]:
        return extract_image(file_path)
    else:
        raise CIPAMError(f"Unsupported file type '{ext}'")
