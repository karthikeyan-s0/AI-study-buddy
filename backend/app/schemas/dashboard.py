from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class PerformanceAnalysisResponse(BaseModel):
    overall_summary: str
    strengths: List[str]
    weak_topics: List[str]
    recommendations: List[str]
    next_steps: List[str]

class StudentSummary(BaseModel):
    id: int
    name: str
    email: str
    education_level: str
    daily_study_hours: float
    learning_preference: str

class SubjectProgressItem(BaseModel):
    id: int
    name: str
    difficulty: str
    exam_date: Optional[str]
    topics_count: int
    completed_topics: int
    progress_percentage: float

class RecentAttemptItem(BaseModel):
    id: int
    quiz_id: int
    topic: str
    score: int
    total_questions: int
    percentage: float
    attempted_at: str

class DashboardResponse(BaseModel):
    student: StudentSummary
    overall_progress: float
    subjects: List[SubjectProgressItem]
    upcoming_exams: List[Dict[str, Any]]
    recent_quiz_attempts: List[RecentAttemptItem]
    study_plans_count: int
    weak_topics: List[str]
    strong_topics: List[str]
    recommendations: List[str]
