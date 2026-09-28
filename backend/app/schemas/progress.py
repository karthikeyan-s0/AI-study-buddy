from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class ProgressCreate(BaseModel):
    subject_id: int = Field(..., description="ID of the subject")
    topic_id: Optional[int] = Field(None, description="Optional ID of the topic")
    completion_percentage: float = Field(0.0, ge=0.0, le=100.0, description="Completion percentage (0.0 to 100.0)")
    study_minutes: int = Field(0, ge=0, description="Total minutes spent studying")

class ProgressUpdate(BaseModel):
    completion_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    study_minutes: Optional[int] = Field(None, ge=0)

class ProgressResponse(BaseModel):
    id: int
    user_id: int
    subject_id: int
    topic_id: Optional[int]
    completion_percentage: float
    study_minutes: int
    last_studied: datetime

    model_config = ConfigDict(from_attributes=True)
