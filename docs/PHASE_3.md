# AI StudyBuddy — Phase 3: Authentication & User Management Documentation

## 1. Authentication Architecture

AI StudyBuddy implements a stateless, token-based authentication system using **JSON Web Tokens (JWT)** and **bcrypt** password hashing. The authentication layer is decoupled into modular components:

- **Configuration (`app/core/config.py`)**: Environment-driven JWT parameters (`JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`).
- **Security Utilities (`app/core/security.py`)**: Isolated functions for hashing, password verification, token encoding, and decoding.
- **Dependency Layer (`app/core/dependencies.py`)**: FastAPI `get_current_user` dependency with `OAuth2PasswordBearer` scheme.
- **Data Validation (`app/schemas/`)**: Strict Pydantic models for user input validation and safe output serialisation (`UserResponse` omitting sensitive fields).
- **Authentication Router (`app/routers/auth.py`)**: REST endpoints for registration, login, and profile introspection (`/auth/me`).

```text
┌────────────────┐          ┌────────────────────┐          ┌───────────────────────┐
│     Client     │          │   FastAPI Router   │          │  Database / Security  │
└───────┬────────┘          └─────────┬──────────┘          └───────────┬───────────┘
        │                             │                                 │
        │─── POST /auth/register ────>│                                 │
        │    {name, email, password}  │─── hash_password(pwd) ─────────>│
        │                             │<── bcrypt hash $2b$... ─────────│
        │                             │─── INSERT User + Profile ──────>│
        │<── 201 UserResponse ────────│                                 │
        │    (no password_hash!)      │                                 │
        │                             │                                 │
        │─── POST /auth/login ───────>│                                 │
        │    {email, password}        │─── verify_password() ──────────>│
        │                             │─── create_access_token() ──────>│
        │<── 200 {access_token, ...} ─│                                 │
        │                             │                                 │
        │─── GET /auth/me ───────────>│                                 │
        │    Authorization: Bearer    │─── decode_access_token() ──────>│
        │                             │─── Query User by ID ───────────>│
        │<── 200 UserResponse ────────│                                 │
```

---

## 2. Registration Flow (`POST /auth/register`)

1. **Input Validation**: Pydantic validates email syntax and password length (minimum 6 characters).
2. **Duplicate Check**: The database is queried for any existing user with the same email. If found, returns `400 Bad Request` with `{"detail": "Email already registered"}`.
3. **Password Hashing**: The plaintext password is salted and hashed using `bcrypt.hashpw(..., bcrypt.gensalt())`.
4. **User & Profile Persistence**:
   - Creates a new `User` record with the hash.
   - Automatically provisions a default `Profile` record (`education_level="College"`, `daily_study_hours=2.0`, `learning_preference="Visual"`).
   - In case of failure, rolls back the transaction.
5. **Safe Response**: Returns HTTP 201 with `UserResponse` (`id`, `name`, `email`, `created_at`). `password_hash` is strictly excluded.

---

## 3. Login Flow (`POST /auth/login`)

1. **User Lookup**: Retrieves user by email.
2. **Credential Verification**: Compares plaintext password against stored hash using `bcrypt.checkpw()`.
3. **Rejection**: If the email does not exist or the password does not match, returns `401 Unauthorized` with `{"detail": "Invalid credentials"}`.
4. **Token Generation**: Signs a JWT containing:
   - `sub`: User ID string
   - `email`: User email
   - `exp`: Expiration timestamp (UTC)
   - `iat`: Issued-at timestamp (UTC)
5. **Response**: Returns HTTP 200 with `{ "access_token": "<jwt>", "token_type": "bearer" }`.

---

## 4. Protected Endpoints & Current User Dependency (`GET /auth/me`)

The reusable dependency `get_current_user()` provides request authentication for all downstream private routes:
1. Extracts Bearer token from the `Authorization: Bearer <token>` header via FastAPI's `OAuth2PasswordBearer`.
2. Validates JWT signature and expiration.
3. Extracts user ID from the `sub` claim.
4. Retrieves `User` from the database.
5. Raises `401 Unauthorized` with `WWW-Authenticate: Bearer` header on:
   - Missing token
   - Invalid token or corrupt signature
   - Expired token (`Token has expired`)
   - Non-existent user

---

## 5. Security Measures

- **Zero Plaintext Storage**: Passwords are exclusively stored as bcrypt hashes ($2b$).
- **No Sensitive Leakage**: Pydantic `UserResponse` model guarantees `password` or `password_hash` is never included in any API response.
- **Constant-Time Verification**: Uses bcrypt's built-in constant-time comparison to prevent timing attacks.
- **Config Isolation**: Secrets and tokens are loaded strictly via environment variables (`.env`).
- **Protected Database Sessions**: Transaction rollbacks are enforced on error to avoid leaving database connections or transactions in inconsistent states.

---

## 6. Automated Test Results

Test suite: `backend/tests/test_auth.py` and `backend/tests/test_database.py`

Command executed:
```bash
python -m pytest -v
```

Output:
```text
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
collected 22 items

tests/test_auth.py::test_register_successfully PASSED                    [  4%]
tests/test_auth.py::test_password_stored_as_hash PASSED                  [  9%]
tests/test_auth.py::test_duplicate_email_rejected PASSED                 [ 13%]
tests/test_auth.py::test_default_profile_created_on_registration PASSED  [ 18%]
tests/test_auth.py::test_login_successfully PASSED                       [ 22%]
tests/test_auth.py::test_wrong_password_rejected PASSED                  [ 27%]
tests/test_auth.py::test_unknown_email_rejected PASSED                   [ 31%]
tests/test_auth.py::test_get_me_with_valid_jwt PASSED                    [ 36%]
tests/test_auth.py::test_missing_token_rejected PASSED                   [ 40%]
tests/test_auth.py::test_invalid_token_rejected PASSED                   [ 45%]
tests/test_auth.py::test_expired_token_rejected PASSED                   [ 50%]
tests/test_auth.py::test_password_hash_never_appears_in_api_response PASSED [ 54%]
tests/test_database.py::test_database_initialization_all_eight_tables PASSED [ 59%]
tests/test_database.py::test_insert_user PASSED                          [ 63%]
tests/test_database.py::test_unique_user_email PASSED                    [ 68%]
tests/test_database.py::test_user_profile_relationship PASSED            [ 72%]
tests/test_database.py::test_user_subject_relationship PASSED            [ 77%]
tests/test_database.py::test_subject_topic_relationship PASSED           [ 81%]
tests/test_database.py::test_study_plan_relationships_and_json PASSED    [ 86%]
tests/test_database.py::test_quiz_and_quiz_attempt_relationships_and_json PASSED [ 90%]
tests/test_database.py::test_progress_relationships PASSED               [ 95%]
tests/test_database.py::test_api_health_and_docs_endpoints PASSED        [100%]

======================== 22 passed, 1 warning in 3.59s ========================
```
