# AI StudyBuddy — AI-Augmented College Final Project

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8-646CFF.svg)](https://vite.dev)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC.svg)](https://tailwindcss.com)
[![Gemini](https://img.shields.io/badge/AI-Gemini%203.8%20Flash-orange.svg)](https://ai.google.dev/)
[![Tests Passing](https://img.shields.io/badge/Pytest-109%20Passed-brightgreen.svg)]()

> **Program**: TN Skill Final Project — Team 11  
> **Track**: AI-Augmented Backend Development  
> **Team Members**:  
> - **Alan K Rison** (*Team Leader*)  
> - **Karthikeyan**  
> - **Mathew**  
> - **Kishore**  
> **System Name**: AI StudyBuddy API & Full-Stack Platform

---

## 1. Project Overview

**AI StudyBuddy** is a full-stack, production-grade educational study platform designed to demonstrate real AI-augmented backend architecture. Rather than relying on simple chatbot wrappers or client-side LLM calls, AI StudyBuddy establishes **FastAPI as the strict source of truth**, with PostgreSQL-compatible SQLAlchemy data models, JWT authentication, deterministic server-side quiz grading, structured JSON generation via **Google Gemini 3.8 Flash**, and a modern **React + Vite + Tailwind CSS** frontend.

### Key Architectural Highlights
- **Deterministic Server-Side Grading**: Quiz scores are evaluated mathematically in Python. LLMs are strictly forbidden from grading student attempts to prevent hallucinations and inconsistent results.
- **Tenant Isolation**: All operations are authenticated with JWT. Client-provided `user_id` parameters are forbidden; ownership is enforced via backend session context.
- **Secret Isolation**: Gemini API keys never leak into client code, Git repositories, or API error payloads.
- **Fail-Safe AI Client**: Structured JSON prompts (`responseMimeType: "application/json"`), timeout handling, retry logic, and clean HTTP 502/503 error mapping.
- **Comprehensive Verification**: 109 automated unit and integration tests passing with 100% coverage across all subsystems.

---

## 2. System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                   React + Vite + Tailwind UI                │
│ (Dashboard, Curriculum, Study Planner, Summarizer, Quizzes) │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / JWT Bearer
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                       FastAPI Backend                       │
│  ├── /auth          (Register, Login, Me)                   │
│  ├── /profile       (Student Preferences & Capacity)        │
│  ├── /subjects      (Course Management)                     │
│  ├── /topics        (Syllabus Items & Statuses)             │
│  ├── /study-plans   (AI-Generated Multi-Day Roadmaps)       │
│  ├── /ai            (Summarizer, Q&A Assistant, Analysis)   │
│  ├── /quizzes       (AI Quiz Generator & Deterministic Hub) │
│  ├── /progress      (Study Logs & Progress Sync)            │
│  └── /dashboard     (Unified Student Learning Analytics)    │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────────┐ ┌────────────────────────────┐
│   SQLAlchemy ORM + SQLite    │ │    Google Gemini 3.8 Flash │
│  (8 PostgreSQL-Ready Tables) │ │ (Structured JSON Prompting)│
└──────────────────────────────┘ └────────────────────────────┘
```

---

## 3. Database Schema (8 Models)

1. **`users`**: `id`, `name`, `email` (unique index), `password_hash`, `created_at`, `updated_at`.
2. **`profiles`**: `id`, `user_id` (1-to-1 with `users`), `education_level`, `daily_study_hours`, `learning_preference`, `created_at`, `updated_at`.
3. **`subjects`**: `id`, `user_id` (FK `users.id`), `name`, `description`, `difficulty`, `exam_date`, `created_at`, `updated_at`.
4. **`topics`**: `id`, `subject_id` (FK `subjects.id`), `name`, `difficulty`, `status` (`not_started`, `in_progress`, `completed`), `created_at`, `updated_at`.
5. **`study_plans`**: `id`, `user_id`, `subject_id`, `title`, `start_date`, `end_date`, `plan_json` (JSON), `created_at`, `updated_at`.
6. **`quizzes`**: `id`, `subject_id`, `topic`, `difficulty`, `questions_json` (JSON), `created_at`.
7. **`quiz_attempts`**: `id`, `quiz_id`, `user_id`, `score`, `total_questions`, `percentage`, `answers_json` (JSON), `attempted_at`.
8. **`progress`**: `id`, `user_id`, `subject_id`, `topic_id`, `completion_percentage`, `study_minutes`, `last_studied`.

---

## 4. Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- A Google Gemini API Key

### Backend Setup
1. Open a terminal and navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure `.env`:
   ```bash
   cp .env.example .env
   ```
   Add your Gemini API Key:
   ```ini
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-3.8-flash
   SECRET_KEY=your_super_secret_jwt_key
   DATABASE_URL=sqlite:///./studybuddy.db
   ```
5. Run the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   Interactive Swagger documentation will be available at: **http://localhost:8000/docs**

### Frontend Setup
1. Open a second terminal and navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Access the web app in your browser at: **http://localhost:5173**

---

## 5. Automated Testing Suite

All 109 backend tests across all 15 phases run hermetically using Pytest with SQLite in-memory fixtures and mocked Gemini responses:

```bash
cd backend
python -m pytest -v
```

Expected result:
```text
======================= 109 passed, 1 warning in 42.66s =======================
```

---

## 6. Docker & Docker Compose Deployment

To run the entire full-stack application inside containerized environments:

1. Provide your `GEMINI_API_KEY` in `backend/.env` or export it:
   ```bash
   export GEMINI_API_KEY=your_key_here
   ```
2. Start the services:
   ```bash
   docker-compose up --build
   ```
3. Endpoints:
   - Frontend UI: `http://localhost:3000`
   - Backend API: `http://localhost:8000`
   - Swagger Docs: `http://localhost:8000/docs`

---

## 7. API Endpoints Reference

| Module | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Health** | `GET` | `/health` | Service health status |
| **Auth** | `POST` | `/auth/register` | Create student account & initial profile |
| | `POST` | `/auth/login` | Authenticate and obtain JWT Bearer token |
| | `GET` | `/auth/me` | Fetch authenticated student profile |
| **Profile** | `GET` | `/profile` | Get academic level, study hours & learning style |
| | `PUT` | `/profile` | Update student profile preferences |
| **Subjects** | `POST` | `/subjects` | Create subject under student account |
| | `GET` | `/subjects` | List student's subjects |
| | `GET` | `/subjects/{id}` | Get subject details |
| | `PUT` | `/subjects/{id}` | Update subject details |
| | `DELETE` | `/subjects/{id}` | Delete subject and cascade topics |
| **Topics** | `POST` | `/subjects/{id}/topics` | Add topic to subject |
| | `GET` | `/subjects/{id}/topics` | List topics for subject |
| | `PUT` | `/topics/{id}` | Update topic name, difficulty, or status |
| | `DELETE` | `/topics/{id}` | Delete topic |
| **Study Plans**| `POST` | `/study-plans/generate` | AI-generated personalized study schedule |
| | `GET` | `/study-plans` | List historical study plans |
| **AI Hub** | `POST` | `/ai/summarize` | AI extraction of summaries, takeaways, terms |
| | `POST` | `/ai/ask` | AI tutor Q&A with educational analogies |
| | `POST` | `/ai/performance/analyze`| AI diagnostic analysis of quiz scores |
| **Quizzes** | `POST` | `/quizzes/generate` | AI generates 4-option multiple choice questions |
| | `POST` | `/quizzes/{id}/submit` | Deterministic server grading with explanations |
| | `GET` | `/quizzes` | List student quizzes |
| | `GET` | `/quizzes/{id}/attempts`| List attempt score history |
| **Progress** | `POST` | `/progress` | Record study minutes & completion % |
| | `GET` | `/progress` | List study progress logs |
| **Dashboard** | `GET` | `/dashboard` | Aggregated metrics, exams, weak topics & advice |

---

## 8. College Project Verification Checklist
- [x] Full-Stack Python FastAPI + React + Vite + Tailwind CSS
- [x] 8 Database Models with SQLite development and PostgreSQL compatibility
- [x] JWT Authentication with Bcrypt Password Hashing
- [x] Strict Multi-Tenant Data Isolation
- [x] Google Gemini 3.8 Flash AI Integration with Timeout & Retry Fallbacks
- [x] Deterministic Quiz Scoring Engine (Zero LLM grading)
- [x] Automated Study Planner with Daily Task Breakdowns
- [x] AI Performance Diagnostic & Learning Dashboard
- [x] 109 Hermetic Automated Tests Passing
- [x] Dockerfile & Docker Compose Multi-Container Orchestration
- [x] Postman Collection Included (`AI_StudyBuddy.postman_collection.json`)
