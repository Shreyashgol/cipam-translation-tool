import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.pipeline import Pipeline
from app.models import Document, TextBlock
from app.exceptions import CIPAMError

@pytest.fixture
def mock_extract():
    with patch("app.pipeline.extract_document") as mock:
        doc = Document(source_filename="input.txt", source_format="txt")
        doc.text_blocks.append(TextBlock(text="Hello World 1", block_type="paragraph", index=0))
        doc.text_blocks.append(TextBlock(text="Hello World 2", block_type="paragraph", index=1))
        mock.return_value = doc
        yield mock

@pytest.fixture
def mock_translator():
    with patch("app.pipeline.Translator") as mock_cls:
        mock_instance = AsyncMock()
        mock_instance.translate_batch.return_value = [
            {"chunk_id": "chunk-0", "translated_text": "नमस्ते दुनिया 1", "target_language": "hindi"},
            {"chunk_id": "chunk-1", "translated_text": "नमस्ते दुनिया 2", "target_language": "hindi"}
        ]
        mock_cls.return_value = mock_instance
        yield mock_instance

def test_pipeline_end_to_end_txt(mock_extract, mock_translator, tmp_path):
    pipeline = Pipeline()
    
    with patch("app.pipeline.run_llm_validation", new_callable=AsyncMock) as mock_llm_judge:
        from app.processing.validator import ValidationResult
        mock_llm_judge.return_value = ValidationResult()
        
        output_path = pipeline.run("input.txt", "hindi", "txt", output_dir=str(tmp_path))
    
    assert os.path.exists(output_path)
    mock_extract.assert_called_once_with("input.txt")
    mock_translator.translate_batch.assert_called_once()
    
    with open(output_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "नमस्ते दुनिया 1" in content

def test_pipeline_output_collision(mock_extract, mock_translator, tmp_path):
    # Create the first output file so collision logic triggers
    original_output = tmp_path / "input_hindi.txt"
    original_output.write_text("old content")
    
    pipeline = Pipeline()
    
    with patch("app.pipeline.run_llm_validation", new_callable=AsyncMock) as mock_llm_judge:
        from app.processing.validator import ValidationResult
        mock_llm_judge.return_value = ValidationResult()
        
        output_path = pipeline.run("input.txt", "hindi", "txt", output_dir=str(tmp_path))
    
    assert "input_hindi_1.txt" in output_path
