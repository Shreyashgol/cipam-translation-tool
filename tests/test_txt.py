import os
import tempfile
import pytest
from app.extractors.txt import extract_txt
from app.exceptions import CIPAMError

def create_temp_file(content: str, encoding: str = "utf-8") -> str:
    fd, path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(fd, "w", encoding=encoding) as f:
        f.write(content)
    return path

def test_extract_normal_text():
    content = "This is a single paragraph."
    path = create_temp_file(content)
    try:
        doc = extract_txt(path)
        assert len(doc.text_blocks) == 1
        assert doc.text_blocks[0].text == content
        assert doc.text_blocks[0].index == 0
        assert doc.source_format == "txt"
    finally:
        os.remove(path)

def test_extract_multiple_paragraphs():
    content = "Paragraph 1\n\nParagraph 2\nLine 2\n\nParagraph 3"
    path = create_temp_file(content)
    try:
        doc = extract_txt(path)
        assert len(doc.text_blocks) == 3
        assert doc.text_blocks[0].text == "Paragraph 1"
        assert doc.text_blocks[1].text == "Paragraph 2\nLine 2"
        assert doc.text_blocks[2].text == "Paragraph 3"
    finally:
        os.remove(path)

def test_extract_empty_lines():
    content = "\n\n\nParagraph 1\n\n\n\nParagraph 2\n\n"
    path = create_temp_file(content)
    try:
        doc = extract_txt(path)
        assert len(doc.text_blocks) == 2
        assert doc.text_blocks[0].text == "Paragraph 1"
        assert doc.text_blocks[1].text == "Paragraph 2"
    finally:
        os.remove(path)

def test_extract_unicode_text():
    content = "यह एक पैराग्राफ है।\n\nThis is another paragraph with emoji 😊."
    path = create_temp_file(content, encoding="utf-8-sig") # BOM encoding
    try:
        doc = extract_txt(path)
        assert len(doc.text_blocks) == 2
        assert "यह एक" in doc.text_blocks[0].text
        assert "emoji 😊" in doc.text_blocks[1].text
    finally:
        os.remove(path)

def test_extract_empty_file():
    path = create_temp_file("")
    try:
        doc = extract_txt(path)
        assert len(doc.text_blocks) == 0
    finally:
        os.remove(path)

def test_extract_missing_file():
    with pytest.raises(CIPAMError, match="File not found"):
        extract_txt("non_existent_file.txt")
