import os
import logging
import asyncio
from groq import AsyncGroq, GroqError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import GROQ_API_KEY, GROQ_MODEL
from app.exceptions import CIPAMError, TranslationError, ConfigurationError
from app.translation.prompts import build_system_prompt

logger = logging.getLogger(__name__)

class Translator:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or GROQ_API_KEY
        if not self.api_key:
            raise ConfigurationError("Groq API key is missing. Please set GROQ_API_KEY in .env file.")
        self.model = model or GROQ_MODEL
        try:
            self.client = AsyncGroq(api_key=self.api_key)
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize Groq client: {e}")

    def _call_groq(self, system_prompt: str, text: str):
        # We handle retry at the batch level to wrap async functions if needed,
        # but since tenacity supports async natively we can just make this async.
        pass

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(GroqError),
        reraise=True
    )
    async def _async_call_groq(self, system_prompt: str, text: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                model=self.model,
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise TranslationError(f"Unexpected error during translation: {e}")

    async def translate(self, text: str, target_language: str, glossary: dict = None) -> str:
        if not text.strip():
            return ""

        system_prompt = build_system_prompt(target_language)
        
        if glossary:
            glossary_str = "\n\nGlossary (Use these specific translations):\n"
            for eng, trans in glossary.items():
                glossary_str += f"- {eng}: {trans}\n"
            system_prompt += glossary_str

        try:
            return await self._async_call_groq(system_prompt, text)
        except GroqError as e:
            error_type = type(e).__name__
            if "RateLimit" in error_type:
                raise TranslationError(f"Groq API rate limit exceeded. Please wait and try again. Details: {e}")
            elif "Timeout" in error_type:
                raise TranslationError("Groq API request timed out. Please try again.")
            elif "Authentication" in error_type:
                raise ConfigurationError("Groq API authentication failed. Check your API key.")
            raise TranslationError(f"Groq API call failed after retries: {error_type} - {e}")

    async def translate_batch(self, chunks: list, target_language: str, glossary: dict = None, max_concurrency: int = 5):
        """Translates a batch of chunks concurrently."""
        semaphore = asyncio.Semaphore(max_concurrency)
        
        async def _translate_chunk(chunk):
            async with semaphore:
                translated_text = await self.translate(chunk.source_text, target_language, glossary)
                return {
                    "chunk_id": chunk.chunk_id,
                    "translated_text": translated_text,
                    "target_language": target_language.lower()
                }

        tasks = [_translate_chunk(chunk) for chunk in chunks]
        results = await asyncio.gather(*tasks)
        return results
