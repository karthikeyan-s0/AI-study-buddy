# AI StudyBuddy — Phase 2: Database Layer Documentation

## 1. Database Architecture

The AI StudyBuddy persistence layer is built on **SQLAlchemy 2.0 ORM** with a decoupled, modular design that is engine-agnostic:
- **Local Development**: SQLite (`studybuddy.db`), with multi-threading support enabled (`check_same_thread: False`).
- **Production / Staging**: Drop-in compatible with PostgreSQL by swapping the `DATABASE_URL` connection string (e.g. `postgresql+psycopg2://user:password@host:5432/studybuddy`) without schema or ORM modifications.
- **Session Lifecycle**: Centralized `engine`, `SessionLocal`, declarative `Base`, and request-scoped `get_db()` dependency with clean session cleanup/closing.
- **Auto-Initialization**: Models are registered with `Base.metadata` in `app.models.__init__.py` and all 8 tables are created automatically on application startup via FastAPI's `lifespan` handler.

```text
┌─────────────────────────────────────────────────────────┐
│                      FastAPI App                        │
│                   (Lifespan Startup)                    │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
                 Base.metadata.create_all()
                             │
       ┌─────────────────────┴─────────────────────┐
       ▼                                           ▼
┌──────────────┐                            ┌──────────────┐
│ SQLite (Dev) │                            │ Postgres (Pr)│
└──────────────┘                            └──────────────┘
```

---

## 2. The Eight Tables

| Table Name | Purpose | Primary Key | Foreign Keys |
| :--- | :--- | :--- | :--- |
| `users` | User identity & credentials storage | `id` (Integer) | None |
| `profiles` | Student learning preferences and goals | `id` (Integer) | `user_id` -> `users.id` (Unique, 1-to-1) |
| `subjects` | Academic subjects managed by the student | `id` (Integer) | `user_id` -> `users.id` (1-to-N) |
| `topics` | Granular study topics belonging to subjects | `id` (Integer) | `subject_id` -> `subjects.id` (1-to-N) |
| `study_plans` | AI-generated timetable & revision plans | `id` (Integer) | `user_id`, `subject_id` |
| `quizzes` | Generated AI quizzes with question sets | `id` (Integer) | `subject_id` -> `subjects.id` |
| `quiz_attempts` | Student quiz submissions & score records | `id` (Integer) | `quiz_id`, `user_id` |
| `progress` | Topic completion % & study time tracker | `id` (Integer) | `user_id`, `subject_id`, `topic_id` (nullable) |

---

## 3. Relationships & Cascade Behavior

```mermaid
erDiagram
    USERS ||--|| PROFILES : has
    USERS ||--o{ SUBJECTS : owns
    SUBJECTS ||--o{ TOPICS : contains
    USERS ||--o{ STUDY_PLANS : creates
    SUBJECTS ||--o{ STUDY_PLANS : receives
    SUBJECTS ||--o{ QUIZZES : has
    QUIZZES ||--o{ QUIZ_ATTEMPTS : logs
    USERS ||--o{ QUIZ_ATTEMPTS : submits
    USERS ||--o{ PROGRESS : tracks
    SUBJECTS ||--o{ PROGRESS : measures
    TOPICS ||--o{ PROGRESS : details
```

### Cascade Policies
- **User Deletion**: Cascades (`cascade="all, delete-orphan"`, `ondelete="CASCADE"`) to delete associated `Profile`, `Subjects`, `StudyPlans`, `QuizAttempts`, and `Progress` records.
- **Subject Deletion**: Cascades to delete associated `Topics`, `StudyPlans`, `Quizzes`, and `Progress` records.
- **Quiz Deletion**: Cascades to delete associated `QuizAttempts`.
- **Topic Deletion**: `ondelete="SET NULL"` for `Progress.topic_id` so that historical study minutes for the subject remain preserved even if a specific topic is deleted.

---

## 4. Important Fields & Data Types

- **`users.email`**: Indexed with unique constraint (`unique=True, index=True`).
- **`users.password_hash`**: Secure storage placeholder for bcrypt hashes. Plaintext passwords are never persisted.
- **`profiles.education_level`**: Defaults to `"College"`.
- **`profiles.daily_study_hours`**: Float representing available daily study hours (default: `2.0`).
- **`profiles.learning_preference`**: Visual, Auditory, Reading/Writing, or Kinesthetic (default: `"Visual"`).
- **`subjects.difficulty`**: Enum values: `"easy"`, `"medium"`, `"hard"`.
- **`topics.status`**: Lifecycle states: `"not_started"`, `"in_progress"`, `"completed"`.
- **Timestamps**: All tables use timezone-aware timestamps with UTC defaults (`DateTime(timezone=True)`).

---

## 5. JSON Fields

SQLAlchemy's native `JSON` type is used for semi-structured data:
- **`study_plans.plan_json`**: Stores the structured day-by-day plan:
  ```json
  {
    "plan": [
      {
        "day": 1,
        "topic": "Processes",
        "duration_minutes": 120,
        "tasks": ["Process states", "PCB", "Practice questions"]
      }
    ]
  }
  ```
- **`quizzes.questions_json`**: Stores the question bank, options, correct answers, and explanations:
  ```json
  [
    {
      "question": "What is PCB in OS?",
      "options": {"A": "Process Control Block", "B": "Program Control Base"},
      "correct_answer": "A",
      "explanation": "PCB is the data structure holding process metadata."
    }
  ]
  ```
- **`quiz_attempts.answers_json`**: Stores the student's selected options:
  ```json
  {"1": "A", "2": "C"}
  ```

---

## 6. Testing Strategy

Isolated testing is enforced in `backend/tests/`:
- **In-Memory Test Database**: Configured in `tests/conftest.py` using `sqlite:///:memory:` with `StaticPool` to prevent touching the development database file `studybuddy.db`.
- **Dependency Overrides**: FastAPI's `get_db` dependency is overridden to inject the test session per test function.
- **Automated Test Coverage**:
  - `test_database_initialization_all_eight_tables`: Confirms metadata and physical table creation.
  - `test_insert_user`: Verifies record insertion and default timestamps.
  - `test_unique_user_email`: Validates duplicate rejection via `IntegrityError`.
  - `test_user_profile_relationship`: Verifies 1-to-1 mapping.
  - `test_user_subject_relationship`: Verifies 1-to-N subject mapping.
  - `test_subject_topic_relationship`: Verifies 1-to-N topic mapping.
  - `test_study_plan_relationships_and_json`: Verifies dual foreign keys and JSON serialization.
  - `test_quiz_and_quiz_attempt_relationships_and_json`: Verifies quiz execution links and JSON storage.
  - `test_progress_relationships`: Verifies 3-way relationship with user, subject, and topic.
  - `test_api_health_and_docs_endpoints`: Confirms `/health` and `/docs` work without regressions.

---

## 7. Future PostgreSQL Compatibility

The database layer adheres to PostgreSQL best practices:
1. **Types**: Uses standard ANSI SQL and SQLAlchemy types (`Integer`, `String`, `Text`, `Date`, `DateTime(timezone=True)`, `JSON`, `Float`).
2. **Foreign Keys**: Explicit naming conventions and standard `ondelete` actions (`CASCADE`, `SET NULL`).
3. **No SQLite Quirks**: Avoided SQLite-specific hacks, typeless columns, or dynamic type casting.
4. **Driver Transition**: Transitioning to PostgreSQL in a future phase requires solely setting `DATABASE_URL=postgresql+psycopg2://user:password@host:5432/dbname` in `.env`.
