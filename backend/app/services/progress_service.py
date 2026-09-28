from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.user import User
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.progress import Progress
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.services.gemini_service import get_gemini_service, GeminiServiceError

def record_or_update_progress(
    db: Session,
    current_user: User,
    subject_id: int,
    topic_id: Optional[int] = None,
    completion_percentage: float = 0.0,
    study_minutes: int = 0
) -> Progress:
    # 1. Verify subject ownership
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.user_id == current_user.id
    ).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )

    # 2. Verify topic if provided
    topic = None
    if topic_id is not None:
        topic = db.query(Topic).filter(
            Topic.id == topic_id,
            Topic.subject_id == subject.id
        ).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found"
            )
        if completion_percentage >= 100.0:
            topic.status = "completed"
        elif completion_percentage > 0.0 and topic.status == "not_started":
            topic.status = "in_progress"

    # 3. Check for existing progress record
    query = db.query(Progress).filter(
        Progress.user_id == current_user.id,
        Progress.subject_id == subject_id
    )
    if topic_id is not None:
        query = query.filter(Progress.topic_id == topic_id)
    else:
        query = query.filter(Progress.topic_id.is_(None))

    progress = query.first()

    now = datetime.now(timezone.utc)
    if progress:
        progress.completion_percentage = completion_percentage
        progress.study_minutes += study_minutes
        progress.last_studied = now
    else:
        progress = Progress(
            user_id=current_user.id,
            subject_id=subject_id,
            topic_id=topic_id,
            completion_percentage=completion_percentage,
            study_minutes=study_minutes,
            last_studied=now
        )
        db.add(progress)

    db.commit()
    db.refresh(progress)
    return progress

def gather_student_stats(db: Session, current_user: User) -> Dict[str, Any]:
    """Gather real statistics for student analytics and dashboard."""
    subjects = db.query(Subject).filter(Subject.user_id == current_user.id).all()
    subject_ids = [s.id for s in subjects]

    topics = db.query(Topic).filter(Topic.subject_id.in_(subject_ids)).all() if subject_ids else []
    
    # Progress records
    progress_records = db.query(Progress).filter(Progress.user_id == current_user.id).all()
    total_study_minutes = sum(p.study_minutes for p in progress_records)

    # Quiz attempts
    attempts = db.query(QuizAttempt).join(Quiz).filter(
        QuizAttempt.user_id == current_user.id
    ).order_by(QuizAttempt.attempted_at.desc()).all()

    total_attempts = len(attempts)
    avg_score = round(sum(a.percentage for a in attempts) / total_attempts, 1) if total_attempts > 0 else 0.0

    # Categorize topics
    topic_scores: Dict[str, List[float]] = {}
    for a in attempts:
        t_name = a.quiz.topic
        topic_scores.setdefault(t_name, []).append(a.percentage)

    weak_topics = []
    strong_topics = []

    for t_name, scores in topic_scores.items():
        avg_t = sum(scores) / len(scores)
        if avg_t < 60.0:
            weak_topics.append(f"{t_name} (Avg Quiz: {round(avg_t, 1)}%)")
        elif avg_t >= 80.0:
            strong_topics.append(f"{t_name} (Avg Quiz: {round(avg_t, 1)}%)")

    # Add hard topics that are not started
    for t in topics:
        if t.status == "not_started" and t.difficulty == "hard" and t.name not in [w.split(" ")[0] for w in weak_topics]:
            weak_topics.append(f"{t.name} (Unstarted Hard Topic)")
        elif t.status == "completed" and t.name not in [s.split(" ")[0] for s in strong_topics]:
            strong_topics.append(f"{t.name} (Completed)")

    return {
        "subjects": subjects,
        "topics": topics,
        "progress_records": progress_records,
        "total_study_minutes": total_study_minutes,
        "total_attempts": total_attempts,
        "avg_quiz_score": avg_score,
        "recent_attempts": attempts[:5],
        "weak_topics": weak_topics[:5],
        "strong_topics": strong_topics[:5]
    }

def run_ai_performance_analysis(db: Session, current_user: User) -> Dict[str, Any]:
    """Analyze student performance using Gemini and return structured educational guidance."""
    stats = gather_student_stats(db, current_user)
    gemini = get_gemini_service()

    if stats["total_attempts"] == 0 and len(stats["topics"]) == 0:
        return {
            "overall_summary": "Welcome to AI StudyBuddy! You have not yet added topics or taken quizzes. Add subjects and topics to receive personalized AI diagnostic performance insights.",
            "strengths": ["Getting started on AI StudyBuddy"],
            "weak_topics": ["No quiz attempts recorded yet"],
            "recommendations": [
                "Create your enrolled subjects and add course topics.",
                "Generate an AI Study Plan to establish a revision timetable.",
                "Take practice quizzes to identify conceptual knowledge gaps."
            ],
            "next_steps": [
                "Navigate to Subjects to add your current courses.",
                "Generate your first quiz."
            ]
        }

    prompt = f"""You are an educational AI performance coach for college students.
Analyze the following student performance metrics and provide actionable learning recommendations:

Student Performance Data:
- Total Subjects Enrolled: {len(stats['subjects'])}
- Total Topics Tracked: {len(stats['topics'])}
- Total Quiz Attempts: {stats['total_attempts']}
- Overall Average Quiz Score: {stats['avg_quiz_score']}%
- Total Recorded Study Minutes: {stats['total_study_minutes']}
- Identified High-Risk/Weak Topics: {stats['weak_topics'] or 'None identified'}
- Identified Strong Topics: {stats['strong_topics'] or 'None identified'}

Requirements:
1. Provide a constructive, motivating 2-3 sentence overall summary of their current mastery.
2. Highlight 2-4 key learning strengths.
3. Highlight 2-4 specific weak areas or unaddressed challenging topics.
4. Provide 3-5 concrete study recommendations (e.g. spaced repetition, active recall, problem solving).
5. Provide 2-3 immediate next steps for today's study session.
6. Return JSON ONLY with the exact following schema:
{{
  "overall_summary": "Summary string",
  "strengths": ["Strength 1", "Strength 2"],
  "weak_topics": ["Weak Topic 1", "Weak Topic 2"],
  "recommendations": ["Recommendation 1", "Recommendation 2"],
  "next_steps": ["Next Step 1", "Next Step 2"]
}}"""

    try:
        data = gemini.generate_json(prompt)
    except GeminiServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service temporarily unavailable: {str(e)}"
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to generate AI performance analysis."
        ) from e

    if not isinstance(data, dict) or "overall_summary" not in data:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service returned invalid performance analysis structure."
        )

    return {
        "overall_summary": str(data.get("overall_summary", "Performance analysis completed.")),
        "strengths": list(data.get("strengths", [])),
        "weak_topics": list(data.get("weak_topics", [])),
        "recommendations": list(data.get("recommendations", [])),
        "next_steps": list(data.get("next_steps", []))
    }
