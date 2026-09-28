from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    status = Column(String(20), default="not_started", nullable=False)  # not_started, in_progress, completed
    difficulty = Column(String(20), default="medium", nullable=False)  # easy, medium, hard
    created_at = Column(DateTime(timezone=True), default=utc_now, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, server_default=func.now())

    # Relationships
    subject = relationship("Subject", back_populates="topics")
    progress_records = relationship("Progress", back_populates="topic")

    def __repr__(self):
        return f"<Topic id={self.id} name='{self.name}' status='{self.status}'>"
