from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse

router = APIRouter(tags=["Subjects"])

@router.post(
    "",
    response_model=SubjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new study subject",
    description="Creates a subject under the authenticated student's account."
)
def create_subject(
    subject_in: SubjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subject = Subject(
        user_id=current_user.id,
        name=subject_in.name,
        description=subject_in.description,
        exam_date=subject_in.exam_date,
        difficulty=subject_in.difficulty or "medium"
    )
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject

@router.get(
    "",
    response_model=List[SubjectResponse],
    summary="List all subjects for current student",
    description="Returns all subjects belonging to the authenticated student."
)
def list_subjects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Subject).filter(Subject.user_id == current_user.id).all()

@router.get(
    "/{subject_id}",
    response_model=SubjectResponse,
    summary="Get subject by ID",
    description="Fetches details of a specific subject belonging to the authenticated student."
)
def get_subject(
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
    return subject

@router.put(
    "/{subject_id}",
    response_model=SubjectResponse,
    summary="Update subject by ID",
    description="Updates subject details (e.g. name, exam date, difficulty) for the authenticated student."
)
def update_subject(
    subject_id: int,
    subject_in: SubjectUpdate,
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

    update_data = subject_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(subject, field, value)

    subject.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(subject)
    return subject

@router.delete(
    "/{subject_id}",
    summary="Delete subject by ID",
    description="Permanently removes a subject and its associated data for the authenticated student."
)
def delete_subject(
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

    db.delete(subject)
    db.commit()
    return {"message": "Subject deleted successfully"}
