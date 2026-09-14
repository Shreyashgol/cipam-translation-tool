from app.models import Document, TextBlock
from app.processing.chunker import chunk_document
from app.processing.cleaner import clean_text

def test_cleaner():
    assert clean_text("  hello   world  ") == "hello world"
    assert clean_text("a \t b") == "a b"

def test_chunk_short_document():
    doc = Document(source_filename="test", source_format="txt")
    doc.text_blocks.append(TextBlock(text="Paragraph 1", block_type="paragraph", index=0))
    doc.text_blocks.append(TextBlock(text="Paragraph 2", block_type="paragraph", index=1))
    
    chunks = chunk_document(doc, max_chars=100)
    assert len(chunks) == 1
    assert chunks[0].source_text == "Paragraph 1\n\nParagraph 2"
    assert chunks[0].metadata["blocks"] == [0, 1]

def test_chunk_long_document():
    doc = Document(source_filename="test", source_format="txt")
    doc.text_blocks.append(TextBlock(text="P1 is long. " * 10, block_type="paragraph", index=0)) # 120 chars
    doc.text_blocks.append(TextBlock(text="P2 is long. " * 10, block_type="paragraph", index=1)) # 120 chars
    
    chunks = chunk_document(doc, max_chars=200)
    assert len(chunks) == 2
    assert "P1" in chunks[0].source_text
    assert "P2" in chunks[1].source_text

def test_chunk_very_long_paragraph():
    doc = Document(source_filename="test", source_format="txt")
    text = "Sentence one. Sentence two. Sentence three. Sentence four."
    doc.text_blocks.append(TextBlock(text=text, block_type="paragraph", index=0))
    
    chunks = chunk_document(doc, max_chars=35)
    assert len(chunks) > 1
    assert "Sentence one." in chunks[0].source_text

def test_chunk_empty_document():
    doc = Document(source_filename="test", source_format="txt")
    chunks = chunk_document(doc)
    assert len(chunks) == 0
