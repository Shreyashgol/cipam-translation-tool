import re

def clean_text(text: str) -> str:
    """Normalize unnecessary whitespace."""
    # Replace multiple spaces/tabs with single space
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()
