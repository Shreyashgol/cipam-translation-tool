import re
import asyncio
from dataclasses import dataclass, field
from typing import List, Optional
from app.models import TranslationChunk, TranslationResult

@dataclass
class ValidationWarning:
    chunk_id: str
    rule: str
    message: str

@dataclass
class ValidationResult:
    passed: bool = True
    warnings: List[ValidationWarning] = field(default_factory=list)

    def add_warning(self, chunk_id: str, rule: str, message: str):
        self.warnings.append(ValidationWarning(chunk_id=chunk_id, rule=rule, message=message))
        self.passed = False

def validate_translation(
    chunks: List[TranslationChunk],
    results: List[TranslationResult]
) -> ValidationResult:
    validation = ValidationResult()

    # 1. Source/translation chunk count mismatch
    if len(chunks) != len(results):
        validation.add_warning(
            chunk_id="all",
            rule="chunk_count_mismatch",
            message=f"Expected {len(chunks)} translated chunks, got {len(results)}"
        )

    # Build lookup for results by chunk_id
    result_map = {r.chunk_id: r for r in results}

    for chunk in chunks:
        result = result_map.get(chunk.chunk_id)

        # 2. Missing chunks
        if result is None:
            validation.add_warning(
                chunk_id=chunk.chunk_id,
                rule="missing_chunk",
                message=f"Chunk '{chunk.chunk_id}' has no translation result"
            )
            continue

        # 3. Empty translation
        if not result.translated_text or not result.translated_text.strip():
            validation.add_warning(
                chunk_id=chunk.chunk_id,
                rule="empty_translation",
                message=f"Chunk '{chunk.chunk_id}' has an empty translation"
            )
            continue

        # 4. Source numbers missing from translation
        source_numbers = re.findall(r'\d+', chunk.source_text)
        for num in source_numbers:
            if num not in result.translated_text:
                validation.add_warning(
                    chunk_id=chunk.chunk_id,
                    rule="missing_number",
                    message=f"Chunk '{chunk.chunk_id}' contains '{num}' in source but not in translation"
                )

        # 5. Suspiciously short translation (less than 20% of source length)
        if len(result.translated_text.strip()) < len(chunk.source_text.strip()) * 0.2:
            validation.add_warning(
                chunk_id=chunk.chunk_id,
                rule="suspiciously_short",
                message=f"Chunk '{chunk.chunk_id}' translation is suspiciously short ({len(result.translated_text)} chars vs {len(chunk.source_text)} source chars)"
            )

        # 6. Completely untranslated (source == translation)
        if chunk.source_text.strip() == result.translated_text.strip():
            validation.add_warning(
                chunk_id=chunk.chunk_id,
                rule="untranslated",
                message=f"Chunk '{chunk.chunk_id}' appears to be completely untranslated"
            )

    # 7. Chunk ordering check
    expected_ids = [c.chunk_id for c in chunks]
    actual_ids = [r.chunk_id for r in results]
    if actual_ids != expected_ids and len(actual_ids) == len(expected_ids):
        validation.add_warning(
            chunk_id="all",
            rule="chunk_ordering",
            message="Translation results are not in the expected chunk order"
        )

    return validation

async def run_llm_validation(
    chunks: List[TranslationChunk], 
    results: List[TranslationResult], 
    translator, 
    target_language: str, 
    glossary: Optional[dict] = None, 
    max_concurrency: int = 5
) -> ValidationResult:
    """Uses the LLM to judge translation terminology and flow."""
    validation = ValidationResult()
    result_map = {r.chunk_id: r for r in results}
    semaphore = asyncio.Semaphore(max_concurrency)
    
    async def _validate_chunk(chunk):
        result = result_map.get(chunk.chunk_id)
        if not result or not result.translated_text:
            return None
            
        system_prompt = (
            f"You are an expert IPR terminology evaluator. "
            f"Review this translation from English to {target_language}.\n"
            f"If there is a severe terminology mismatch, grammatical error, or it loses critical meaning, reply exactly with 'FAIL: <reason>'.\n"
            f"Otherwise, reply exactly with 'PASS'."
        )
        
        if glossary:
            system_prompt += "\n\nGlossary that MUST be followed:\n"
            for eng, trans in glossary.items():
                system_prompt += f"- {eng}: {trans}\n"
                
        prompt = f"Source:\n{chunk.source_text}\n\nTranslation:\n{result.translated_text}"
        
        async with semaphore:
            try:
                res = await translator._async_call_groq(system_prompt, prompt)
                if res.startswith("FAIL"):
                    return ValidationWarning(chunk.chunk_id, "llm_judge_fail", res)
            except Exception as e:
                return ValidationWarning(chunk.chunk_id, "llm_judge_error", f"Judge API error: {e}")
        return None

    tasks = [_validate_chunk(chunk) for chunk in chunks]
    warnings = await asyncio.gather(*tasks)
    
    for w in warnings:
        if w:
            validation.warnings.append(w)
            validation.passed = False
            
    return validation
