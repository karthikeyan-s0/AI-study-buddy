from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class ProfileUpdate(BaseModel):
    education_level: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Education level, e.g., High School, College, Graduate"
    )
    daily_study_hours: Optional[float] = Field(
        None,
        ge=0.0,
        le=24.0,
        description="Daily available study hours (0.0 to 24.0)"
    )
    learning_preference: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Learning style preference, e.g., Visual, Auditory, Reading, Kinesthetic"
    )

class ProfileResponse(BaseModel):
    id: int
    user_id: int
    education_level: str
    daily_study_hours: float
    learning_preference: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
