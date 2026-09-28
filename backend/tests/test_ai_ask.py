from unittest.mock import patch
from datetime import timedelta
from app.services.gemini_service import GeminiAPIError, GeminiConfigurationError
from app.core.security import create_access_token

def register_and_login(client, name="Ask Student", email="askstudent@example.com", password="password123"):
    """Helper to register and login a test user, returning the access token."""
    client.post("/auth/register", json={
        "name": name,
        "email": email,
        "password": password
    })
    login_resp = client.post("/auth/login", json={
        "email": email,
        "password": password
    })
    return login_resp.json()["access_token"]

# 1 & 2: Authentication
def test_unauthenticated_ask_rejected(client):
    """Verify request without JWT returns 401."""
    resp = client.post("/ai/ask", json={"question": "What is virtual memory?"})
    assert resp.status_code == 401

def test_invalid_jwt_rejected(client):
    """Verify request with invalid JWT returns 401."""
    resp = client.post(
        "/ai/ask",
        json={"question": "What is virtual memory?"},
        headers={"Authorization": "Bearer bad.token.here"}
    )
    assert resp.status_code == 401

def test_expired_jwt_rejected(client):
    """Verify request with expired JWT returns 401."""
    expired_token = create_access_token(data={"sub": "1"}, expires_delta=timedelta(seconds=-10))
    resp = client.post(
        "/ai/ask",
        json={"question": "What is virtual memory?"},
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert resp.status_code == 401

# 3, 4, 5, 6, 7, 8: Validation
@patch("app.services.gemini_service.GeminiService.generate_text")
def test_valid_question_accepted(mock_gen, client):
    """Verify valid question is accepted and whitespace is trimmed."""
    token = register_and_login(client, "Q User", "quser@example.com")
    mock_gen.return_value = "Virtual memory maps virtual addresses to physical RAM."

    resp = client.post(
        "/ai/ask",
        json={"question": "   What is virtual memory?   "},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "Virtual memory" in data["answer"]

    # Verify trimmed question was passed to prompt
    prompt_sent = mock_gen.call_args[0][0]
    assert "What is virtual memory?" in prompt_sent
    assert "   What is virtual memory?   " not in prompt_sent

def test_empty_question_rejected(client):
    """Verify empty question string returns 422."""
    token = register_and_login(client, "Empty Q", "emptyq@example.com")
    resp = client.post(
        "/ai/ask",
        json={"question": ""},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 422

def test_whitespace_only_question_rejected(client):
    """Verify whitespace-only question returns 422."""
    token = register_and_login(client, "WS Q", "wsq@example.com")
    resp = client.post(
        "/ai/ask",
        json={"question": "     \n\t   "},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 422

def test_excessively_large_question_rejected(client):
    """Verify questions exceeding 2000 characters are rejected with 422."""
    token = register_and_login(client, "Large Q", "largeq@example.com")
    oversized = "Q" * 2001
    resp = client.post(
        "/ai/ask",
        json={"question": oversized},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 422

@patch("app.services.gemini_service.GeminiService.generate_text")
def test_optional_context_accepted(mock_gen, client):
    """Verify question with context is accepted and context is embedded."""
    token = register_and_login(client, "Ctx User", "ctxuser@example.com")
    mock_gen.return_value = "Inheritance enables code reuse."

    resp = client.post(
        "/ai/ask",
        json={
            "question": "Explain inheritance",
            "context": "Python OOP BCA exam preparation"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["answer"] == "Inheritance enables code reuse."

    prompt_sent = mock_gen.call_args[0][0]
    assert "Explain inheritance" in prompt_sent
    assert "Python OOP BCA exam preparation" in prompt_sent

def test_excessively_large_context_rejected(client):
    """Verify context exceeding 5000 characters is rejected with 422."""
    token = register_and_login(client, "Large Ctx", "largectx@example.com")
    oversized_ctx = "C" * 5001
    resp = client.post(
        "/ai/ask",
        json={"question": "What is SQL?", "context": oversized_ctx},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 422

# 9, 10, 11, 12: Gemini interaction
@patch("app.services.gemini_service.GeminiService.generate_text")
def test_gemini_interaction_and_response(mock_gen, client):
    """Verify prompt formatting and AskResponse output schema."""
    token = register_and_login(client, "Interaction User", "interact@example.com")
    mock_gen.return_value = "Deadlock occurs when processes hold resources while waiting for others."

    resp = client.post(
        "/ai/ask",
        json={"question": "What is a deadlock?", "context": "Operating Systems"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert data["answer"].startswith("Deadlock occurs")

# 13, 14, 15, 16: Error cases
@patch("app.services.gemini_service.GeminiService.generate_text")
def test_empty_gemini_response_handled(mock_gen, client):
    """Verify empty or whitespace response from AI returns 502 Bad Gateway."""
    token = register_and_login(client, "Empty AI User", "emptyaq@example.com")
    mock_gen.return_value = "   "

    resp = client.post(
        "/ai/ask",
        json={"question": "Explain recursion"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 502
    assert resp.json()["detail"] == "AI service returned an empty response."

@patch("app.services.gemini_service.GeminiService.generate_text")
def test_gemini_service_exception_handled(mock_gen, client):
    """Verify GeminiServiceError returns safe 503 without raw provider traces."""
    token = register_and_login(client, "Error User 2", "err2@example.com")
    mock_gen.side_effect = GeminiAPIError("google.api_core.exceptions.ResourceExhausted: 429 quota")

    resp = client.post(
        "/ai/ask",
        json={"question": "Explain quicksort"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 503
    assert resp.json()["detail"] == "AI service is temporarily unavailable. Please try again later."
    assert "google.api_core" not in resp.text

@patch("app.services.gemini_service.GeminiService.generate_text")
def test_missing_api_configuration_handled(mock_gen, client):
    """Verify missing API key returns safe 503 without leaking configuration details."""
    token = register_and_login(client, "Config Err User", "cfgerr@example.com")
    mock_gen.side_effect = GeminiConfigurationError("Missing GEMINI_API_KEY")

    resp = client.post(
        "/ai/ask",
        json={"question": "Explain trees"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 503
    assert resp.json()["detail"] == "AI service is temporarily unavailable. Please try again later."

# 17, 18, 19: Security
@patch("app.services.gemini_service.GeminiService.generate_text")
def test_api_key_and_token_never_exposed(mock_gen, client):
    """Verify secret API key and JWT tokens never leak into prompt or response."""
    token = register_and_login(client, "Sec Student", "secstudent@example.com")
    mock_gen.return_value = "Safe educational answer."

    resp = client.post(
        "/ai/ask",
        json={"question": "Explain TCP vs UDP"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert "AQ.Ab8RN" not in resp.text

    # Verify authorization bearer token was NOT passed to the Gemini prompt
    prompt_sent = mock_gen.call_args[0][0]
    assert token not in prompt_sent
    assert "Bearer" not in prompt_sent

def test_client_controlled_user_id_rejected(client):
    """Verify client sending user_id in payload is rejected by Pydantic extra='forbid'."""
    token = register_and_login(client, "Forbid Student", "forbid@example.com")
    resp = client.post(
        "/ai/ask",
        json={"question": "Explain hashing", "user_id": 999},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 422
