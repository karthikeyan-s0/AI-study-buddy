from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class SubjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Subject name")
    description: Optional[str] = Field(None, max_length=500, description="Brief description of the subject")
    exam_date: Optional[date] = Field(None, description="Upcoming examination date (YYYY-MM-DD)")
    difficulty: Optional[str] = Field("medium", max_length=30, description="Subject difficulty level (easy, medium, hard)")

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Subject name")
    description: Optional[str] = Field(None, max_length=500, description="Brief description of the subject")
    exam_date: Optional[date] = Field(None, description="Upcoming examination date (YYYY-MM-DD)")
    difficulty: Optional[str] = Field(None, max_length=30, description="Subject difficulty level")

class SubjectResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    exam_date: Optional[date]
    difficulty: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
