from datetime import date, datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict

class StudyPlanGenerateRequest(BaseModel):
    subject_id: int = Field(..., description="ID of the subject to generate a plan for")
    start_date: Optional[date] = Field(None, description="Start date of the study plan (defaults to current date)")
    end_date: Optional[date] = Field(None, description="Target completion or exam date")

class StudyPlanResponse(BaseModel):
    id: int
    user_id: int
    subject_id: int
    title: str
    start_date: Optional[date]
    end_date: Optional[date]
    plan_json: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
