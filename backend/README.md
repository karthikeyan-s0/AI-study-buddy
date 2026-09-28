# AI StudyBuddy Backend

AI-augmented backend system for college students, built with FastAPI, SQLAlchemy, and SQLite (PostgreSQL-compatible).

## Running the Application

```bash
# Navigate to backend directory
cd backend

# Run the FastAPI server
python -m uvicorn app.main:app --reload --port 8000
```

- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Running Tests

```bash
# Run pytest with verbose output
python -m pytest -v
```
