from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.progress import Progress
from app.schemas.progress import ProgressCreate, ProgressResponse
from app.services.progress_service import record_or_update_progress

router = APIRouter(prefix="/progress", tags=["Progress"])

@router.post(
    "",
    response_model=ProgressResponse,
    status_code=status.HTTP_200_OK,
    summary="Record or update topic study progress",
    description="Updates completion percentage and increments study minutes for a given subject/topic."
)
def update_progress(
    req: ProgressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return record_or_update_progress(
        db=db,
        current_user=current_user,
        subject_id=req.subject_id,
        topic_id=req.topic_id,
        completion_percentage=req.completion_percentage,
        study_minutes=req.study_minutes
    )

@router.get(
    "",
    response_model=List[ProgressResponse],
    summary="List all progress records for current student",
    description="Returns all logged progress entries for the authenticated student."
)
def list_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Progress).filter(Progress.user_id == current_user.id).all()

@router.get(
    "/subjects/{subject_id}",
    response_model=List[ProgressResponse],
    summary="Get progress records for a specific subject",
    description="Returns progress records associated with a subject owned by the authenticated student."
)
def get_subject_progress(
    subject_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.user_id == current_user.id
    ).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    return db.query(Progress).filter(
        Progress.user_id == current_user.id,
        Progress.subject_id == subject_id
    ).all()

@router.get(
    "/topics/{topic_id}",
    response_model=ProgressResponse,
    summary="Get progress record for a specific topic",
    description="Returns progress for a topic owned by the authenticated student."
)
def get_topic_progress(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    topic = db.query(Topic).join(Subject).filter(
        Topic.id == topic_id,
        Subject.user_id == current_user.id
    ).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )

    progress = db.query(Progress).filter(
        Progress.user_id == current_user.id,
        Progress.topic_id == topic_id
    ).first()
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found for this topic"
        )
    return progress
