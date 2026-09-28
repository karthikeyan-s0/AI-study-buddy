from unittest.mock import patch

def register_and_login(client, name="Dash Student", email="dashstudent@example.com", password="password123"):
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

def test_dashboard_empty_initial_state(client):
    """A fresh user with no subjects should get a clean dashboard with zeroed stats."""
    token = register_and_login(client, "Fresh Student", "fresh@example.com")
    resp = client.get("/dashboard", headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["student"]["email"] == "fresh@example.com"
    assert data["overall_progress"] == 0.0
    assert data["total_subjects"] == 0 if "total_subjects" in data else True
    assert data["subjects"] == []
    assert data["upcoming_exams"] == []
    assert data["recent_quiz_attempts"] == []

@patch("app.services.gemini_service.GeminiService.generate_json")
def test_dashboard_populated_state(mock_gen, client):
    """User with subjects, topics, progress, and quizzes gets aggregated stats."""
    token = register_and_login(client, "Active Student", "active@example.com")

    # 1. Create Subject with upcoming exam
    s_resp = client.post("/subjects", json={
        "name": "Software Engineering",
        "description": "Design patterns and SDLC",
        "difficulty": "medium",
        "exam_date": "2026-12-15"
    }, headers={"Authorization": f"Bearer {token}"})
    assert s_resp.status_code == 201
    subject_id = s_resp.json()["id"]

    # 2. Create 2 topics
    t1_resp = client.post(f"/subjects/{subject_id}/topics", json={
        "name": "Design Patterns",
        "difficulty": "medium",
        "status": "completed"
    }, headers={"Authorization": f"Bearer {token}"})
    assert t1_resp.status_code == 201
    t1_id = t1_resp.json()["id"]

    t2_resp = client.post(f"/subjects/{subject_id}/topics", json={
        "name": "Agile Methodologies",
        "difficulty": "easy",
        "status": "not_started"
    }, headers={"Authorization": f"Bearer {token}"})
    assert t2_resp.status_code == 201
    t2_id = t2_resp.json()["id"]

    # 3. Add progress for topic 1 (100%, 60 min)
    client.post("/progress", json={
        "subject_id": subject_id,
        "topic_id": t1_id,
        "completion_percentage": 100.0,
        "study_minutes": 60
    }, headers={"Authorization": f"Bearer {token}"})

    # 4. Generate quiz & submit attempt
    mock_gen.return_value = {
        "questions": [
            {
                "question": "What pattern category is Singleton?",
                "options": {
                    "A": "Creational",
                    "B": "Structural",
                    "C": "Behavioral",
                    "D": "Architectural"
                },
                "correct_answer": "A",
                "explanation": "Singleton is a creational design pattern."
            }
        ]
    }
    q_resp = client.post("/quizzes/generate", json={
        "subject_id": subject_id,
        "topic": "Design Patterns",
        "difficulty": "medium",
        "number_of_questions": 1
    }, headers={"Authorization": f"Bearer {token}"})
    assert q_resp.status_code == 201
    quiz_id = q_resp.json()["id"]

    # Submit quiz (100% correct: "0": "A")
    client.post(f"/quizzes/{quiz_id}/submit", json={
        "answers": {"0": "A"}
    }, headers={"Authorization": f"Bearer {token}"})

    # 5. Fetch Dashboard
    resp = client.get("/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()

    assert data["overall_progress"] == 50.0
    assert len(data["subjects"]) == 1
    assert data["subjects"][0]["progress_percentage"] == 50.0
    assert len(data["upcoming_exams"]) == 1
    assert data["upcoming_exams"][0]["name"] == "Software Engineering"
    assert len(data["recent_quiz_attempts"]) == 1
    assert data["recent_quiz_attempts"][0]["percentage"] == 100.0
    assert any("Design Patterns" in item for item in data["strong_topics"])
