def register_and_login(client, name="Topic Student", email="topicstudent@example.com", password="password123"):
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

def create_test_subject(client, token, name="Operating Systems"):
    """Helper to create a subject under the authenticated user."""
    resp = client.post("/subjects", json={"name": name, "difficulty": "medium"}, headers={"Authorization": f"Bearer {token}"})
    return resp.json()["id"]

def test_authenticated_user_can_create_topic(client):
    """Verify that an authenticated student can create a topic under their subject."""
    token = register_and_login(client, "Student 1", "s1@example.com")
    subject_id = create_test_subject(client, token, "Operating Systems")

    payload = {
        "name": "Process Scheduling",
        "status": "not_started",
        "difficulty": "medium"
    }
    resp = client.post(f"/subjects/{subject_id}/topics", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Process Scheduling"
    assert data["status"] == "not_started"
    assert data["difficulty"] == "medium"
    assert data["subject_id"] == subject_id
    assert "id" in data
    assert "created_at" in data

def test_unauthenticated_create_rejected(client):
    """Verify unauthenticated POST /subjects/{id}/topics returns 401."""
    resp = client.post("/subjects/1/topics", json={"name": "Threads"})
    assert resp.status_code == 401

def test_cannot_create_under_another_users_subject(client):
    """Verify Student B cannot create a topic under Student A's subject."""
    token_a = register_and_login(client, "Student A", "sa@example.com")
    token_b = register_and_login(client, "Student B", "sb@example.com")

    subj_a_id = create_test_subject(client, token_a, "Private Subject A")

    resp = client.post(
        f"/subjects/{subj_a_id}/topics",
        json={"name": "Intrusion Topic"},
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Subject not found"

def test_authenticated_user_can_list_own_topics(client):
    """Verify listing topics returns all topics for the authenticated user's subject."""
    token = register_and_login(client, "Lister", "lister@example.com")
    subject_id = create_test_subject(client, token, "DBMS")

    client.post(f"/subjects/{subject_id}/topics", json={"name": "SQL Queries"}, headers={"Authorization": f"Bearer {token}"})
    client.post(f"/subjects/{subject_id}/topics", json={"name": "Normalization"}, headers={"Authorization": f"Bearer {token}"})

    resp = client.get(f"/subjects/{subject_id}/topics", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    topics = resp.json()
    assert len(topics) == 2
    names = [t["name"] for t in topics]
    assert "SQL Queries" in names
    assert "Normalization" in names

def test_cannot_list_another_users_topics(client):
    """Verify Student B cannot list topics under Student A's subject."""
    token_a = register_and_login(client, "Owner A", "owner_a@example.com")
    token_b = register_and_login(client, "Owner B", "owner_b@example.com")

    subj_a_id = create_test_subject(client, token_a, "Algorithms")
    client.post(f"/subjects/{subj_a_id}/topics", json={"name": "Sorting"}, headers={"Authorization": f"Bearer {token_a}"})

    resp = client.get(f"/subjects/{subj_a_id}/topics", headers={"Authorization": f"Bearer {token_b}"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Subject not found"

def test_authenticated_user_can_get_own_topic(client):
    """Verify retrieving a single topic by ID."""
    token = register_and_login(client, "Getter", "getter_topic@example.com")
    subject_id = create_test_subject(client, token, "Networks")
    create_resp = client.post(f"/subjects/{subject_id}/topics", json={"name": "TCP Handshake"}, headers={"Authorization": f"Bearer {token}"})
    topic_id = create_resp.json()["id"]

    resp = client.get(f"/topics/{topic_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "TCP Handshake"
    assert resp.json()["subject_id"] == subject_id

def test_cannot_get_another_users_topic(client):
    """Verify accessing another user's topic by ID returns 404."""
    token_a = register_and_login(client, "Topic Owner A", "topica@example.com")
    token_b = register_and_login(client, "Topic Owner B", "topicb@example.com")

    subj_a_id = create_test_subject(client, token_a, "Compiler")
    topic_a = client.post(f"/subjects/{subj_a_id}/topics", json={"name": "Lexical Analysis"}, headers={"Authorization": f"Bearer {token_a}"}).json()

    resp = client.get(f"/topics/{topic_a['id']}", headers={"Authorization": f"Bearer {token_b}"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Topic not found"

def test_authenticated_user_can_update_own_topic(client):
    """Verify updating a topic's status and difficulty."""
    token = register_and_login(client, "Topic Updater", "topicupdater@example.com")
    subject_id = create_test_subject(client, token, "Cloud")
    topic = client.post(f"/subjects/{subject_id}/topics", json={"name": "Kubernetes"}, headers={"Authorization": f"Bearer {token}"}).json()

    update_resp = client.put(
        f"/topics/{topic['id']}",
        json={"status": "completed", "difficulty": "hard"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["status"] == "completed"
    assert data["difficulty"] == "hard"
    assert data["name"] == "Kubernetes"

def test_partial_update_works(client):
    """Verify partial updates leave unspecified fields unchanged."""
    token = register_and_login(client, "Partial Topic", "partialtopic@example.com")
    subject_id = create_test_subject(client, token, "Math")
    topic = client.post(f"/subjects/{subject_id}/topics", json={"name": "Linear Algebra", "status": "not_started", "difficulty": "hard"}, headers={"Authorization": f"Bearer {token}"}).json()

    patch_resp = client.put(f"/topics/{topic['id']}", json={"status": "in_progress"}, headers={"Authorization": f"Bearer {token}"})
    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data["status"] == "in_progress"
    assert data["name"] == "Linear Algebra"
    assert data["difficulty"] == "hard"

def test_cannot_update_another_users_topic(client):
    """Verify User B cannot update User A's topic."""
    token_a = register_and_login(client, "Sec Owner A", "secownera@example.com")
    token_b = register_and_login(client, "Sec Owner B", "secownerb@example.com")

    subject_a = create_test_subject(client, token_a, "Physics")
    topic_a = client.post(f"/subjects/{subject_a}/topics", json={"name": "Quantum Mechanics"}, headers={"Authorization": f"Bearer {token_a}"}).json()

    resp = client.put(f"/topics/{topic_a['id']}", json={"status": "completed"}, headers={"Authorization": f"Bearer {token_b}"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Topic not found"

def test_cannot_change_subject_ownership(client):
    """Verify client cannot reassign topic to another subject via PUT."""
    token = register_and_login(client, "Assign Tester", "assigntester@example.com")
    subject_1 = create_test_subject(client, token, "Subject 1")
    subject_2 = create_test_subject(client, token, "Subject 2")

    topic = client.post(f"/subjects/{subject_1}/topics", json={"name": "Immutable Topic"}, headers={"Authorization": f"Bearer {token}"}).json()

    # Attempt to change subject_id
    update_resp = client.put(f"/topics/{topic['id']}", json={"subject_id": subject_2}, headers={"Authorization": f"Bearer {token}"})
    assert update_resp.status_code == 200
    assert update_resp.json()["subject_id"] == subject_1  # Remains subject_1

def test_authenticated_user_can_delete_own_topic(client):
    """Verify deleting a topic."""
    token = register_and_login(client, "Topic Deleter", "topicdeleter@example.com")
    subject_id = create_test_subject(client, token, "Stats")
    topic = client.post(f"/subjects/{subject_id}/topics", json={"name": "Probability"}, headers={"Authorization": f"Bearer {token}"}).json()

    del_resp = client.delete(f"/topics/{topic['id']}", headers={"Authorization": f"Bearer {token}"})
    assert del_resp.status_code == 200
    assert del_resp.json()["message"] == "Topic deleted successfully"

    # Subsequent GET returns 404
    get_resp = client.get(f"/topics/{topic['id']}", headers={"Authorization": f"Bearer {token}"})
    assert get_resp.status_code == 404

def test_cannot_delete_another_users_topic(client):
    """Verify User B cannot delete User A's topic."""
    token_a = register_and_login(client, "Del A", "dela@example.com")
    token_b = register_and_login(client, "Del B", "delb@example.com")

    subject_a = create_test_subject(client, token_a, "Biology")
    topic_a = client.post(f"/subjects/{subject_a}/topics", json={"name": "Genetics"}, headers={"Authorization": f"Bearer {token_a}"}).json()

    del_resp = client.delete(f"/topics/{topic_a['id']}", headers={"Authorization": f"Bearer {token_b}"})
    assert del_resp.status_code == 404
    assert del_resp.json()["detail"] == "Topic not found"

def test_invalid_values_rejected(client):
    """Verify empty name or excessive length is rejected with 422."""
    token = register_and_login(client, "Topic Validator", "topicvalidator@example.com")
    subject_id = create_test_subject(client, token, "History")

    # Empty name
    empty_resp = client.post(f"/subjects/{subject_id}/topics", json={"name": ""}, headers={"Authorization": f"Bearer {token}"})
    assert empty_resp.status_code == 422

    # Excessive length
    long_resp = client.post(f"/subjects/{subject_id}/topics", json={"name": "A" * 101}, headers={"Authorization": f"Bearer {token}"})
    assert long_resp.status_code == 422

def test_response_matches_actual_topic_model(client):
    """Verify response structure directly matches SQLAlchemy Topic model fields."""
    token = register_and_login(client, "Schema Match", "schemamatch@example.com")
    subject_id = create_test_subject(client, token, "Chemistry")

    resp = client.post(f"/subjects/{subject_id}/topics", json={"name": "Organic Chemistry"}, headers={"Authorization": f"Bearer {token}"})
    data = resp.json()
    expected_fields = {"id", "subject_id", "name", "status", "difficulty", "created_at", "updated_at"}
    assert expected_fields.issubset(set(data.keys()))
