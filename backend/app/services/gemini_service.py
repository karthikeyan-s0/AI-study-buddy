import json
import logging
from typing import Optional, Dict, Any
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

class GeminiServiceError(Exception):
    """Base exception for all Gemini AI service errors."""
    pass

class GeminiConfigurationError(GeminiServiceError):
    """Raised when Gemini configuration (e.g., API key) is missing or invalid."""
    pass

class GeminiAPIError(GeminiServiceError):
    """Raised when Gemini API returns an error or fails to respond."""
    pass

class GeminiService:
    """
    Reusable Gemini AI service layer.
    Communicates with the Google Gemini API using secure header authentication,
    enforcing clean error shielding to never expose secrets or raw provider traces.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL or "gemini-3.8-flash"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    def _get_headers(self) -> Dict[str, str]:
        if not self.api_key:
            raise GeminiConfigurationError("Gemini API key is not configured. Please set GEMINI_API_KEY.")
        return {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    FALLBACK_MODELS = [
        "gemini-3.5-flash-lite",
        "gemini-flash-lite-latest",
        "gemini-3.8-flash",
        "gemini-3.5-flash",
    ]

    def _get_candidate_models(self) -> list:
        candidates = []
        if self.model:
            candidates.append(self.model)
        for m in self.FALLBACK_MODELS:
            if m not in candidates:
                candidates.append(m)
        return candidates

    def generate_text(self, prompt: str, timeout: float = 60.0) -> str:
        """
        Send a text prompt to Gemini and return the generated text.
        Automatically falls back to alternate models if a model is unavailable or rate-limited.
        
        Args:
            prompt: Text prompt for generation.
            timeout: HTTP timeout in seconds (default 60.0s).
            
        Returns:
            Clean string output from the model.
        """
        if not prompt or not prompt.strip():
            raise GeminiAPIError("Prompt cannot be empty.")

        headers = self._get_headers()
        models = self._get_candidate_models()
        last_error = None

        for model in models:
            url = f"{self.base_url}/models/{model}:generateContent"
            payload = {
                "contents": [
                    {
                        "parts": [{"text": prompt}]
                    }
                ]
            }

            try:
                with httpx.Client(timeout=timeout) as client:
                    response = client.post(url, headers=headers, json=payload)
            except httpx.TimeoutException as e:
                logger.error("Gemini API call to model %s timed out after %s seconds", model, timeout)
                last_error = GeminiAPIError("AI service request timed out. Please try again.")
                continue
            except httpx.RequestError as e:
                logger.error("Network error communicating with Gemini API model %s: %s", model, type(e).__name__)
                last_error = GeminiAPIError("Unable to connect to AI service. Please check network connectivity.")
                continue

            if response.status_code == 200:
                try:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if not candidates:
                        raise GeminiAPIError("Empty response received from AI service.")
                    
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if not parts or not parts[0].get("text"):
                        raise GeminiAPIError("Empty content received from AI service.")
                    
                    self.model = model
                    return parts[0]["text"].strip()
                except (ValueError, KeyError, IndexError) as e:
                    logger.error("Failed to parse Gemini API response: %s", type(e).__name__)
                    last_error = GeminiAPIError("Malformed response received from AI service.")
                    continue
            else:
                logger.warning("Gemini model %s returned HTTP %s. Trying fallback model...", model, response.status_code)
                last_error = GeminiAPIError(f"AI service error (HTTP {response.status_code}). Please try again.")

        raise last_error or GeminiAPIError("AI service is temporarily unavailable. Please try again later.")

    def generate_json(self, prompt: str, timeout: float = 60.0) -> Any:
        """
        Send a prompt with structured JSON response expectation.
        Automatically falls back to alternate models if a model is unavailable or rate-limited.
        
        Args:
            prompt: Text prompt instructing JSON generation.
            timeout: HTTP timeout in seconds.
            
        Returns:
            Parsed JSON object (dict or list).
        """
        if not prompt or not prompt.strip():
            raise GeminiAPIError("Prompt cannot be empty.")

        headers = self._get_headers()
        models = self._get_candidate_models()
        last_error = None

        for model in models:
            url = f"{self.base_url}/models/{model}:generateContent"
            payload = {
                "contents": [
                    {
                        "parts": [{"text": prompt}]
                    }
                ],
                "generationConfig": {
                    "responseMimeType": "application/json"
                }
            }

            try:
                with httpx.Client(timeout=timeout) as client:
                    response = client.post(url, headers=headers, json=payload)
            except httpx.TimeoutException as e:
                logger.error("Gemini API call to model %s timed out after %s seconds", model, timeout)
                last_error = GeminiAPIError("AI service request timed out. Please try again.")
                continue
            except httpx.RequestError as e:
                logger.error("Network error communicating with Gemini API model %s: %s", model, type(e).__name__)
                last_error = GeminiAPIError("Unable to connect to AI service. Please check network connectivity.")
                continue

            if response.status_code == 200:
                try:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if not candidates:
                        raise GeminiAPIError("Empty response received from AI service.")
                    
                    raw_text = candidates[0].get("content", {}).get("parts", [])[0].get("text", "")
                    self.model = model
                    return json.loads(raw_text)
                except (ValueError, KeyError, IndexError) as e:
                    logger.error("Failed to parse JSON from Gemini response: %s", type(e).__name__)
                    last_error = GeminiAPIError("Failed to parse structured JSON from AI service.")
                    continue
            else:
                logger.warning("Gemini model %s returned HTTP %s. Trying fallback model...", model, response.status_code)
                last_error = GeminiAPIError(f"AI service error (HTTP {response.status_code}). Please try again.")

        raise last_error or GeminiAPIError("AI service is temporarily unavailable. Please try again later.")

# Module-level convenience functions
_default_service: Optional[GeminiService] = None

def get_gemini_service() -> GeminiService:
    global _default_service
    if _default_service is None:
        _default_service = GeminiService()
    return _default_service

def generate_text(prompt: str, timeout: float = 60.0) -> str:
    """Convenience helper to generate text using the default GeminiService instance."""
    return get_gemini_service().generate_text(prompt, timeout=timeout)
