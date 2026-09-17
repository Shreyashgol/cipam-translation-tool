from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class TextBlock:
    text: str
    block_type: str  # e.g., 'paragraph', 'heading', 'list_item'
    index: int
    page_number: Optional[int] = None

@dataclass
class Document:
    source_filename: str
    source_format: str
    text_blocks: List[TextBlock] = field(default_factory=list)

@dataclass
class TranslationChunk:
    chunk_id: str
    source_text: str
    metadata: dict = field(default_factory=dict)

@dataclass
class TranslationResult:
    chunk_id: str
    translated_text: str
    target_language: str

# Data models for document translation workflow
