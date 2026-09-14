# CIPAM Translation Tool

## Problem Statement
The Cell for IPR Promotion and Management (CIPAM) frequently deals with intellectual property documents (patents, trademarks, copyrights) that need to be made accessible in regional Indian languages. Manual translation is slow, expensive, and often struggles with highly specialized legal and technical terminology.

## Objective
To build a meaning-preserving, context-aware translation pipeline using Large Language Models (LLMs) that translates English IPR documents into regional Indian languages while strictly adhering to an official glossary of IPR terms.

## Features
- **Context-Aware Translation**: Uses advanced LLMs (Groq) for highly contextual translations instead of literal word-for-word replacement.
- **Terminology Guidance**: Injects an official IPR glossary to guarantee consistency for specialized legal terms.
- **Intelligent Chunking**: Splits large documents semantically while preserving paragraph structure, preventing translation timeouts and context loss.
- **Multi-Format Extraction**: Natively extracts text from TXT, PDF, DOCX, and images (OCR).
- **Deterministic Validation**: Runs post-translation checks to detect empty results, missing numbers, suspiciously short outputs, and missing chunks.
- **Interactive CLI**: Beautiful, terminal-based user interface built with Rich and Typer.

## Supported Formats
### Input Formats
- `.txt` (Plain text)
- `.pdf` (Portable Document Format)
- `.docx` (Microsoft Word)
- `.png`, `.jpg`, `.jpeg` (Images via OCR)

### Output Formats
- `.txt` (Plain text)
- `.docx` (Microsoft Word)

## Supported Languages
English to:
- Hindi
- Marathi
- Bengali
- Gujarati
- Tamil
- Telugu

## Architecture
```
[Input Document (TXT/PDF/DOCX/IMG)]
        │
        ▼
[Extration Layer (PyMuPDF/docx/Tesseract)] ──► Output: Unified Document Model
        │
        ▼
[Processing Layer (Semantic Chunker)] ──► Splits by max chars/paragraphs
        │
        ▼
[Translation Layer (Groq API + Glossary)] ──► Context-aware translation
        │
        ▼
[Validation Layer (Deterministic Checks)] ──► Output: Warnings if issues found
        │
        ▼
[Output Layer (TXT/DOCX Generator)] ──► Translated Document
```

## Technology Stack
- **Language**: Python 3.9+
- **CLI Framework**: Typer, Rich
- **LLM Integration**: Groq API (llama3-70b-8192 / mixtral-8x7b-32768)
- **Document Processing**: PyMuPDF (fitz), python-docx
- **OCR**: pytesseract, Pillow (PIL)
- **Testing**: pytest

## Project Structure
```text
cipam-translator/
├── app/
│   ├── extractors/     # Parsers for PDF, DOCX, TXT, Images
│   ├── processing/     # Chunking and Validation logic
│   ├── translation/    # Groq integration, Prompts, Glossary
│   ├── output/         # TXT and DOCX generators
│   ├── cli.py          # Command Line Interface (Typer/Rich)
│   ├── pipeline.py     # Main orchestration pipeline
│   ├── models.py       # Dataclasses
│   ├── config.py       # Environment variables
│   └── exceptions.py   # Custom error handling
├── tests/              # Pytest test suite (51 tests)
├── .env                # API Keys
├── pyproject.toml      # Dependencies & Build config
└── README.md
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Shreyashgol/cipam-translation-tool.git
   cd cipam-translator
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -e .
   ```

## Tesseract OCR Requirements
For image processing (PNG/JPG), Tesseract OCR must be installed on your system.
- **macOS**: `brew install tesseract`
- **Linux (Ubuntu/Debian)**: `sudo apt-get install tesseract-ocr`
- **Windows**: Download installer from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) and add to PATH.

## Configuration
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama3-70b-8192
```

## Usage

### Interactive Mode
Simply run the tool without arguments for an interactive, menu-driven experience:
```bash
cipam
```

### Command-Line Mode
For automation or scripting, use the `translate` command:
```bash
cipam translate document.pdf --to hindi --format docx
```

### List Supported Languages
```bash
cipam languages
```

## Error Handling
The application features robust error handling for common issues:
- Missing files or unsupported formats.
- API keys missing or invalid (`ConfigurationError`).
- Rate limits and timeouts (`TranslationError`).
- File output collisions (automatically appends counter to filename).

## Testing
The project includes a comprehensive test suite (51 tests) covering unit tests and end-to-end mocked integration tests.
```bash
pytest tests/
```

## Limitations
- **Perfection**: LLMs provide highly contextual translations, but they are not guaranteed to be 100% perfect. A human-in-the-loop review is recommended for legally binding documents.
- **OCR Quality**: Image extraction depends heavily on the source image resolution and clarity.

## Future Improvements
- **LLM-Based Quality Checker**: Add a secondary LLM pass (LLM-as-a-judge) to review the initial translation for fluency and accuracy.
- **Advanced Layout Preservation**: Currently, paragraph order is preserved. Future versions could preserve complex PDF/DOCX layouts (tables, columns, exact text coordinates).
- **Batch Processing**: Allow a directory of documents to be processed asynchronously.
