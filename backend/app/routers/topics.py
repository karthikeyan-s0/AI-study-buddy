from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.subject import Subject
from app.models.topic import Topic
from app.schemas.topic import TopicCreate, TopicUpdate, TopicResponse

router = APIRouter(tags=["Topics"])

@router.post(
    "/subjects/{subject_id}/topics",
    response_model=TopicResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new topic under a subject",
    description="Creates a study topic for the given subject, verifying ownership by the authenticated student."
)
def create_topic(
    subject_id: int,
    topic_in: TopicCreate,
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

    topic = Topic(
        subject_id=subject.id,
        name=topic_in.name,
        status=topic_in.status or "not_started",
        difficulty=topic_in.difficulty or "medium"
    )
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic

@router.get(
    "/subjects/{subject_id}/topics",
    response_model=List[TopicResponse],
    summary="List all topics for a subject",
    description="Returns all topics belonging to the student's specified subject."
)
def list_topics(
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

    return db.query(Topic).filter(Topic.subject_id == subject.id).all()

@router.get(
    "/topics/{topic_id}",
    response_model=TopicResponse,
    summary="Get topic by ID",
    description="Fetches a specific topic verifying ownership through its associated subject."
)
def get_topic(
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
    return topic

@router.put(
    "/topics/{topic_id}",
    response_model=TopicResponse,
    summary="Update topic by ID",
    description="Partially updates topic attributes (e.g., status, difficulty, name). Subject assignment cannot be altered."
)
def update_topic(
    topic_id: int,
    topic_in: TopicUpdate,
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

    update_data = topic_in.model_dump(exclude_unset=True)
    update_data.pop("subject_id", None)  # Prevent client from altering subject association

    for field, value in update_data.items():
        setattr(topic, field, value)

    topic.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(topic)
    return topic

@router.delete(
    "/topics/{topic_id}",
    summary="Delete topic by ID",
    description="Permanently deletes a topic verifying ownership through its associated subject."
)
def delete_topic(
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

    db.delete(topic)
    db.commit()
    return {"message": "Topic deleted successfully"}
