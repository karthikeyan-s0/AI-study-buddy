def register_and_login(client, name="Subject Student", email="subjstudent@example.com", password="password123"):
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

def test_authenticated_user_can_create_subject(client):
    """Verify that an authenticated student can create a new subject."""
    token = register_and_login(client, "User One", "user1@example.com")
    payload = {
        "name": "Operating Systems",
        "description": "OS principles and internals",
        "exam_date": "2026-10-15",
        "difficulty": "medium"
    }
    resp = client.post("/subjects", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Operating Systems"
    assert data["description"] == "OS principles and internals"
    assert data["exam_date"] == "2026-10-15"
    assert data["difficulty"] == "medium"
    assert "id" in data
    assert "user_id" in data

def test_unauthenticated_create_rejected(client):
    """Verify unauthenticated POST /subjects returns 401."""
    resp = client.post("/subjects", json={"name": "Database Systems"})
    assert resp.status_code == 401

def test_authenticated_user_can_list_own_subjects(client):
    """Verify listing subjects returns all subjects belonging to the authenticated student."""
    token = register_and_login(client, "User List", "userlist@example.com")
    client.post("/subjects", json={"name": "Compiler Design"}, headers={"Authorization": f"Bearer {token}"})
    client.post("/subjects", json={"name": "Computer Architecture"}, headers={"Authorization": f"Bearer {token}"})

    resp = client.get("/subjects", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    names = [s["name"] for s in data]
    assert "Compiler Design" in names
    assert "Computer Architecture" in names

def test_user_cannot_see_another_users_subjects(client):
    """Verify User A cannot see subjects created by User B."""
    token_a = register_and_login(client, "Student A", "studenta@example.com")
    token_b = register_and_login(client, "Student B", "studentb@example.com")

    # User A creates a subject
    client.post("/subjects", json={"name": "Discrete Mathematics"}, headers={"Authorization": f"Bearer {token_a}"})

    # User B lists subjects — should be empty
    resp_b = client.get("/subjects", headers={"Authorization": f"Bearer {token_b}"})
    assert resp_b.status_code == 200
    assert len(resp_b.json()) == 0

def test_authenticated_user_can_get_own_subject(client):
    """Verify retrieving a specific subject by ID."""
    token = register_and_login(client, "Getter", "getter@example.com")
    create_resp = client.post("/subjects", json={"name": "Algorithms"}, headers={"Authorization": f"Bearer {token}"})
    subject_id = create_resp.json()["id"]

    get_resp = client.get(f"/subjects/{subject_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Algorithms"

def test_getting_another_users_subject_returns_404(client):
    """Verify accessing another user's subject by ID returns 404."""
    token_a = register_and_login(client, "Owner A", "ownera@example.com")
    token_b = register_and_login(client, "Owner B", "ownerb@example.com")

    # User A creates subject
    create_resp = client.post("/subjects", json={"name": "Secret Theory"}, headers={"Authorization": f"Bearer {token_a}"})
    subject_id = create_resp.json()["id"]

    # User B attempts to access it
    resp_b = client.get(f"/subjects/{subject_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert resp_b.status_code == 404
    assert resp_b.json()["detail"] == "Subject not found"

def test_authenticated_user_can_update_own_subject(client):
    """Verify updating a subject's fields."""
    token = register_and_login(client, "Updater", "updater@example.com")
    create_resp = client.post("/subjects", json={"name": "Web Dev", "difficulty": "easy"}, headers={"Authorization": f"Bearer {token}"})
    subject_id = create_resp.json()["id"]

    update_resp = client.put(f"/subjects/{subject_id}", json={
        "name": "Full Stack Web Development",
        "difficulty": "hard",
        "description": "Advanced web dev"
    }, headers={"Authorization": f"Bearer {token}"})
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["name"] == "Full Stack Web Development"
    assert data["difficulty"] == "hard"
    assert data["description"] == "Advanced web dev"

def test_partial_update_works(client):
    """Verify partial update leaves unspecified fields intact."""
    token = register_and_login(client, "Partial", "partial@example.com")
    create_resp = client.post("/subjects", json={
        "name": "Machine Learning",
        "description": "ML fundamentals",
        "difficulty": "hard"
    }, headers={"Authorization": f"Bearer {token}"})
    subject_id = create_resp.json()["id"]

    # Only update difficulty
    patch_resp = client.put(f"/subjects/{subject_id}", json={"difficulty": "medium"}, headers={"Authorization": f"Bearer {token}"})
    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data["difficulty"] == "medium"
    assert data["name"] == "Machine Learning"
    assert data["description"] == "ML fundamentals"

def test_user_cannot_update_another_users_subject(client):
    """Verify User B cannot update User A's subject."""
    token_a = register_and_login(client, "Subject User A", "subja@example.com")
    token_b = register_and_login(client, "Subject User B", "subjb@example.com")

    create_resp = client.post("/subjects", json={"name": "Cybersecurity"}, headers={"Authorization": f"Bearer {token_a}"})
    subject_id = create_resp.json()["id"]

    resp = client.put(f"/subjects/{subject_id}", json={"name": "Hacked Name"}, headers={"Authorization": f"Bearer {token_b}"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Subject not found"

def test_authenticated_user_can_delete_own_subject(client):
    """Verify deleting a subject returns success."""
    token = register_and_login(client, "Deleter", "deleter@example.com")
    create_resp = client.post("/subjects", json={"name": "To Be Deleted"}, headers={"Authorization": f"Bearer {token}"})
    subject_id = create_resp.json()["id"]

    del_resp = client.delete(f"/subjects/{subject_id}", headers={"Authorization": f"Bearer {token}"})
    assert del_resp.status_code == 200
    assert del_resp.json()["message"] == "Subject deleted successfully"

def test_deleted_subject_cannot_be_retrieved(client):
    """Verify a deleted subject returns 404 on subsequent get requests."""
    token = register_and_login(client, "Re-getter", "regetter@example.com")
    create_resp = client.post("/subjects", json={"name": "Temporary Subject"}, headers={"Authorization": f"Bearer {token}"})
    subject_id = create_resp.json()["id"]

    client.delete(f"/subjects/{subject_id}", headers={"Authorization": f"Bearer {token}"})

    get_resp = client.get(f"/subjects/{subject_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_resp.status_code == 404
    assert get_resp.json()["detail"] == "Subject not found"

def test_deleting_another_users_subject_returns_404(client):
    """Verify deleting another user's subject returns 404."""
    token_a = register_and_login(client, "Safe Owner", "safeowner@example.com")
    token_b = register_and_login(client, "Attacker", "attacker@example.com")

    create_resp = client.post("/subjects", json={"name": "Protected Subject"}, headers={"Authorization": f"Bearer {token_a}"})
    subject_id = create_resp.json()["id"]

    del_resp = client.delete(f"/subjects/{subject_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert del_resp.status_code == 404
    assert del_resp.json()["detail"] == "Subject not found"

def test_invalid_subject_data_rejected(client):
    """Verify empty name or name exceeding max length is rejected with 422."""
    token = register_and_login(client, "Validator", "validator@example.com")

    # Empty name
    empty_resp = client.post("/subjects", json={"name": ""}, headers={"Authorization": f"Bearer {token}"})
    assert empty_resp.status_code == 422

    # Name exceeding 100 characters
    long_resp = client.post("/subjects", json={"name": "A" * 101}, headers={"Authorization": f"Bearer {token}"})
    assert long_resp.status_code == 422
