from unittest.mock import patch
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt

def register_and_login(client, name="Quiz Student", email="quizstudent@example.com", password="password123"):
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

def create_subject(client, token, subject_name="Computer Networks"):
    """Helper to create a subject."""
    resp = client.post("/subjects", json={
        "name": subject_name,
        "description": "Networking basics",
        "difficulty": "medium",
        "exam_date": "2026-12-01"
    }, headers={"Authorization": f"Bearer {token}"})
    return resp.json()["id"]

MOCK_QUIZ_JSON = {
    "questions": [
        {
            "question": "Which layer of the OSI model does TCP operate on?",
            "options": {
                "A": "Network Layer",
                "B": "Transport Layer",
                "C": "Data Link Layer",
                "D": "Application Layer"
            },
            "correct_answer": "B",
            "explanation": "TCP operates at Layer 4, the Transport Layer."
        },
        {
            "question": "What is the primary purpose of ARP?",
            "options": {
                "A": "Resolve IP to MAC address",
                "B": "Route packets",
                "C": "Encrypt data",
                "D": "Assign IP dynamically"
            },
            "correct_answer": "A",
            "explanation": "ARP maps an IPv4 address to a physical MAC address."
        }
    ]
}

@patch("app.services.gemini_service.GeminiService.generate_json")
def test_generate_quiz_success(mock_gen, client):
    """Test generating a quiz with mocked Gemini."""
    token = register_and_login(client, "Quiz User 1", "quiz1@example.com")
    subject_id = create_subject(client, token)

    mock_gen.return_value = MOCK_QUIZ_JSON

    resp = client.post("/quizzes/generate", json={
        "subject_id": subject_id,
        "topic": "TCP/IP Protocol",
        "difficulty": "medium",
        "number_of_questions": 2
    }, headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["subject_id"] == subject_id
    assert data["topic"] == "TCP/IP Protocol"
    assert data["difficulty"] == "medium"
    assert len(data["questions_json"]) == 2
    assert data["questions_json"][0]["question"] == "Which layer of the OSI model does TCP operate on?"

@patch("app.services.gemini_service.GeminiService.generate_json")
def test_submit_quiz_deterministic_scoring(mock_gen, client):
    """Test deterministic scoring of quiz attempts."""
    token = register_and_login(client, "Scorer", "scorer@example.com")
    subject_id = create_subject(client, token)

    mock_gen.return_value = MOCK_QUIZ_JSON

    gen_resp = client.post("/quizzes/generate", json={
        "subject_id": subject_id,
        "topic": "TCP/IP Protocol",
        "difficulty": "medium",
        "number_of_questions": 2
    }, headers={"Authorization": f"Bearer {token}"})
    assert gen_resp.status_code == 201
    quiz_id = gen_resp.json()["id"]

    # Submit 1 correct, 1 incorrect ("0": "B" is correct, "1": "C" is incorrect)
    submit_resp = client.post(f"/quizzes/{quiz_id}/submit", json={
        "answers": {
            "0": "B",
            "1": "C"
        }
    }, headers={"Authorization": f"Bearer {token}"})

    assert submit_resp.status_code == 200
    res = submit_resp.json()
    assert res["quiz_id"] == quiz_id
    assert res["score"] == 1
    assert res["total_questions"] == 2
    assert res["percentage"] == 50.0
    assert len(res["feedback"]) == 2
    assert res["feedback"][0]["is_correct"] is True
    assert res["feedback"][1]["is_correct"] is False
    assert res["feedback"][1]["correct_answer"] == "A"

    # Submit 100% correct ("0": "B", "1": "A")
    submit_resp2 = client.post(f"/quizzes/{quiz_id}/submit", json={
        "answers": {
            "0": "B",
            "1": "A"
        }
    }, headers={"Authorization": f"Bearer {token}"})

    assert submit_resp2.status_code == 200
    res2 = submit_resp2.json()
    assert res2["score"] == 2
    assert res2["percentage"] == 100.0

@patch("app.services.gemini_service.GeminiService.generate_json")
def test_quiz_attempts_history(mock_gen, client):
    """Test retrieving quiz attempt history."""
    token = register_and_login(client, "Historian", "historian@example.com")
    subject_id = create_subject(client, token)

    mock_gen.return_value = MOCK_QUIZ_JSON

    gen_resp = client.post("/quizzes/generate", json={
        "subject_id": subject_id,
        "topic": "TCP/IP Protocol",
        "difficulty": "medium",
        "number_of_questions": 2
    }, headers={"Authorization": f"Bearer {token}"})
    assert gen_resp.status_code == 201
    quiz_id = gen_resp.json()["id"]

    # Submit an attempt
    client.post(f"/quizzes/{quiz_id}/submit", json={
        "answers": {"0": "B", "1": "A"}
    }, headers={"Authorization": f"Bearer {token}"})

    # Get attempts
    att_resp = client.get(f"/quizzes/{quiz_id}/attempts", headers={"Authorization": f"Bearer {token}"})
    assert att_resp.status_code == 200
    attempts = att_resp.json()
    assert len(attempts) == 1
    assert attempts[0]["score"] == 2
    assert attempts[0]["percentage"] == 100.0

@patch("app.services.gemini_service.GeminiService.generate_json")
def test_quiz_tenant_isolation(mock_gen, client):
    """Ensure a student cannot generate a quiz for another student's subject."""
    token1 = register_and_login(client, "User One", "user1@example.com")
    token2 = register_and_login(client, "User Two", "user2@example.com")
    subject_id1 = create_subject(client, token1)

    mock_gen.return_value = MOCK_QUIZ_JSON

    # User 2 tries to generate quiz for User 1's subject
    resp = client.post("/quizzes/generate", json={
        "subject_id": subject_id1,
        "topic": "TCP/IP Protocol",
        "difficulty": "medium",
        "number_of_questions": 2
    }, headers={"Authorization": f"Bearer {token2}"})

    assert resp.status_code == 404
