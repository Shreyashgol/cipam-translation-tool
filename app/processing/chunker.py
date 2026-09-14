import re
from typing import List
from app.models import Document, TranslationChunk
from app.processing.cleaner import clean_text

def split_into_sentences(text: str) -> List[str]:
    # Basic sentence splitter prioritizing punctuation followed by space
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def chunk_document(doc: Document, max_chars: int = 1000) -> List[TranslationChunk]:
    chunks = []
    current_chunk_text = ""
    current_chunk_blocks = []
    chunk_index = 0

    def add_chunk():
        nonlocal current_chunk_text, current_chunk_blocks, chunk_index
        if current_chunk_text:
            chunks.append(TranslationChunk(
                chunk_id=f"chunk-{chunk_index}",
                source_text=current_chunk_text,
                metadata={"blocks": current_chunk_blocks}
            ))
            chunk_index += 1
            current_chunk_text = ""
            current_chunk_blocks = []

    for block in doc.text_blocks:
        text = clean_text(block.text)
        if not text:
            continue
            
        if len(text) > max_chars:
            # If we already have something in the current chunk, save it
            if current_chunk_text:
                add_chunk()
                
            # Split long paragraph by sentences
            sentences = split_into_sentences(text)
            for sentence in sentences:
                if len(current_chunk_text) + len(sentence) + 1 > max_chars and current_chunk_text:
                    add_chunk()
                
                if current_chunk_text:
                    current_chunk_text += " " + sentence
                else:
                    current_chunk_text = sentence
                
                if block.index not in current_chunk_blocks:
                    current_chunk_blocks.append(block.index)
        else:
            # Normal size paragraph
            if current_chunk_text and (len(current_chunk_text) + len(text) + 2 > max_chars):
                add_chunk()
            
            if current_chunk_text:
                current_chunk_text += "\n\n" + text
            else:
                current_chunk_text = text
            current_chunk_blocks.append(block.index)
            
    if current_chunk_text:
        add_chunk()
        
    return chunks
