# AI StudyBuddy — Phase 6 & 7: Topics + Gemini AI Service Documentation

## 1. Topic Model Fields Discovered

The existing SQLAlchemy model [`app/models/topic.py`](file:///C:/Users/Biosp/.gemini/antigravity/scratch/studybuddy/backend/app/models/topic.py) was inspected and served as the source of truth:

| Field Name | Type | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- |
| `id` | `Integer` | Primary Key, Indexed | Unique topic identifier |
| `subject_id` | `Integer` | Foreign Key (`subjects.id`, `CASCADE`), Indexed, Non-null | Parent subject reference |
| `name` | `String(100)` | Non-null | Name of the study topic |
| `status` | `String(20)` | Default: `"not_started"`, Non-null | Study lifecycle state (`not_started`, `in_progress`, `completed`) |
| `difficulty` | `String(20)` | Default: `"medium"`, Non-null | Difficulty level (`easy`, `medium`, `hard`) |
| `created_at` | `DateTime(timezone=True)` | Default: UTC now | Creation timestamp |
| `updated_at` | `DateTime(timezone=True)` | Default: UTC now, on update: UTC now | Last update timestamp |

---

## 2. Relational Hierarchy: Subject ── Topics

```text
┌─────────────────┐             1 : N             ┌──────────────────┐
│      User       │ ────────────────────────────> │     Subject      │
│  (Auth Entity)  │ <──────────────────────────── │ (Academic Topic) │
└─────────────────┘                               └────────┬─────────┘
                                                           │ 1 : N
                                                  ┌────────▼─────────┐
                                                  │      Topic       │
                                                  │ (Granular Unit)  │
                                                  └──────────────────┘
```

- Each **Subject** has many **Topics**.
- Deleting a `Subject` triggers `cascade="all, delete-orphan"`, automatically cleaning up child topics.
- Topics cannot exist orphaned from their parent subject.

---

## 3. Topic CRUD Endpoints

| Method | Endpoint | Protection | Description | Status Codes |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/subjects/{subject_id}/topics` | `Bearer <JWT>` | Creates a topic under the authenticated student's subject | 201, 401, 404, 422 |
| `GET` | `/subjects/{subject_id}/topics` | `Bearer <JWT>` | Lists all topics for the authenticated student's subject | 200, 401, 404 |
| `GET` | `/topics/{topic_id}` | `Bearer <JWT>` | Fetches a specific topic verifying ownership through its subject | 200, 401, 404 |
| `PUT` | `/topics/{topic_id}` | `Bearer <JWT>` | Partially updates topic attributes (`status`, `difficulty`, `name`) | 200, 401, 404, 422 |
| `DELETE` | `/topics/{topic_id}` | `Bearer <JWT>` | Permanently removes a topic | 200, 401, 404 |

---

## 4. Topic Ownership & Security Architecture

Ownership is verified along the relational path:
```text
JWT ──> get_current_user() ──> current_user.id ──> Subject.user_id ──> Topic.subject_id
```

1. **Creation**: When creating a topic via `POST /subjects/{subject_id}/topics`, the backend explicitly checks that `Subject.id == subject_id and Subject.user_id == current_user.id`.
2. **Access / Mutate / Delete**: Endpoints querying by `topic_id` join with `Subject` and assert `Subject.user_id == current_user.id`.
3. **Immutable Parent**: `PUT /topics/{topic_id}` strips `subject_id` from the update payload, preventing clients from transferring topics between subjects.
4. **Information Hiding**: If a resource belongs to another user or does not exist, `404 Not Found` is returned uniformly.

---

## 5. Gemini AI Service Layer Architecture

The AI layer in [`app/services/gemini_service.py`](file:///C:/Users/Biosp/.gemini/antigravity/scratch/studybuddy/backend/app/services/gemini_service.py) decouples LLM interactions from API routers:

```text
┌───────────────────────┐
│     FastAPI Router    │ (Auth, validation, business logic)
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│     GeminiService     │ (Prompt formatting, response parsing, error handling)
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Google Gemini REST API│ (Models: gemini-3.8-flash, secure headers)
└───────────────────────┘
```

- **Client Technology**: High-performance HTTP client via `httpx` with timeout management (default: 60s).
- **Header Authentication**: Uses `x-goog-api-key: <key>` header rather than query string parameters to prevent key leakage in request URLs or proxy logs.
- **Structured JSON Support**: Supports `responseMimeType: "application/json"` with automatic JSON decoding.

---

## 6. Gemini Configuration & Secrets Protection

- Loaded through `app.core.config.Settings` from `.env`.
- Environment keys: `GEMINI_API_KEY` and `GEMINI_MODEL` (default: `"gemini-3.8-flash"`).
- **Graceful Degradation**: Application boots cleanly even if `GEMINI_API_KEY` is empty; errors are raised only when an AI generation method is invoked.
- **Key Masking**: In all exceptions and logs, secret keys are never included in error strings, responses, or stack traces.

---

## 7. Error Handling

- `GeminiConfigurationError`: Raised with user-friendly guidance if the API key is not configured.
- `GeminiAPIError`: Handles HTTP 4xx/5xx from the provider, empty responses, malformed JSON, and timeouts cleanly without leaking raw tracebacks.
- Timeouts (`httpx.TimeoutException`) map to: `"AI service request timed out. Please try again."`
- Network failures (`httpx.RequestError`) map to: `"Unable to connect to AI service. Please check network connectivity."`

---

## 8. Mock Testing Strategy

All tests in [`tests/test_gemini_service.py`](file:///C:/Users/Biosp/.gemini/antigravity/scratch/studybuddy/backend/tests/test_gemini_service.py) mock `httpx.Client.post`:
- Zero external network requests are made during automated test runs.
- Mocks simulate successful text generation, structured JSON generation, empty candidate lists, HTTP 500 errors, read timeouts, network connection errors, and verify that the API key never leaks in error text.

---

## 9. Automated Test Results

Command executed:
```bash
python -m pytest -v
```

Output:
```text
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
collected 69 items

tests/test_auth.py: 12 passed
tests/test_database.py: 10 passed
tests/test_gemini_service.py: 9 passed
tests/test_profile.py: 10 passed
tests/test_subjects.py: 13 passed
tests/test_topics.py: 15 passed

======================= 69 passed, 1 warning in 24.39s ========================
```
