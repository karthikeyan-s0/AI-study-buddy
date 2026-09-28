from app.models.user import User
from app.models.profile import Profile
from app.core.security import create_access_token

def register_and_login(client, name="Test Student", email="student@example.com", password="password123"):
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

def test_authenticated_user_can_get_profile(client):
    """Verify that an authenticated user can retrieve their default profile."""
    token = register_and_login(client, "Alice", "alice@example.com")
    resp = client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["education_level"] == "College"
    assert data["daily_study_hours"] == 2.0
    assert data["learning_preference"] == "Visual"
    assert "user_id" in data
    assert "password" not in data
    assert "password_hash" not in data

def test_unauthenticated_get_rejected(client):
    """Verify that unauthenticated GET /profile returns 401."""
    resp = client.get("/profile")
    assert resp.status_code == 401

def test_authenticated_user_can_update_profile(client):
    """Verify that an authenticated user can update their profile values."""
    token = register_and_login(client, "Bob", "bob@example.com")
    update_payload = {
        "education_level": "Undergraduate",
        "daily_study_hours": 3.5,
        "learning_preference": "Kinesthetic"
    }
    resp = client.put("/profile", json=update_payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["education_level"] == "Undergraduate"
    assert data["daily_study_hours"] == 3.5
    assert data["learning_preference"] == "Kinesthetic"

def test_updated_values_are_persisted(client):
    """Verify that changes made by PUT /profile persist when fetched via GET /profile."""
    token = register_and_login(client, "Charlie", "charlie@example.com")
    client.put("/profile", json={
        "education_level": "Master's Degree",
        "daily_study_hours": 4.0,
        "learning_preference": "Reading"
    }, headers={"Authorization": f"Bearer {token}"})

    get_resp = client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["education_level"] == "Master's Degree"
    assert data["daily_study_hours"] == 4.0
    assert data["learning_preference"] == "Reading"

def test_partial_update_works(client):
    """Verify partial updates only modify specified fields, preserving existing values."""
    token = register_and_login(client, "Dana", "dana@example.com")
    # Only update daily_study_hours
    resp = client.put("/profile", json={"daily_study_hours": 5.0}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["daily_study_hours"] == 5.0
    assert data["education_level"] == "College"  # preserved default
    assert data["learning_preference"] == "Visual"  # preserved default

def test_unauthenticated_put_rejected(client):
    """Verify unauthenticated PUT /profile returns 401."""
    resp = client.put("/profile", json={"daily_study_hours": 3.0})
    assert resp.status_code == 401

def test_user_cannot_modify_another_users_profile(client):
    """Verify that User A updating their profile does not change User B's profile."""
    token_a = register_and_login(client, "User A", "usera@example.com")
    token_b = register_and_login(client, "User B", "userb@example.com")

    # User A updates profile to 6.0 hours
    client.put("/profile", json={"daily_study_hours": 6.0}, headers={"Authorization": f"Bearer {token_a}"})

    # User B's profile should remain unchanged at 2.0 hours
    resp_b = client.get("/profile", headers={"Authorization": f"Bearer {token_b}"})
    assert resp_b.status_code == 200
    assert resp_b.json()["daily_study_hours"] == 2.0

def test_missing_profile_handled_correctly(client, db_session):
    """Verify 404 is returned if a user's profile record is missing from the database."""
    # Create user manually without a profile
    user_no_profile = User(
        name="No Profile User",
        email="noprofile@example.com",
        password_hash="somehash"
    )
    db_session.add(user_no_profile)
    db_session.commit()
    db_session.refresh(user_no_profile)

    token = create_access_token(data={"sub": str(user_no_profile.id)})

    get_resp = client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    assert get_resp.status_code == 404
    assert get_resp.json()["detail"] == "Profile not found"

    put_resp = client.put("/profile", json={"daily_study_hours": 2.0}, headers={"Authorization": f"Bearer {token}"})
    assert put_resp.status_code == 404
    assert put_resp.json()["detail"] == "Profile not found"

def test_invalid_daily_study_hours_rejected(client):
    """Verify negative or unrealistic study hours are rejected with 422 Unprocessable Entity."""
    token = register_and_login(client, "Invalid Hours", "invalidhours@example.com")

    # Test negative hours
    neg_resp = client.put("/profile", json={"daily_study_hours": -2.0}, headers={"Authorization": f"Bearer {token}"})
    assert neg_resp.status_code == 422

    # Test hours > 24
    over_resp = client.put("/profile", json={"daily_study_hours": 25.0}, headers={"Authorization": f"Bearer {token}"})
    assert over_resp.status_code == 422

def test_password_hash_never_appears_in_profile_response(client):
    """Verify password_hash is never present in GET or PUT /profile responses."""
    token = register_and_login(client, "Leak Test", "leaktest@example.com")

    get_resp = client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    assert "password_hash" not in get_resp.text
    assert "password123" not in get_resp.text

    put_resp = client.put("/profile", json={"education_level": "College"}, headers={"Authorization": f"Bearer {token}"})
    assert "password_hash" not in put_resp.text
    assert "password123" not in put_resp.text
