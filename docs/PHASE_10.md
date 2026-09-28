# AI StudyBuddy — Phase 10: AI Q&A Assistant Documentation

## 1. Objective
The AI Q&A Assistant provides an interactive, educational study support endpoint where college students can ask subject-matter questions and receive clear, structured, pedagogical explanations with code snippets, analogies, and examples without exposing provider credentials or raw LLM errors.

---

## 2. Endpoint
```http
POST /ai/ask
```
- **Tag**: `AI`
- **Authentication**: Required (`Bearer <JWT>`)
- **Rate/Request Guard**: Enforces payload size restrictions and sanitization

---

## 3. Request Schema (`AskRequest`)
Defined in [`app/schemas/ai.py`](file:///C:/Users/Biosp/.gemini/antigravity/scratch/studybuddy/backend/app/schemas/ai.py):

| Field | Type | Required | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `question` | `str` | Yes | `1 <= len <= 2000`, non-whitespace | The academic question being asked |
| `context` | `str` | No | `len <= 5000` | Optional educational context, student level, or syllabus details |

- Input strings are automatically stripped of surrounding whitespace.
- Configured with `extra="forbid"` to reject unauthorized fields such as `user_id`.

---

## 4. Response Schema (`AskResponse`)
```json
{
  "answer": "Normalization is a database design technique..."
}
```

---

## 5. Authentication
- Secured via FastAPI's `get_current_user` dependency.
- Requires valid `Authorization: Bearer <JWT>`. Missing, invalid, or expired tokens return `401 Unauthorized`.

---

## 6. Gemini Prompt Design
The prompt builder in [`app/routers/ai.py`](file:///C:/Users/Biosp/.gemini/antigravity/scratch/studybuddy/backend/app/routers/ai.py) conditions Gemini to behave as an academic tutor:
- Explains concepts in accessible student-friendly language.
- Employs step-by-step breakdowns, analogies, and minimal code examples where relevant.
- Avoids unnecessary filler or conversational tangents.
- Refuses to invent facts or leak internal system instructions and API keys.

---

## 7. Request Flow
```text
Student Client
      │
      │  POST /ai/ask { "question": "...", "context": "..." }
      ▼
FastAPI OAuth2Bearer Authentication (extracts & verifies JWT)
      │
      ▼
Pydantic Request Validation (trims whitespace, asserts bounds)
      │
      ▼
Prompt Builder (combines educational instructions + context + question)
      │
      ▼
Gemini Service Layer (app/services/gemini_service.py)
      │
      ▼
Google Gemini REST API (gemini-3.8-flash)
      │
      ▼
Output Sanitizer & Validator (verifies non-empty string)
      │
      ▼
Return HTTP 200 with AskResponse
```

---

## 8. Error Handling
- **Invalid/Empty Question**: Returns `HTTP 422 Unprocessable Content`.
- **Unauthenticated**: Returns `HTTP 401 Unauthorized`.
- **Empty Response from AI**: Returns `HTTP 502 Bad Gateway` (`AI service returned an empty response.`).
- **Gemini Timeout / Network / Provider Outage**: Returns safe `HTTP 503 Service Unavailable` (`AI service is temporarily unavailable. Please try again later.`), shielding raw Google API stack traces.

---

## 9. Security
- **No Client User ID**: Client-supplied `user_id` is rejected via `extra="forbid"`.
- **Header Authentication**: API key is passed to Gemini via `x-goog-api-key` header, avoiding presence in URL logs.
- **Credential Masking**: Secrets and JWT tokens are never forwarded to the LLM or exposed in API errors.
- **Stateless Operation**: No database changes or logging of sensitive queries were introduced in Phase 10.

---

## 10. Testing
Comprehensive test suite in [`tests/test_ai_ask.py`](file:///C:/Users/Biosp/.gemini/antigravity/scratch/studybuddy/backend/tests/test_ai_ask.py):
- 15 dedicated unit tests covering missing tokens, expired tokens, whitespace trimming, size boundary rejections, prompt argument verification, empty response handling, exception shielding, and payload constraint enforcement.
- Uses `unittest.mock.patch` to prevent real API calls during test runs.

---

## 11. Example Request & Response

### Request
```http
POST /ai/ask
Authorization: Bearer <valid_jwt_token>
Content-Type: application/json

{
  "question": "What is normalization in DBMS?",
  "context": "Explain it for a BCA student with a simple example."
}
```

### Response (HTTP 200)
```json
{
  "answer": "Normalization is a database design technique that organizes tables to reduce data redundancy and eliminate undesirable insertion, update, and deletion anomalies. For example, instead of storing student names and course details together in one big table, we divide them into two tables (Students and Courses) linked by a Student_ID."
}
```

---

## 12. How to Run
```powershell
cd C:\Users\Biosp\.gemini\antigravity\scratch\studybuddy\backend
python -m pytest -v
python -m uvicorn app.main:app --reload --port 8000
```
- Interactive Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
