from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.subject import Subject
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.schemas.quiz import (
    QuizGenerateRequest,
    QuizResponse,
    QuizSubmitRequest,
    QuizSubmitResponse,
    QuizAttemptResponse,
)
from app.services.quiz_service import (
    generate_quiz_for_subject,
    calculate_and_record_quiz_attempt,
)

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])

@router.post(
    "/generate",
    response_model=QuizResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate AI quiz for a subject/topic",
    description="Generates a customized multiple-choice quiz using Gemini, validates structure, and saves to database."
)
def generate_quiz(
    req: QuizGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return generate_quiz_for_subject(
        db=db,
        current_user=current_user,
        subject_id=req.subject_id,
        topic=req.topic,
        difficulty=req.difficulty or "medium",
        num_questions=req.number_of_questions or 5
    )

@router.post(
    "/{quiz_id}/submit",
    response_model=QuizSubmitResponse,
    summary="Submit quiz answers for deterministic grading",
    description="Calculates score, percentage, and detailed question-by-question feedback on the backend. Saves attempt."
)
def submit_quiz(
    quiz_id: int,
    req: QuizSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return calculate_and_record_quiz_attempt(
        db=db,
        current_user=current_user,
        quiz_id=quiz_id,
        answers=req.answers
    )

@router.get(
    "",
    response_model=List[QuizResponse],
    summary="List all quizzes for current student",
    description="Returns all generated quizzes belonging to the student's subjects."
)
def list_quizzes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Quiz).join(Subject).filter(
        Subject.user_id == current_user.id
    ).all()

@router.get(
    "/{quiz_id}",
    response_model=QuizResponse,
    summary="Get quiz by ID",
    description="Fetches a specific quiz if owned by the authenticated student."
)
def get_quiz(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    quiz = db.query(Quiz).join(Subject).filter(
        Quiz.id == quiz_id,
        Subject.user_id == current_user.id
    ).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    return quiz

@router.get(
    "/{quiz_id}/attempts",
    response_model=List[QuizAttemptResponse],
    summary="Get previous attempts for a quiz",
    description="Returns all past submission attempts and scores for this quiz."
)
def get_quiz_attempts(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    quiz = db.query(Quiz).join(Subject).filter(
        Quiz.id == quiz_id,
        Subject.user_id == current_user.id
    ).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    return db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz.id,
        QuizAttempt.user_id == current_user.id
    ).order_by(QuizAttempt.attempted_at.desc()).all()
