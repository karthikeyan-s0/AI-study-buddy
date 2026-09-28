from datetime import date, datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.profile import Profile
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.study_plan import StudyPlan
from app.services.gemini_service import get_gemini_service, GeminiServiceError

def build_study_plan_prompt(
    profile: Optional[Profile],
    subject: Subject,
    topics: List[Topic],
    start_date: date,
    end_date: Optional[date]
) -> str:
    edu_level = profile.education_level if profile else "College"
    daily_hours = profile.daily_study_hours if profile else 2.0
    pref = profile.learning_preference if profile else "Visual"

    topics_info = []
    if topics:
        for t in topics:
            topics_info.append(f"- {t.name} (Difficulty: {t.difficulty}, Status: {t.status})")
    else:
        topics_info.append(f"- Comprehensive core fundamentals of {subject.name}")

    topics_text = "\n".join(topics_info)
    target_date_str = str(end_date) if end_date else (str(subject.exam_date) if subject.exam_date else "Flexible")

    return f"""You are an expert AI study planning assistant for college students.
Create a realistic, structured daily study plan.

Student Profile:
- Education Level: {edu_level}
- Daily Study Hours: {daily_hours} hours
- Learning Preference: {pref}

Subject:
- Name: {subject.name}
- Difficulty: {subject.difficulty}
- Exam Date: {subject.exam_date or 'Not scheduled'}

Topics:
{topics_text}

Schedule:
- Start Date: {start_date}
- Target Completion Date: {target_date_str}

Requirements:
1. Divide topics realistically across the available study days.
2. Total study time per day must not exceed {daily_hours * 60} minutes ({daily_hours} hours).
3. Include learning sessions, practical exercises, periodic revision, and a mock test before the exam.
4. Adapt explanations to a student who prefers {pref} learning.
5. Return JSON ONLY with the exact following schema:
{{
  "title": "Study Plan title (string)",
  "summary": "Short strategic summary (string)",
  "days": [
    {{
      "day": 1,
      "date": "{start_date}",
      "topics": [
        {{
          "topic": "Topic Name",
          "duration_minutes": 60,
          "activities": ["Read concept notes", "Practice exercises"]
        }}
      ]
    }}
  ]
}}"""

def validate_study_plan_json(data: Any) -> Dict[str, Any]:
    """Validate structure of generated study plan JSON."""
    if not isinstance(data, dict):
        raise ValueError("AI response must be a JSON object.")
    if "days" not in data or not isinstance(data["days"], list):
        raise ValueError("AI plan must contain a 'days' list.")
    if not data["days"]:
        raise ValueError("AI plan 'days' list cannot be empty.")
    if "title" not in data or not isinstance(data["title"], str):
        data["title"] = "AI Study Plan"
    return data

def generate_study_plan_for_subject(
    db: Session,
    current_user: User,
    subject_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> StudyPlan:
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

    # 2. Fetch student profile and topics
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    topics = db.query(Topic).filter(Topic.subject_id == subject.id).all()

    plan_start = start_date or date.today()
    plan_end = end_date or subject.exam_date

    # 3. Construct prompt
    prompt = build_study_plan_prompt(
        profile=profile,
        subject=subject,
        topics=topics,
        start_date=plan_start,
        end_date=plan_end
    )

    # 4. Call Gemini AI service
    gemini = get_gemini_service()
    try:
        raw_json = gemini.generate_json(prompt)
    except GeminiServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service temporarily unavailable: {str(e)}"
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to generate AI study plan."
        ) from e

    # 5. Validate AI response structure
    try:
        validated_plan = validate_study_plan_json(raw_json)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Invalid AI response structure: {str(e)}"
        ) from e

    # 6. Save StudyPlan to database
    title = str(validated_plan.get("title", f"{subject.name} Study Plan"))[:150]
    study_plan = StudyPlan(
        user_id=current_user.id,
        subject_id=subject.id,
        title=title,
        start_date=plan_start,
        end_date=plan_end,
        plan_json=validated_plan,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(study_plan)
    db.commit()
    db.refresh(study_plan)
    return study_plan
