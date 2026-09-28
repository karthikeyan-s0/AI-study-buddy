from unittest.mock import patch
from app.services.gemini_service import GeminiAPIError

def register_and_login(client, name="AI Student", email="aistudent@example.com", password="password123"):
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

@patch("app.services.gemini_service.GeminiService.generate_json")
def test_authenticated_user_can_summarize_content(mock_gen, client):
    """Verify that an authenticated student can summarize study material."""
    token = register_and_login(client, "Reader", "reader@example.com")
    sample_text = (
        "Operating systems manage hardware resources. A process is a program in execution. "
        "Each process is represented in the operating system by a Process Control Block (PCB), "
        "which contains state, program counter, CPU registers, and scheduling information."
    )
    mock_gen.return_value = {
        "summary": "Operating systems manage hardware and execute processes tracked via Process Control Blocks.",
        "key_points": [
            "A process is a program in execution.",
            "The PCB contains crucial process state information."
        ],
        "important_terms": [
            "Process: A program in execution",
            "PCB: Process Control Block storing metadata"
        ]
    }

    resp = client.post("/ai/summarize", json={
        "content": sample_text,
        "summary_length": "medium"
    }, headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 200
    data = resp.json()
    assert "Operating systems" in data["summary"]
    assert len(data["key_points"]) == 2
    assert len(data["important_terms"]) == 2

    # Verify prompt received the sample text
    mock_gen.assert_called_once()
    prompt_arg = mock_gen.call_args[0][0]
    assert sample_text in prompt_arg
    assert "medium" in prompt_arg

def test_unauthenticated_summarize_rejected(client):
    """Verify unauthenticated POST /ai/summarize returns 401."""
    resp = client.post("/ai/summarize", json={"content": "Some study material here."})
    assert resp.status_code == 401

def test_empty_content_rejected(client):
    """Verify empty or short content is rejected with 422 Unprocessable Entity."""
    token = register_and_login(client, "Short Input", "short@example.com")

    # Empty string
    empty_resp = client.post("/ai/summarize", json={"content": ""}, headers={"Authorization": f"Bearer {token}"})
    assert empty_resp.status_code == 422

    # Whitespace only
    ws_resp = client.post("/ai/summarize", json={"content": "           "}, headers={"Authorization": f"Bearer {token}"})
    assert ws_resp.status_code == 422

    # Under minimum 10 characters
    too_short = client.post("/ai/summarize", json={"content": "Short"}, headers={"Authorization": f"Bearer {token}"})
    assert too_short.status_code == 422

def test_excessively_large_content_rejected(client):
    """Verify content exceeding maximum length limit (25,000 chars) is rejected with 422."""
    token = register_and_login(client, "Long Input", "long@example.com")
    huge_text = "A" * 26000

    resp = client.post("/ai/summarize", json={"content": huge_text}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 422

@patch("app.services.gemini_service.GeminiService.generate_json")
def test_empty_gemini_response_handled(mock_gen, client):
    """Verify handling when AI returns empty or non-dict structure."""
    token = register_and_login(client, "Empty AI", "empty_ai@example.com")
    mock_gen.return_value = {}  # missing "summary" key

    resp = client.post("/ai/summarize", json={
        "content": "This is legitimate study material that needs summarizing."
    }, headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 502
    assert "invalid summary structure" in resp.json()["detail"]

@patch("app.services.gemini_service.GeminiService.generate_json")
def test_gemini_failure_handled_safely(mock_gen, client):
    """Verify provider failure returns 503 without exposing secrets."""
    token = register_and_login(client, "Error User", "erroruser@example.com")
    mock_gen.side_effect = GeminiAPIError("Provider error 503")

    resp = client.post("/ai/summarize", json={
        "content": "This is legitimate study material that needs summarizing."
    }, headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 503
    assert "AI service temporarily unavailable" in resp.json()["detail"]

@patch("app.services.gemini_service.GeminiService.generate_json")
def test_api_key_never_exposed(mock_gen, client):
    """Verify that GEMINI_API_KEY does not appear in errors or responses."""
    token = register_and_login(client, "Key Leak Check", "keyleak@example.com")
    mock_gen.side_effect = Exception("Internal generic failure")

    resp = client.post("/ai/summarize", json={
        "content": "This is legitimate study material that needs summarizing."
    }, headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 503
    assert "AQ.Ab8RN" not in resp.text
    assert "secret" not in resp.text.lower()
