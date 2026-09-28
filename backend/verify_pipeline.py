"""
End-to-End Pipeline Verification Script for AI StudyBuddy.
Executes against FastAPI TestClient to verify the complete student journey:
1. Registration & Login (JWT)
2. Profile Update
3. Subject & Topic Creation
4. Mock/Live Gemini Study Plan
5. AI Summarizer
6. Deterministic Quiz Generation & Scoring
7. Progress Recording
8. Aggregated Dashboard Verification
"""
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

def run_verification():
    print("[START] Starting AI StudyBuddy Full Pipeline Verification...")
    client = TestClient(app)

    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200
    print("[OK] Health Check passed:", res.json())

    import time
    test_email = f"e2e_{int(time.time())}@college.edu"

    # 2. Register & Login
    client.post("/auth/register", json={
        "name": "E2E Student",
        "email": test_email,
        "password": "finalproject2026"
    })
    login_res = client.post("/auth/login", json={
        "email": test_email,
        "password": "finalproject2026"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[OK] Auth & JWT Generation passed")

    # 3. Profile
    prof_res = client.put("/profile", json={
        "education_level": "Undergraduate",
        "daily_study_hours": 3.0,
        "learning_preference": "Visual"
    }, headers=headers)
    assert prof_res.status_code == 200
    print("[OK] Student Profile updated")

    # 4. Create Subject & Topic
    subj_res = client.post("/subjects", json={
        "name": "Cloud Computing",
        "description": "Distributed systems and AWS",
        "difficulty": "medium",
        "exam_date": "2026-12-20"
    }, headers=headers)
    assert subj_res.status_code == 201
    subject_id = subj_res.json()["id"]

    top_res = client.post(f"/subjects/{subject_id}/topics", json={
        "name": "Serverless Architecture",
        "difficulty": "medium",
        "status": "not_started"
    }, headers=headers)
    assert top_res.status_code == 201
    topic_id = top_res.json()["id"]
    print("[OK] Subject & Topic created")

    # 5. Study Plan (Mocked AI)
    with patch("app.services.gemini_service.GeminiService.generate_json") as mock_gen:
        mock_gen.return_value = {
            "title": "Cloud Computing 7-Day Plan",
            "summary": "Master serverless and container technologies.",
            "days": [
                {
                    "day": 1,
                    "date": "2026-10-01",
                    "topics": [
                        {
                            "topic": "Serverless Architecture",
                            "duration_minutes": 60,
                            "activities": ["Read AWS Lambda overview", "Write first handler function"]
                        }
                    ]
                }
            ]
        }
        plan_res = client.post("/study-plans/generate", json={
            "subject_id": subject_id,
            "start_date": "2026-10-01",
            "end_date": "2026-10-07"
        }, headers=headers)
        assert plan_res.status_code == 201
        print("[OK] AI Study Plan generated & stored")

    # 6. AI Summarizer
    with patch("app.services.gemini_service.GeminiService.generate_json") as mock_gen:
        mock_gen.return_value = {
            "summary": "Serverless architecture executes code without provisioning servers.",
            "key_points": ["Pay-per-use execution", "Automatic horizontal scaling"],
            "important_terms": [
                "FaaS: Function as a Service platform"
            ]
        }
        sum_res = client.post("/ai/summarize", json={
            "content": "Serverless computing is a cloud-computing execution model where the cloud provider runs the server."
        }, headers=headers)
        assert sum_res.status_code == 200
        print("[OK] AI Summarizer generated structured JSON")

    # 7. Quizzes & Deterministic Grading
    with patch("app.services.gemini_service.GeminiService.generate_json") as mock_gen:
        mock_gen.return_value = {
            "questions": [
                {
                    "question": "What is an event source in serverless?",
                    "options": {
                        "A": "The trigger that executes the function",
                        "B": "The physical server chassis",
                        "C": "The compiler target",
                        "D": "The billing currency"
                    },
                    "correct_answer": "A",
                    "explanation": "Event sources invoke the function."
                }
            ]
        }
        q_res = client.post("/quizzes/generate", json={
            "subject_id": subject_id,
            "topic": "Serverless Architecture",
            "difficulty": "medium",
            "number_of_questions": 1
        }, headers=headers)
        assert q_res.status_code == 201
        quiz_id = q_res.json()["id"]

        # Deterministic submission
        sub_res = client.post(f"/quizzes/{quiz_id}/submit", json={
            "answers": {"0": "A"}
        }, headers=headers)
        assert sub_res.status_code == 200
        assert sub_res.json()["percentage"] == 100.0
        print("[OK] AI Quiz generated and deterministically graded (100% score)")

    # 8. Record Progress
    prog_res = client.post("/progress", json={
        "subject_id": subject_id,
        "topic_id": topic_id,
        "completion_percentage": 100.0,
        "study_minutes": 60
    }, headers=headers)
    assert prog_res.status_code == 200
    print("[OK] Progress recorded & topic synchronized")

    # 9. Dashboard
    dash_res = client.get("/dashboard", headers=headers)
    assert dash_res.status_code == 200
    d_data = dash_res.json()
    assert d_data["overall_progress"] == 100.0
    assert len(d_data["subjects"]) == 1
    assert len(d_data["recent_quiz_attempts"]) == 1
    print("[OK] Dashboard aggregated stats verified:", {
        "overall_progress": d_data["overall_progress"],
        "subjects": len(d_data["subjects"]),
        "recent_quiz_attempts": len(d_data["recent_quiz_attempts"])
    })

    print("\n[SUCCESS] ALL 9 SUBSYSTEMS VERIFIED END-TO-END WITH ZERO ERRORS!")

if __name__ == "__main__":
    run_verification()
