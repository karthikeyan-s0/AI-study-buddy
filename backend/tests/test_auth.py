from datetime import timedelta
import pytest
from app.models.user import User
from app.models.profile import Profile
from app.core.security import create_access_token, verify_password

def test_register_successfully(client, db_session):
    """Test successful user registration and verify response structure."""
    payload = {
        "name": "Karthi",
        "email": "karthi@example.com",
        "password": "password123"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Karthi"
    assert data["email"] == "karthi@example.com"
    assert "id" in data
    assert "created_at" in data
    assert "password" not in data
    assert "password_hash" not in data

def test_password_stored_as_hash(client, db_session):
    """Ensure password is never stored in plaintext in the database."""
    payload = {
        "name": "Security Test",
        "email": "sectest@example.com",
        "password": "my_secret_pass"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201

    user = db_session.query(User).filter(User.email == "sectest@example.com").first()
    assert user is not None
    assert user.password_hash != "my_secret_pass"
    assert user.password_hash.startswith("$2b$") or user.password_hash.startswith("$2a$")
    assert verify_password("my_secret_pass", user.password_hash)

def test_duplicate_email_rejected(client):
    """Ensure duplicate email registration is rejected with 400."""
    payload = {
        "name": "User One",
        "email": "dup@example.com",
        "password": "password123"
    }
    resp1 = client.post("/auth/register", json=payload)
    assert resp1.status_code == 201

    resp2 = client.post("/auth/register", json=payload)
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Email already registered"

def test_default_profile_created_on_registration(client, db_session):
    """Verify that a default profile is created automatically for new users."""
    payload = {
        "name": "Profile Student",
        "email": "profilestudent@example.com",
        "password": "password123"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    user_id = response.json()["id"]

    profile = db_session.query(Profile).filter(Profile.user_id == user_id).first()
    assert profile is not None
    assert profile.education_level == "College"
    assert profile.daily_study_hours == 2.0
    assert profile.learning_preference == "Visual"

def test_login_successfully(client):
    """Verify login with correct credentials returns valid JWT token."""
    client.post("/auth/register", json={
        "name": "Login User",
        "email": "login@example.com",
        "password": "password123"
    })

    login_resp = client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "password123"
    })
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 20

def test_wrong_password_rejected(client):
    """Verify login with incorrect password returns 401."""
    client.post("/auth/register", json={
        "name": "Wrong Pass User",
        "email": "wrongpass@example.com",
        "password": "password123"
    })

    resp = client.post("/auth/login", json={
        "email": "wrongpass@example.com",
        "password": "incorrectpassword"
    })
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"

def test_unknown_email_rejected(client):
    """Verify login with unregistered email returns 401."""
    resp = client.post("/auth/login", json={
        "email": "doesnotexist@example.com",
        "password": "somepassword"
    })
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"

def test_get_me_with_valid_jwt(client):
    """Verify GET /auth/me returns current user profile when given valid token."""
    client.post("/auth/register", json={
        "name": "Valid Token User",
        "email": "validtoken@example.com",
        "password": "password123"
    })

    login_resp = client.post("/auth/login", json={
        "email": "validtoken@example.com",
        "password": "password123"
    })
    token = login_resp.json()["access_token"]

    me_resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["name"] == "Valid Token User"
    assert me_data["email"] == "validtoken@example.com"
    assert "password_hash" not in me_data

def test_missing_token_rejected(client):
    """Verify GET /auth/me without authorization header returns 401."""
    resp = client.get("/auth/me")
    assert resp.status_code == 401

def test_invalid_token_rejected(client):
    """Verify GET /auth/me with an invalid token returns 401."""
    resp = client.get("/auth/me", headers={"Authorization": "Bearer not.a.valid.token"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Could not validate credentials"

def test_expired_token_rejected(client, db_session):
    """Verify GET /auth/me with an expired JWT returns 401 Token has expired."""
    user = User(
        name="Expired User",
        email="expired@example.com",
        password_hash="somehash"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    expired_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(seconds=-10)
    )

    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Token has expired"

def test_password_hash_never_appears_in_api_response(client):
    """Verify password_hash is omitted across all auth responses."""
    reg_resp = client.post("/auth/register", json={
        "name": "Leak Check",
        "email": "leakcheck@example.com",
        "password": "password123"
    })
    assert "password_hash" not in reg_resp.text
    assert "password123" not in reg_resp.text

    login_resp = client.post("/auth/login", json={
        "email": "leakcheck@example.com",
        "password": "password123"
    })
    token = login_resp.json()["access_token"]

    me_resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert "password_hash" not in me_resp.text
