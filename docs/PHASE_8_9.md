# AI StudyBuddy — Phase 8 & 9: AI Study Plan & Summarizer Documentation

## 1. Phase 8: AI Study Plan Generation

### Architecture
The study plan generator gathers holistic student context and queries Google Gemini to construct an achievable day-by-day revision schedule:

```text
┌─────────────────┐
│     Student     │ ──> POST /study-plans/generate {subject_id, start_date, end_date}
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│ Context Aggregator                           │
│  - Profile (Education, Daily Hours, Style)   │
│  - Subject (Name, Difficulty, Exam Date)     │
│  - Topics (Names, Status, Difficulties)      │
└────────┬─────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│ Gemini 3.8 Flash                             │
│  (Structured Prompt with JSON response mode) │
└────────┬─────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│ JSON Schema Validator                        │
│  - Checks keys ('days', 'title', 'summary')  │
│  - Validates non-empty schedule array        │
└────────┬─────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│ Database Persistence                         │
│  - Saves to study_plans (plan_json)          │
│  - Foreign keys: user_id, subject_id         │
└──────────────────────────────────────────────┘
```

### Context Integration
The prompt builder in [`app/services/study_plan_service.py`](file:///C:/Users/Biosp/.gemini/antigravity/scratch/studybuddy/backend/app/services/study_plan_service.py) synthesizes:
- **Student Profile**: Education level (e.g. College), daily study capacity in hours, and learning preference (e.g. Visual).
- **Subject Parameters**: Target course name, subject difficulty, and scheduled exam date.
- **Granular Topics**: Topic names, current lifecycle state (`not_started`, `in_progress`, `completed`), and difficulty ratings.
- **Time Constraints**: Hard cap ensuring total duration per day does not exceed `daily_study_hours * 60` minutes.

### JSON Validation & Database Storage
- The model output is validated through `validate_study_plan_json()` before persistence.
- Any malformed structure (e.g. missing `days` array) is rejected with `502 Bad Gateway`.
- Validated output is stored directly in the `study_plans.plan_json` column using SQLAlchemy's native `JSON` type.

### Ownership Protection
- Verifies `Subject.id == subject_id and Subject.user_id == current_user.id`.
- Rejects unauthorized subject IDs with `404 Not Found`.

---

## 2. Phase 9: AI Study Material Summarizer

### Architecture
The summarizer provides an educational synthesis service to convert dense study notes or textbook extracts into structured revision aids.

```text
Student Text ──> POST /ai/summarize ──> Prompt Builder ──> Gemini AI ──> Structured Summary
```

### Request & Response Schemas
- **`SummarizeRequest`**:
  - `content`: String (10 to 25,000 characters). Whitespace-only or empty strings are rejected with `422 Unprocessable Content`.
  - `summary_length`: Optional depth parameter (`"short"`, `"medium"`, `"detailed"`).
- **`SummarizeResponse`**:
  - `summary`: Concise, structured summary paragraph.
  - `key_points`: List of high-impact core takeaways.
  - `important_terms`: List of key terms and definitions.

### Prompt Strategy
Instructs Gemini to:
1. Preserve core factual and scientific concepts without fabricating information.
2. Filter redundant filler and verbose digressions.
3. Extract 3 to 7 bullet points and definitions.
4. Return strictly valid JSON matching the Pydantic schema.

### Error Handling & Key Shielding
- Service failures or timeouts from Gemini return clean `503 Service Unavailable` responses.
- Malformed AI outputs return `502 Bad Gateway`.
- Secret keys and low-level stack traces are never exposed in responses or logs.

---

## 3. Automated Test Results

Command executed:
```bash
python -m pytest -v
```

Output:
```text
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
collected 85 items

tests/test_ai.py: 7 passed
tests/test_auth.py: 12 passed
tests/test_database.py: 10 passed
tests/test_gemini_service.py: 9 passed
tests/test_profile.py: 10 passed
tests/test_study_plans.py: 9 passed
tests/test_subjects.py: 13 passed
tests/test_topics.py: 15 passed

======================= 85 passed, 1 warning in 31.33s =======================
```
