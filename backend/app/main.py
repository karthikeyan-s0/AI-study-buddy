from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
import app.models  # noqa: F401 - Register all models with Base.metadata

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize all database tables on application startup
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="AI StudyBuddy — Intelligent AI-Augmented Study Companion for College Students",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"], summary="Health check endpoint")
def health_check():
    """Health check endpoint to verify that the service is running."""
    return {
        "status": "ok",
        "service": "AI StudyBuddy API"
    }

from app.routers import auth, profile, subjects, topics, study_plans, ai, quizzes, progress, dashboard
app.include_router(auth.router, prefix="/auth")
app.include_router(profile.router, prefix="/profile")
app.include_router(subjects.router, prefix="/subjects")
app.include_router(topics.router)
app.include_router(study_plans.router)
app.include_router(ai.router)
app.include_router(quizzes.router)
app.include_router(progress.router)
app.include_router(dashboard.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
