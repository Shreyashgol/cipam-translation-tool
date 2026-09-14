class CIPAMError(Exception):
    """Base exception for CIPAM Translation Tool."""
    pass

class ExtractionError(CIPAMError):
    """Error during text extraction."""
    pass

class TranslationError(CIPAMError):
    """Error during translation."""
    pass

class OutputError(CIPAMError):
    """Error during output generation."""
    pass

class ConfigurationError(CIPAMError):
    """Error in configuration (e.g. missing API key)."""
    pass
