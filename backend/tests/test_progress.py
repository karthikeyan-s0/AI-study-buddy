def register_and_login(client, name="Progress Student", email="progstudent@example.com", password="password123"):
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

def create_subject_and_topic(client, token):
    s_resp = client.post("/subjects", json={
        "name": "Database Management",
        "description": "SQL and NoSQL",
        "difficulty": "medium",
        "exam_date": "2026-11-15"
    }, headers={"Authorization": f"Bearer {token}"})
    subject_id = s_resp.json()["id"]

    t_resp = client.post(f"/subjects/{subject_id}/topics", json={
        "name": "Indexing & B-Trees",
        "difficulty": "hard",
        "status": "not_started"
    }, headers={"Authorization": f"Bearer {token}"})
    topic_id = t_resp.json()["id"]
    return subject_id, topic_id

def test_record_and_upsert_progress(client):
    token = register_and_login(client, "Progress User", "prog1@example.com")
    subject_id, topic_id = create_subject_and_topic(client, token)

    # First update: 50% completed, 45 minutes
    resp = client.post("/progress", json={
        "subject_id": subject_id,
        "topic_id": topic_id,
        "completion_percentage": 50.0,
        "study_minutes": 45
    }, headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["subject_id"] == subject_id
    assert data["topic_id"] == topic_id
    assert data["completion_percentage"] == 50.0
    assert data["study_minutes"] == 45

    # Second update: completion goes to 100%, +30 minutes (should accumulate to 75 minutes)
    resp2 = client.post("/progress", json={
        "subject_id": subject_id,
        "topic_id": topic_id,
        "completion_percentage": 100.0,
        "study_minutes": 30
    }, headers={"Authorization": f"Bearer {token}"})

    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["completion_percentage"] == 100.0
    assert data2["study_minutes"] == 75

    # Check topic status is updated to completed
    t_get = client.get(f"/topics/{topic_id}", headers={"Authorization": f"Bearer {token}"})
    assert t_get.status_code == 200
    assert t_get.json()["status"] == "completed"

def test_get_progress_endpoints(client):
    token = register_and_login(client, "Progress Reader", "prog_reader@example.com")
    subject_id, topic_id = create_subject_and_topic(client, token)

    client.post("/progress", json={
        "subject_id": subject_id,
        "topic_id": topic_id,
        "completion_percentage": 75.0,
        "study_minutes": 60
    }, headers={"Authorization": f"Bearer {token}"})

    # List all
    all_resp = client.get("/progress", headers={"Authorization": f"Bearer {token}"})
    assert all_resp.status_code == 200
    assert len(all_resp.json()) == 1

    # By subject
    subj_resp = client.get(f"/progress/subjects/{subject_id}", headers={"Authorization": f"Bearer {token}"})
    assert subj_resp.status_code == 200
    assert len(subj_resp.json()) == 1

    # By topic
    top_resp = client.get(f"/progress/topics/{topic_id}", headers={"Authorization": f"Bearer {token}"})
    assert top_resp.status_code == 200
    assert top_resp.json()["completion_percentage"] == 75.0

def test_progress_tenant_isolation(client):
    token1 = register_and_login(client, "Owner", "owner@example.com")
    token2 = register_and_login(client, "Stranger", "stranger@example.com")
    subject_id, topic_id = create_subject_and_topic(client, token1)

    # Stranger tries to update owner's topic progress
    resp = client.post("/progress", json={
        "subject_id": subject_id,
        "topic_id": topic_id,
        "completion_percentage": 100.0,
        "study_minutes": 60
    }, headers={"Authorization": f"Bearer {token2}"})

    assert resp.status_code == 404
