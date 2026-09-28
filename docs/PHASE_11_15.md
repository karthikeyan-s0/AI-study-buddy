# AI StudyBuddy — Phases 11–15: Quizzes, Progress Tracking & Learning Dashboard

## 1. Overview
Phases 11 through 15 complete the core educational intelligence features of the AI StudyBuddy platform:
1. **Phase 11 — AI Quiz Generation**: Dynamic creation of college-level 4-option multiple-choice quizzes for any subject topic using Gemini 3.8 Flash.
2. **Phase 12 — Deterministic Quiz Scoring Engine**: Strict, server-side mathematical grading of student attempts. LLMs are never used for scoring to guarantee zero hallucinations and accurate assessment.
3. **Phase 13 — Progress Tracking**: Topic completion percentage and accumulated study time recording with automatic topic status synchronization.
4. **Phase 14 — AI Performance Analysis**: Student weakness identification, strengths profiling, and actionable study recommendations powered by Gemini analysis of quiz attempt trends.
5. **Phase 15 — Aggregated Student Learning Dashboard**: A unified overview providing student profile metrics, overall progress, subject breakdown, upcoming exam countdowns, recent quiz scores, and weak/strong topics.

---

## 2. API Endpoints

### Phase 11: Quiz Generation & Retrieval
- **`POST /quizzes/generate`**
  - **Auth**: Required (`Bearer <JWT>`)
  - **Request Body**:
    ```json
    {
      "subject_id": 1,
      "topic": "TCP/IP Protocol",
      "difficulty": "medium",
      "number_of_questions": 5
    }
    ```
  - **Response (201 Created)**: Returns the generated Quiz entity with `questions_json` array containing question text, 4 options (A, B, C, D), correct answers, and educational explanations.

- **`GET /quizzes`**
  - **Auth**: Required (`Bearer <JWT>`)
  - **Query Params**: `subject_id` (optional)
  - **Response**: List of quizzes created for the student's subjects.

- **`GET /quizzes/{quiz_id}`**
  - **Auth**: Required (`Bearer <JWT>`)
  - **Response**: Details of the specific quiz.

### Phase 12: Deterministic Quiz Submission & Attempts
- **`POST /quizzes/{quiz_id}/submit`**
  - **Auth**: Required (`Bearer <JWT>`)
  - **Request Body**:
    ```json
    {
      "answers": {
        "0": "B",
        "1": "A",
        "2": "C"
      }
    }
    ```
  - **Grading Mechanism**: Pure deterministic Python matching. Verifies answer key against `questions_json`, calculates integer `score`, `total_questions`, float `percentage`, and builds structured question-by-question feedback with explanations.
  - **Persistence**: Records an entry in the `quiz_attempts` table.
  - **Response (200 OK)**:
    ```json
    {
      "attempt_id": 1,
      "quiz_id": 1,
      "score": 3,
      "total_questions": 3,
      "percentage": 100.0,
      "feedback": [
        {
          "question_index": 0,
          "question": "Which layer...",
          "selected_answer": "B",
          "correct_answer": "B",
          "is_correct": true,
          "explanation": "..."
        }
      ],
      "attempted_at": "2026-09-28T05:25:00Z"
    }
    ```

- **`GET /quizzes/{quiz_id}/attempts`**
  - **Auth**: Required (`Bearer <JWT>`)
  - **Response**: Historical attempts by the current user for that quiz.

### Phase 13: Progress Tracking
- **`POST /progress`**
  - **Auth**: Required (`Bearer <JWT>`)
  - **Request Body**:
    ```json
    {
      "subject_id": 1,
      "topic_id": 2,
      "completion_percentage": 100.0,
      "study_minutes": 45
    }
    ```
  - **Logic**: Upserts progress row, accumulates `study_minutes`, updates `last_studied` timestamp, and automatically transitions `topic.status` to `"completed"` (if 100%) or `"in_progress"` (if > 0%).

- **`GET /progress`**
  - Lists all progress records for the authenticated student.
- **`GET /progress/subjects/{subject_id}`**
  - Lists progress records filtered by subject.
- **`GET /progress/topics/{topic_id}`**
  - Retrieves specific progress for a given topic.

### Phase 14: AI Performance Analysis
- **`POST /ai/performance/analyze`**
  - **Auth**: Required (`Bearer <JWT>`)
  - **Request Body**:
    ```json
    {
      "subject_id": 1
    }
    ```
  - **Logic**: Queries student's quiz attempts, averages scores per topic, builds an academic diagnostic prompt for Gemini, and returns structured strengths, weak topics, and concrete study recommendations.

### Phase 15: Aggregated Dashboard
- **`GET /dashboard`**
  - **Auth**: Required (`Bearer <JWT>`)
  - **Response**: Aggregated summary combining profile, subject completion percentages, upcoming exam dates, recent quiz performance, weak and strong topics, and dynamic study advice.

---

## 3. Data Integrity & Tenant Isolation
- All endpoints strictly isolate tenant data using `get_current_user`.
- Foreign key traversals (`Quiz -> Subject -> User`, `Progress -> Subject -> User`) verify that students cannot view, submit to, or alter records belonging to other users.
- Input models are protected against client-controlled `user_id` injection using Pydantic's `extra="forbid"`.
