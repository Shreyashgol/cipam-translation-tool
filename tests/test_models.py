from app.models import TextBlock, Document, TranslationChunk, TranslationResult

def test_text_block_creation():
    block = TextBlock(text="Hello", block_type="paragraph", index=0)
    assert block.text == "Hello"
    assert block.block_type == "paragraph"
    assert block.index == 0
    assert block.page_number is None

def test_document_creation():
    doc = Document(source_filename="test.txt", source_format="txt")
    assert doc.source_filename == "test.txt"
    assert doc.source_format == "txt"
    assert len(doc.text_blocks) == 0

    block = TextBlock(text="Hello", block_type="paragraph", index=0)
    doc.text_blocks.append(block)
    assert len(doc.text_blocks) == 1

def test_translation_chunk():
    chunk = TranslationChunk(chunk_id="chunk-1", source_text="Hello world")
    assert chunk.chunk_id == "chunk-1"
    assert chunk.source_text == "Hello world"
    assert chunk.metadata == {}

def test_translation_result():
    result = TranslationResult(chunk_id="chunk-1", translated_text="Namaste duniya", target_language="hindi")
    assert result.chunk_id == "chunk-1"
    assert result.translated_text == "Namaste duniya"
    assert result.target_language == "hindi"
