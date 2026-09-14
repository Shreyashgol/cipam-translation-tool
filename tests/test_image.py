import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from PIL import Image
from app.extractors.image import extract_image, TesseractNotFoundError
from app.exceptions import CIPAMError

def create_temp_image(width=100, height=50):
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    img = Image.new("RGB", (width, height), color="white")
    img.save(path)
    return path

@patch("app.extractors.image.shutil.which", return_value="/usr/local/bin/tesseract")
@patch("app.extractors.image.pytesseract.image_to_string")
def test_extract_image_basic(mock_ocr, mock_which):
    mock_ocr.return_value = "Hello World\n\nSecond paragraph"
    path = create_temp_image()
    try:
        doc = extract_image(path)
        assert doc.source_format == "image"
        assert len(doc.text_blocks) == 2
        assert doc.text_blocks[0].text == "Hello World"
        assert doc.text_blocks[1].text == "Second paragraph"
    finally:
        os.remove(path)

@patch("app.extractors.image.shutil.which", return_value="/usr/local/bin/tesseract")
@patch("app.extractors.image.pytesseract.image_to_string")
def test_extract_image_empty_ocr(mock_ocr, mock_which):
    mock_ocr.return_value = ""
    path = create_temp_image()
    try:
        doc = extract_image(path)
        assert len(doc.text_blocks) == 0
    finally:
        os.remove(path)

@patch("app.extractors.image.shutil.which", return_value=None)
def test_tesseract_not_installed(mock_which):
    path = create_temp_image()
    try:
        with pytest.raises(TesseractNotFoundError, match="Tesseract OCR is not installed"):
            extract_image(path)
    finally:
        os.remove(path)

def test_extract_missing_image():
    with pytest.raises(CIPAMError, match="File not found"):
        extract_image("nonexistent.png")
