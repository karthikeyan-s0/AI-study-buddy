from unittest.mock import patch, MagicMock
import pytest
import httpx

from app.services.gemini_service import (
    GeminiService,
    GeminiConfigurationError,
    GeminiAPIError,
)

def test_missing_api_key_handled():
    """Verify that GeminiConfigurationError is raised when API key is missing."""
    service = GeminiService(api_key="")
    with pytest.raises(GeminiConfigurationError) as exc_info:
        service.generate_text("Hello")
    assert "Gemini API key is not configured" in str(exc_info.value)

def test_empty_prompt_rejected():
    """Verify that an empty or whitespace prompt raises GeminiAPIError."""
    service = GeminiService(api_key="mock_key")
    with pytest.raises(GeminiAPIError) as exc_info:
        service.generate_text("   ")
    assert "Prompt cannot be empty" in str(exc_info.value)

@patch("httpx.Client.post")
def test_successful_prompt_generation(mock_post):
    """Verify successful generation flow and payload inspection with mocked response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": "Processes are running instances of programs."}]
                }
            }
        ]
    }
    mock_post.return_value = mock_response

    service = GeminiService(api_key="mock_secret_key_12345", model="gemini-3.8-flash")
    result = service.generate_text("Explain processes")

    # Assert clean text response returned
    assert result == "Processes are running instances of programs."

    # Assert prompt and headers passed correctly
    mock_post.assert_called_once()
    called_args, called_kwargs = mock_post.call_args
    assert "models/gemini-3.8-flash:generateContent" in called_args[0]
    assert called_kwargs["headers"]["x-goog-api-key"] == "mock_secret_key_12345"
    assert called_kwargs["json"]["contents"][0]["parts"][0]["text"] == "Explain processes"

@patch("httpx.Client.post")
def test_empty_response_handled(mock_post):
    """Verify handling when Gemini API returns empty candidates list."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"candidates": []}
    mock_post.return_value = mock_response

    service = GeminiService(api_key="mock_key")
    with pytest.raises(GeminiAPIError) as exc_info:
        service.generate_text("Hello")
    assert "Empty response received" in str(exc_info.value)

@patch("httpx.Client.post")
def test_gemini_http_error_handled(mock_post):
    """Verify handling when Gemini API returns 500 error."""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_post.return_value = mock_response

    service = GeminiService(api_key="mock_key")
    with pytest.raises(GeminiAPIError) as exc_info:
        service.generate_text("Hello")
    assert "AI service error (HTTP 500)" in str(exc_info.value)

@patch("httpx.Client.post")
def test_gemini_timeout_handled(mock_post):
    """Verify timeout exception is converted to clean user-friendly message."""
    mock_post.side_effect = httpx.TimeoutException("Read timed out")

    service = GeminiService(api_key="mock_key")
    with pytest.raises(GeminiAPIError) as exc_info:
        service.generate_text("Explain scheduling")
    assert "AI service request timed out" in str(exc_info.value)

@patch("httpx.Client.post")
def test_gemini_network_error_handled(mock_post):
    """Verify network connection error is cleanly caught."""
    mock_post.side_effect = httpx.ConnectError("Failed to connect")

    service = GeminiService(api_key="mock_key")
    with pytest.raises(GeminiAPIError) as exc_info:
        service.generate_text("Explain memory management")
    assert "Unable to connect to AI service" in str(exc_info.value)

@patch("httpx.Client.post")
def test_api_key_never_appears_in_errors(mock_post):
    """Verify that private API keys are never included in error strings."""
    secret_key = "sensitive_production_gemini_key_9999"
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_post.return_value = mock_response

    service = GeminiService(api_key=secret_key)
    with pytest.raises(GeminiAPIError) as exc_info:
        service.generate_text("Hello")
    
    error_message = str(exc_info.value)
    assert secret_key not in error_message
    assert "AI service error (HTTP 403)" in error_message

@patch("httpx.Client.post")
def test_successful_json_generation(mock_post):
    """Verify generate_json returns parsed structured data."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": '{"topics": ["P1", "P2"], "estimated_days": 5}'}]
                }
            }
        ]
    }
    mock_post.return_value = mock_response

    service = GeminiService(api_key="mock_key")
    data = service.generate_json("Generate JSON schedule")
    assert isinstance(data, dict)
    assert data["topics"] == ["P1", "P2"]
    assert data["estimated_days"] == 5
