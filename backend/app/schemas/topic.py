from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class TopicBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Topic name")
    status: Optional[str] = Field("not_started", max_length=20, description="Topic status (not_started, in_progress, completed)")
    difficulty: Optional[str] = Field("medium", max_length=20, description="Topic difficulty level (easy, medium, hard)")

class TopicCreate(TopicBase):
    pass

class TopicUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Topic name")
    status: Optional[str] = Field(None, max_length=20, description="Topic status (not_started, in_progress, completed)")
    difficulty: Optional[str] = Field(None, max_length=20, description="Topic difficulty level")

class TopicResponse(BaseModel):
    id: int
    subject_id: int
    name: str
    status: str
    difficulty: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
