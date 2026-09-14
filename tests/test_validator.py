from app.models import TranslationChunk, TranslationResult
from app.processing.validator import validate_translation

def test_valid_translation():
    chunks = [TranslationChunk(chunk_id="c0", source_text="Hello world")]
    results = [TranslationResult(chunk_id="c0", translated_text="नमस्ते दुनिया", target_language="hindi")]
    v = validate_translation(chunks, results)
    assert v.passed
    assert len(v.warnings) == 0

def test_empty_translation():
    chunks = [TranslationChunk(chunk_id="c0", source_text="Hello")]
    results = [TranslationResult(chunk_id="c0", translated_text="", target_language="hindi")]
    v = validate_translation(chunks, results)
    assert not v.passed
    assert any(w.rule == "empty_translation" for w in v.warnings)

def test_missing_chunk():
    chunks = [TranslationChunk(chunk_id="c0", source_text="Hello")]
    results = []
    v = validate_translation(chunks, results)
    assert not v.passed
    assert any(w.rule == "missing_chunk" for w in v.warnings)

def test_chunk_count_mismatch():
    chunks = [TranslationChunk(chunk_id="c0", source_text="Hello")]
    results = [
        TranslationResult(chunk_id="c0", translated_text="नमस्ते", target_language="hindi"),
        TranslationResult(chunk_id="c1", translated_text="दुनिया", target_language="hindi"),
    ]
    v = validate_translation(chunks, results)
    assert not v.passed
    assert any(w.rule == "chunk_count_mismatch" for w in v.warnings)

def test_missing_number():
    chunks = [TranslationChunk(chunk_id="c0", source_text="Article 123 of 2023")]
    results = [TranslationResult(chunk_id="c0", translated_text="अनुच्छेद का", target_language="hindi")]
    v = validate_translation(chunks, results)
    assert not v.passed
    assert any(w.rule == "missing_number" for w in v.warnings)

def test_suspiciously_short():
    chunks = [TranslationChunk(chunk_id="c0", source_text="This is a very long paragraph " * 10)]
    results = [TranslationResult(chunk_id="c0", translated_text="Short", target_language="hindi")]
    v = validate_translation(chunks, results)
    assert not v.passed
    assert any(w.rule == "suspiciously_short" for w in v.warnings)

def test_untranslated():
    chunks = [TranslationChunk(chunk_id="c0", source_text="Hello world")]
    results = [TranslationResult(chunk_id="c0", translated_text="Hello world", target_language="hindi")]
    v = validate_translation(chunks, results)
    assert not v.passed
    assert any(w.rule == "untranslated" for w in v.warnings)

def test_chunk_ordering():
    chunks = [
        TranslationChunk(chunk_id="c0", source_text="First"),
        TranslationChunk(chunk_id="c1", source_text="Second"),
    ]
    results = [
        TranslationResult(chunk_id="c1", translated_text="दूसरा", target_language="hindi"),
        TranslationResult(chunk_id="c0", translated_text="पहला", target_language="hindi"),
    ]
    v = validate_translation(chunks, results)
    assert not v.passed
    assert any(w.rule == "chunk_ordering" for w in v.warnings)
