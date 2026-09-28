from typing import Dict, Any, List
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.profile import Profile
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.study_plan import StudyPlan
from app.schemas.dashboard import (
    DashboardResponse,
    StudentSummary,
    SubjectProgressItem,
    RecentAttemptItem,
)
from app.services.progress_service import gather_student_stats

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get(
    "",
    response_model=DashboardResponse,
    summary="Get combined student learning dashboard",
    description="Returns an aggregated overview of subjects, topic progress, upcoming exams, quiz scores, and weak/strong topics."
)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    student_summary = StudentSummary(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        education_level=profile.education_level if profile else "College",
        daily_study_hours=profile.daily_study_hours if profile else 2.0,
        learning_preference=profile.learning_preference if profile else "Visual"
    )

    stats = gather_student_stats(db, current_user)
    subjects: List[Subject] = stats["subjects"]

    subject_progress_items = []
    total_completion_acc = 0.0

    for s in subjects:
        s_topics = [t for t in stats["topics"] if t.subject_id == s.id]
        total_t = len(s_topics)
        completed_t = sum(1 for t in s_topics if t.status == "completed")
        in_prog_t = sum(1 for t in s_topics if t.status == "in_progress")
        
        # Calculate subject percentage
        if total_t > 0:
            subj_pct = round(((completed_t + (0.5 * in_prog_t)) / total_t) * 100.0, 1)
        else:
            subj_pct = 0.0

        total_completion_acc += subj_pct
        subject_progress_items.append(
            SubjectProgressItem(
                id=s.id,
                name=s.name,
                difficulty=s.difficulty,
                exam_date=str(s.exam_date) if s.exam_date else None,
                topics_count=total_t,
                completed_topics=completed_t,
                progress_percentage=subj_pct
            )
        )

    overall_progress = round(total_completion_acc / len(subjects), 1) if subjects else 0.0

    # Upcoming exams
    upcoming_exams = []
    for s in subjects:
        if s.exam_date:
            upcoming_exams.append({
                "subject_id": s.id,
                "name": s.name,
                "exam_date": str(s.exam_date),
                "difficulty": s.difficulty
            })
    upcoming_exams.sort(key=lambda x: x["exam_date"])

    # Recent quiz attempts
    recent_attempts_items = []
    for a in stats["recent_attempts"]:
        recent_attempts_items.append(
            RecentAttemptItem(
                id=a.id,
                quiz_id=a.quiz_id,
                topic=a.quiz.topic,
                score=a.score,
                total_questions=a.total_questions,
                percentage=a.percentage,
                attempted_at=a.attempted_at.strftime("%Y-%m-%d %H:%M")
            )
        )

    # Study plans count
    plans_count = db.query(StudyPlan).filter(StudyPlan.user_id == current_user.id).count()

    # Dynamic recommendations
    recommendations = []
    if stats["weak_topics"]:
        recommendations.append(f"Focus today on your weakest area: {stats['weak_topics'][0].split(' ')[0]}.")
    if upcoming_exams:
        recommendations.append(f"Prepare for your upcoming exam in {upcoming_exams[0]['name']} on {upcoming_exams[0]['exam_date']}.")
    if plans_count == 0 and len(subjects) > 0:
        recommendations.append(f"Generate an AI Study Plan for {subjects[0].name} to pace your revision.")
    if len(recommendations) == 0:
        recommendations.append("Add subjects and start taking quizzes to unlock personalized daily recommendations!")

    return DashboardResponse(
        student=student_summary,
        overall_progress=overall_progress,
        subjects=subject_progress_items,
        upcoming_exams=upcoming_exams,
        recent_quiz_attempts=recent_attempts_items,
        study_plans_count=plans_count,
        weak_topics=stats["weak_topics"],
        strong_topics=stats["strong_topics"],
        recommendations=recommendations
    )
