# AI StudyBuddy — Phase 5: Subject Management Documentation

## 1. Subject Architecture

The Subject domain represents academic courses/subjects enrolled by students. In the relational hierarchy:
- Each **User** owns multiple **Subjects** (`User 1 ── N Subjects`).
- Downstream entities such as **Topics**, **StudyPlans**, **Quizzes**, and **Progress** branch directly from `Subject`.

```text
┌─────────────────┐             1 : N             ┌──────────────────┐
│      User       │ ────────────────────────────> │     Subject      │
│  (Auth Entity)  │ <──────────────────────────── │ (Academic Topic) │
└─────────────────┘                               └────────┬─────────┘
                                                           │ 1 : N
                                                  (Topics / Plans / Quizzes)
```

---

## 2. CRUD Endpoints

| Method | Endpoint | Protection | Description | Status Codes |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/subjects` | `Bearer <JWT>` | Creates a new subject for the authenticated student | 201, 401, 422 |
| `GET` | `/subjects` | `Bearer <JWT>` | Lists all subjects belonging to the student | 200, 401 |
| `GET` | `/subjects/{subject_id}` | `Bearer <JWT>` | Fetches a specific subject by ID | 200, 401, 404 |
| `PUT` | `/subjects/{subject_id}` | `Bearer <JWT>` | Partially updates subject details | 200, 401, 404, 422 |
| `DELETE` | `/subjects/{subject_id}` | `Bearer <JWT>` | Permanently removes a subject | 200, 401, 404 |

---

## 3. Authentication & Ownership Protection

Multi-tenant student isolation is strictly enforced across every operation:
- **Automatic Binding**: In `POST /subjects`, `user_id` is assigned directly from `current_user.id`. The client cannot pass or override `user_id`.
- **Query Scoping**: Queries for listing, reading, updating, or deleting filter exclusively by:
  ```python
  Subject.id == subject_id, Subject.user_id == current_user.id
  ```
- **Uniform 404 Behavior**: If a student queries an ID belonging to another student, the API returns `404 Not Found` rather than `403 Forbidden` to prevent object enumeration or ID sniffing.

---

## 4. Request & Response Schemas

### `SubjectCreate` (Request Body)
```json
{
  "name": "Operating Systems",
  "description": "OS principles and internals",
  "exam_date": "2026-10-15",
  "difficulty": "medium"
}
```

### `SubjectUpdate` (Request Body — Partial Update)
```json
{
  "difficulty": "hard"
}
```

### `SubjectResponse` (Response Body)
```json
{
  "id": 1,
  "user_id": 3,
  "name": "Operating Systems",
  "description": "OS principles and internals",
  "exam_date": "2026-10-15",
  "difficulty": "hard",
  "created_at": "2026-09-28T05:06:50.899368",
  "updated_at": "2026-09-28T05:06:50.931750"
}
```

---

## 5. Input Validation Rules

Enforced via Pydantic V2 in [`app/schemas/subject.py`](file:///C:/Users/Biosp/.gemini/antigravity/scratch/studybuddy/backend/app/schemas/subject.py):
- `name`: Required string, `1 <= len <= 100`. Empty strings or inputs over 100 characters trigger `HTTP 422 Unprocessable Entity`.
- `description`: Optional string, `len <= 500`.
- `exam_date`: Optional standard ISO date (`YYYY-MM-DD`).
- `difficulty`: Optional string, `len <= 30` (defaults to `"medium"`).

---

## 6. Automated Test Results

Test suite: `backend/tests/test_subjects.py` (running with `test_profile.py`, `test_auth.py`, `test_database.py`)

Command executed:
```bash
python -m pytest -v
```

Output:
```text
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
collected 45 items

tests/test_auth.py::test_register_successfully PASSED                    [  2%]
tests/test_auth.py::test_password_stored_as_hash PASSED                  [  4%]
tests/test_auth.py::test_duplicate_email_rejected PASSED                 [  6%]
tests/test_auth.py::test_default_profile_created_on_registration PASSED  [  8%]
tests/test_auth.py::test_login_successfully PASSED                       [ 11%]
tests/test_auth.py::test_wrong_password_rejected PASSED                  [ 13%]
tests/test_auth.py::test_unknown_email_rejected PASSED                   [ 15%]
tests/test_auth.py::test_get_me_with_valid_jwt PASSED                    [ 17%]
tests/test_auth.py::test_missing_token_rejected PASSED                   [ 20%]
tests/test_auth.py::test_invalid_token_rejected PASSED                   [ 22%]
tests/test_auth.py::test_expired_token_rejected PASSED                   [ 24%]
tests/test_auth.py::test_password_hash_never_appears_in_api_response PASSED [ 26%]
tests/test_database.py::test_database_initialization_all_eight_tables PASSED [ 28%]
tests/test_database.py::test_insert_user PASSED                          [ 31%]
tests/test_database.py::test_unique_user_email PASSED                    [ 33%]
tests/test_database.py::test_user_profile_relationship PASSED            [ 35%]
tests/test_database.py::test_user_subject_relationship PASSED            [ 37%]
tests/test_database.py::test_subject_topic_relationship PASSED           [ 40%]
tests/test_database.py::test_study_plan_relationships_and_json PASSED    [ 42%]
tests/test_database.py::test_quiz_and_quiz_attempt_relationships_and_json PASSED [ 44%]
tests/test_database.py::test_progress_relationships PASSED               [ 46%]
tests/test_database.py::test_api_health_and_docs_endpoints PASSED        [ 48%]
tests/test_profile.py::test_authenticated_user_can_get_profile PASSED    [ 51%]
tests/test_profile.py::test_unauthenticated_get_rejected PASSED          [ 53%]
tests/test_profile.py::test_authenticated_user_can_update_profile PASSED [ 55%]
tests/test_profile.py::test_updated_values_are_persisted PASSED          [ 57%]
tests/test_profile.py::test_partial_update_works PASSED                  [ 60%]
tests/test_profile.py::test_unauthenticated_put_rejected PASSED          [ 62%]
tests/test_profile.py::test_user_cannot_modify_another_users_profile PASSED [ 64%]
tests/test_profile.py::test_missing_profile_handled_correctly PASSED     [ 66%]
tests/test_profile.py::test_invalid_daily_study_hours_rejected PASSED    [ 68%]
tests/test_profile.py::test_password_hash_never_appears_in_profile_response PASSED [ 71%]
tests/test_subjects.py::test_authenticated_user_can_create_subject PASSED [ 73%]
tests/test_subjects.py::test_unauthenticated_create_rejected PASSED      [ 75%]
tests/test_subjects.py::test_authenticated_user_can_list_own_subjects PASSED [ 77%]
tests/test_subjects.py::test_user_cannot_see_another_users_subjects PASSED [ 80%]
tests/test_subjects.py::test_authenticated_user_can_get_own_subject PASSED [ 82%]
tests/test_subjects.py::test_getting_another_users_subject_returns_404 PASSED [ 84%]
tests/test_subjects.py::test_authenticated_user_can_update_own_subject PASSED [ 86%]
tests/test_subjects.py::test_partial_update_works PASSED                 [ 88%]
tests/test_subjects.py::test_user_cannot_update_another_users_subject PASSED [ 91%]
tests/test_subjects.py::test_authenticated_user_can_delete_own_subject PASSED [ 93%]
tests/test_subjects.py::test_deleted_subject_cannot_be_retrieved PASSED  [ 95%]
tests/test_subjects.py::test_deleting_another_users_subject_returns_404 PASSED [ 97%]
tests/test_subjects.py::test_invalid_subject_data_rejected PASSED        [100%]

======================= 45 passed, 1 warning in 16.18s ========================
```
