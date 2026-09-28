from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.study_plan import StudyPlan
from app.schemas.study_plan import StudyPlanGenerateRequest, StudyPlanResponse
from app.services.study_plan_service import generate_study_plan_for_subject

router = APIRouter(prefix="/study-plans", tags=["Study Plans"])

@router.post(
    "/generate",
    response_model=StudyPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate personalized AI study plan",
    description="Creates and persists a personalized daily study plan combining student preferences, subject details, and topics."
)
def generate_study_plan(
    req: StudyPlanGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return generate_study_plan_for_subject(
        db=db,
        current_user=current_user,
        subject_id=req.subject_id,
        start_date=req.start_date,
        end_date=req.end_date
    )

@router.get(
    "",
    response_model=List[StudyPlanResponse],
    summary="List all study plans for current student",
    description="Returns all study plans owned by the authenticated student."
)
def list_study_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(StudyPlan).filter(StudyPlan.user_id == current_user.id).all()

@router.get(
    "/{plan_id}",
    response_model=StudyPlanResponse,
    summary="Get study plan by ID",
    description="Returns a specific study plan if owned by the authenticated student."
)
def get_study_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plan = db.query(StudyPlan).filter(
        StudyPlan.id == plan_id,
        StudyPlan.user_id == current_user.id
    ).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study plan not found"
        )
    return plan
