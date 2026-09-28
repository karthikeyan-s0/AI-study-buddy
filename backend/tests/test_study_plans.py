from unittest.mock import patch
from app.models.study_plan import StudyPlan
from app.services.gemini_service import GeminiAPIError

def register_and_login(client, name="Plan Student", email="planstudent@example.com", password="password123"):
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

def create_subject_with_topics(client, token, subject_name="Operating Systems"):
    """Helper to create a subject with two topics."""
    s_resp = client.post("/subjects", json={
        "name": subject_name,
        "description": "OS principles",
        "difficulty": "hard",
        "exam_date": "2026-11-20"
    }, headers={"Authorization": f"Bearer {token}"})
    subject_id = s_resp.json()["id"]

    client.post(f"/subjects/{subject_id}/topics", json={"name": "Processes", "difficulty": "medium", "status": "completed"}, headers={"Authorization": f"Bearer {token}"})
    client.post(f"/subjects/{subject_id}/topics", json={"name": "Deadlocks", "difficulty": "hard", "status": "not_started"}, headers={"Authorization": f"Bearer {token}"})
    return subject_id

@patch("app.services.gemini_service.GeminiService.generate_json")
def test_authenticated_user_can_generate_plan(mock_gen, client, db_session):
    """Verify end-to-end study plan generation, validation, and database storage."""
    token = register_and_login(client, "Planner", "planner@example.com")
    subject_id = create_subject_with_topics(client, token, "Operating Systems")

    mock_plan = {
        "title": "OS Mastery 7-Day Plan",
        "summary": "Focus heavily on Deadlocks while revising Processes.",
        "days": [
            {
                "day": 1,
                "date": "2026-10-01",
                "topics": [
                    {
                        "topic": "Deadlocks",
                        "duration_minutes": 90,
                        "activities": ["Study Banker's algorithm", "Deadlock detection"]
                    }
                ]
            }
        ]
    }
    mock_gen.return_value = mock_plan

    resp = client.post("/study-plans/generate", json={
        "subject_id": subject_id,
        "start_date": "2026-10-01",
        "end_date": "2026-10-07"
    }, headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "OS Mastery 7-Day Plan"
    assert data["subject_id"] == subject_id
    assert "id" in data
    assert data["plan_json"]["days"][0]["topics"][0]["topic"] == "Deadlocks"

    # Verify saved in database
    db_plan = db_session.query(StudyPlan).filter(StudyPlan.id == data["id"]).first()
    assert db_plan is not None
    assert db_plan.title == "OS Mastery 7-Day Plan"
    assert db_plan.user_id == data["user_id"]

def test_unauthenticated_study_plan_request_rejected(client):
    """Verify unauthenticated POST /study-plans/generate returns 401."""
    resp = client.post("/study-plans/generate", json={"subject_id": 1})
    assert resp.status_code == 401

def test_cannot_generate_plan_for_another_users_subject(client):
    """Verify Student B cannot generate plan for Student A's subject."""
    token_a = register_and_login(client, "Owner A", "own_a@example.com")
    token_b = register_and_login(client, "Owner B", "own_b@example.com")

    subj_a_id = create_subject_with_topics(client, token_a, "Physics")

    resp = client.post("/study-plans/generate", json={"subject_id": subj_a_id}, headers={"Authorization": f"Bearer {token_b}"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Subject not found"

def test_missing_subject_returns_404(client):
    """Verify requesting plan for nonexistent subject returns 404."""
    token = register_and_login(client, "Missing Subj", "missingsubj@example.com")
    resp = client.post("/study-plans/generate", json={"subject_id": 99999}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Subject not found"

@patch("app.services.gemini_service.GeminiService.generate_json")
def test_profile_and_topics_context_passed_to_prompt(mock_gen, client):
    """Verify student profile and topic details are embedded into the Gemini prompt."""
    token = register_and_login(client, "Context Student", "ctxstudent@example.com")
    # Update profile
    client.put("/profile", json={"education_level": "Graduate", "daily_study_hours": 3.0, "learning_preference": "Visual"}, headers={"Authorization": f"Bearer {token}"})
    subject_id = create_subject_with_topics(client, token, "Distributed Systems")

    mock_gen.return_value = {
        "title": "Plan",
        "days": [{"day": 1, "topics": []}]
    }

    client.post("/study-plans/generate", json={"subject_id": subject_id}, headers={"Authorization": f"Bearer {token}"})

    assert mock_gen.called
    prompt_arg = mock_gen.call_args[0][0]
    assert "Graduate" in prompt_arg
    assert "3.0 hours" in prompt_arg
    assert "Visual" in prompt_arg
    assert "Distributed Systems" in prompt_arg
    assert "Processes" in prompt_arg
    assert "Deadlocks" in prompt_arg

@patch("app.services.gemini_service.GeminiService.generate_json")
def test_invalid_json_structure_rejected(mock_gen, client):
    """Verify malformed AI response (missing 'days' list) returns 502 Bad Gateway."""
    token = register_and_login(client, "Invalid AI", "invalidai@example.com")
    subject_id = create_subject_with_topics(client, token, "Math")

    # Missing 'days' key
    mock_gen.return_value = {"title": "Bad Plan", "strategy": "No days provided"}

    resp = client.post("/study-plans/generate", json={"subject_id": subject_id}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 502
    assert "Invalid AI response structure" in resp.json()["detail"]

@patch("app.services.gemini_service.GeminiService.generate_json")
def test_empty_ai_response_handled(mock_gen, client):
    """Verify empty days list in AI response is rejected with 502."""
    token = register_and_login(client, "Empty Days", "emptydays@example.com")
    subject_id = create_subject_with_topics(client, token, "Science")

    mock_gen.return_value = {"title": "Empty Plan", "days": []}

    resp = client.post("/study-plans/generate", json={"subject_id": subject_id}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 502
    assert "cannot be empty" in resp.json()["detail"]

@patch("app.services.gemini_service.GeminiService.generate_json")
def test_gemini_failure_handled_safely(mock_gen, client):
    """Verify GeminiServiceError raises 503 without exposing secrets."""
    token = register_and_login(client, "Gemini Fail", "geminifail@example.com")
    subject_id = create_subject_with_topics(client, token, "History")

    mock_gen.side_effect = GeminiAPIError("Provider 503 overload")

    resp = client.post("/study-plans/generate", json={"subject_id": subject_id}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 503
    assert "AI service temporarily unavailable" in resp.json()["detail"]

@patch("app.services.gemini_service.GeminiService.generate_json")
def test_saved_plan_belongs_to_authenticated_user(mock_gen, client):
    """Verify listing study plans only displays plans owned by the authenticated student."""
    token_a = register_and_login(client, "Student A", "plana@example.com")
    token_b = register_and_login(client, "Student B", "planb@example.com")

    subj_a_id = create_subject_with_topics(client, token_a, "Subj A")
    mock_gen.return_value = {"title": "Plan A", "days": [{"day": 1, "topics": []}]}

    client.post("/study-plans/generate", json={"subject_id": subj_a_id}, headers={"Authorization": f"Bearer {token_a}"})

    # Student B listing plans should see 0 plans
    resp_b = client.get("/study-plans", headers={"Authorization": f"Bearer {token_b}"})
    assert resp_b.status_code == 200
    assert len(resp_b.json()) == 0

    # Student A listing plans should see 1 plan
    resp_a = client.get("/study-plans", headers={"Authorization": f"Bearer {token_a}"})
    assert resp_a.status_code == 200
    assert len(resp_a.json()) == 1
    assert resp_a.json()[0]["title"] == "Plan A"
