import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from groq import GroqError
from app.translation.translator import Translator
from app.exceptions import TranslationError, ConfigurationError

@pytest.fixture
def mock_groq_client():
    with patch("app.translation.translator.AsyncGroq") as mock:
        yield mock

@patch("app.translation.translator.GROQ_API_KEY", None)
def test_missing_api_key():
    with pytest.raises(ConfigurationError, match="Groq API key is missing"):
        Translator(api_key="")

@pytest.mark.asyncio
async def test_successful_translation(mock_groq_client):
    # Setup mock response
    mock_instance = mock_groq_client.return_value
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "नमस्ते दुनिया"
    
    # We must patch the AsyncGroq completions create method as async
    mock_create = AsyncMock(return_value=mock_response)
    mock_instance.chat.completions.create = mock_create

    translator = Translator(api_key="fake-key", model="fake-model")
    result = await translator.translate("Hello world", "Hindi")

    assert result == "नमस्ते दुनिया"
    mock_instance.chat.completions.create.assert_called_once()
    
    # Check if system prompt is constructed properly
    call_args = mock_instance.chat.completions.create.call_args[1]
    assert call_args["model"] == "fake-model"
    messages = call_args["messages"]
    assert len(messages) == 2
    assert "CIPAM/IPR" in messages[0]["content"]
    assert "Hindi" in messages[0]["content"]

@pytest.mark.asyncio
async def test_empty_translation():
    translator = Translator(api_key="fake-key")
    assert await translator.translate("   ", "Hindi") == ""

@pytest.mark.asyncio
async def test_translation_with_glossary(mock_groq_client):
    mock_instance = mock_groq_client.return_value
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "translated text"
    
    mock_create = AsyncMock(return_value=mock_response)
    mock_instance.chat.completions.create = mock_create

    translator = Translator(api_key="fake-key")
    await translator.translate("text", "Hindi", glossary={"Patent": "पेटेंट"})
    
    call_args = mock_instance.chat.completions.create.call_args[1]
    messages = call_args["messages"]
    system_prompt = messages[0]["content"]
    assert "Glossary" in system_prompt
    assert "Patent: पेटेंट" in system_prompt

@patch("app.translation.translator.Translator._async_call_groq")
@pytest.mark.asyncio
async def test_groq_api_error(mock_call_groq):
    # Testing that GroqError from internal call raises TranslationError
    mock_call_groq.side_effect = GroqError("API Error")
    
    translator = Translator(api_key="fake-key")
    with pytest.raises(TranslationError, match="Groq API call failed"):
        await translator.translate("text", "Hindi")
