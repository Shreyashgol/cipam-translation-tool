import os
import tempfile
from app.models import TranslationResult
from app.output.txt import write_txt
from app.exceptions import CIPAMError

def test_write_txt():
    results = [
        TranslationResult("chunk-1", "नमस्ते", "hindi"),
        TranslationResult("chunk-2", "दुनिया", "hindi")
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "output.txt")
        write_txt(results, output_path)
        
        assert os.path.exists(output_path)
        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        assert "नमस्ते\n\nदुनिया\n\n" == content
