# AI StudyBuddy — Phase 4: Student Profile Management Documentation

## 1. Profile Architecture

The student profile layer provides personalized learning preferences and study configuration, maintaining a strict 1-to-1 relationship with the authenticated user:

```text
┌─────────────────┐             1 : 1             ┌──────────────────┐
│      User       │ ────────────────────────────> │     Profile      │
│  (Auth Entity)  │ <──────────────────────────── │ (Learning Setup) │
└─────────────────┘                               └──────────────────┘
```

The profile model was instantiated and linked in Phase 2/3 and is now fully managed via dedicated, secure REST endpoints in Phase 4.

---

## 2. Endpoints

| Method | Endpoint | Protection | Description | Status Codes |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/profile` | `Bearer <JWT>` | Retrieves the authenticated student's profile | 200, 401, 404 |
| `PUT` | `/profile` | `Bearer <JWT>` | Updates education level, daily study hours, or learning preference | 200, 401, 404, 422 |

---

## 3. Authentication & Ownership Protection

Security is guaranteed at the dependency injection level:
1. The request provides `Authorization: Bearer <token>`.
2. `get_current_user` validates the JWT and resolves the database `User` instance.
3. The profile query filters strictly by `Profile.user_id == current_user.id`.
4. The client cannot pass a `user_id` in request payloads or URL parameters, preventing any privilege escalation or cross-tenant modification.

---

## 4. Request & Response Schemas

### `ProfileUpdate` (Request Body)
Supports partial updates; any omitted fields remain unchanged.
```json
{
  "education_level": "College",
  "daily_study_hours": 3.5,
  "learning_preference": "Kinesthetic"
}
```

### `ProfileResponse` (Response Body)
Guarantees zero exposure of sensitive user or password hash data.
```json
{
  "id": 1,
  "user_id": 1,
  "education_level": "College",
  "daily_study_hours": 3.5,
  "learning_preference": "Kinesthetic",
  "created_at": "2026-09-28T05:03:08.474157",
  "updated_at": "2026-09-28T05:03:08.732036"
}
```

---

## 5. Input Validation Rules

Enforced via Pydantic V2 in [`app/schemas/profile.py`](file:///C:/Users/Biosp/.gemini/antigravity/scratch/studybuddy/backend/app/schemas/profile.py):
- `education_level`: Optional string, `1 <= len <= 50`.
- `daily_study_hours`: Optional float constrained to `0.0 <= hours <= 24.0` (`ge=0.0, le=24.0`). Negative hours or values over 24 are rejected automatically with `HTTP 422 Unprocessable Entity`.
- `learning_preference`: Optional string, `1 <= len <= 50`.

---

## 6. Automated Test Results

Test suite: `backend/tests/test_profile.py` (along with `test_auth.py` and `test_database.py`)

Command executed:
```bash
python -m pytest -v
```

Output:
```text
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
collected 32 items

tests/test_auth.py::test_register_successfully PASSED                    [  3%]
tests/test_auth.py::test_password_stored_as_hash PASSED                  [  6%]
tests/test_auth.py::test_duplicate_email_rejected PASSED                 [  9%]
tests/test_auth.py::test_default_profile_created_on_registration PASSED  [ 12%]
tests/test_auth.py::test_login_successfully PASSED                       [ 15%]
tests/test_auth.py::test_wrong_password_rejected PASSED                  [ 18%]
tests/test_auth.py::test_unknown_email_rejected PASSED                   [ 21%]
tests/test_auth.py::test_get_me_with_valid_jwt PASSED                    [ 25%]
tests/test_auth.py::test_missing_token_rejected PASSED                   [ 28%]
tests/test_auth.py::test_invalid_token_rejected PASSED                   [ 31%]
tests/test_auth.py::test_expired_token_rejected PASSED                   [ 34%]
tests/test_auth.py::test_password_hash_never_appears_in_api_response PASSED [ 37%]
tests/test_database.py::test_database_initialization_all_eight_tables PASSED [ 40%]
tests/test_database.py::test_insert_user PASSED                          [ 43%]
tests/test_database.py::test_unique_user_email PASSED                    [ 46%]
tests/test_database.py::test_user_profile_relationship PASSED            [ 50%]
tests/test_database.py::test_user_subject_relationship PASSED            [ 53%]
tests/test_database.py::test_subject_topic_relationship PASSED           [ 56%]
tests/test_database.py::test_study_plan_relationships_and_json PASSED    [ 59%]
tests/test_database.py::test_quiz_and_quiz_attempt_relationships_and_json PASSED [ 62%]
tests/test_database.py::test_progress_relationships PASSED               [ 65%]
tests/test_database.py::test_api_health_and_docs_endpoints PASSED        [ 68%]
tests/test_profile.py::test_authenticated_user_can_get_profile PASSED    [ 71%]
tests/test_profile.py::test_unauthenticated_get_rejected PASSED          [ 75%]
tests/test_profile.py::test_authenticated_user_can_update_profile PASSED [ 78%]
tests/test_profile.py::test_updated_values_are_persisted PASSED          [ 81%]
tests/test_profile.py::test_partial_update_works PASSED                  [ 84%]
tests/test_profile.py::test_unauthenticated_put_rejected PASSED          [ 87%]
tests/test_profile.py::test_user_cannot_modify_another_users_profile PASSED [ 90%]
tests/test_profile.py::test_missing_profile_handled_correctly PASSED     [ 93%]
tests/test_profile.py::test_invalid_daily_study_hours_rejected PASSED    [ 96%]
tests/test_profile.py::test_password_hash_never_appears_in_profile_response PASSED [100%]

======================== 32 passed, 1 warning in 6.97s ========================
```
