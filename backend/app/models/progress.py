from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="SET NULL"), nullable=True, index=True)
    completion_percentage = Column(Float, default=0.0, nullable=False)
    study_minutes = Column(Integer, default=0, nullable=False)
    last_studied = Column(DateTime(timezone=True), default=utc_now, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="progress_records")
    subject = relationship("Subject", back_populates="progress_records")
    topic = relationship("Topic", back_populates="progress_records")

    def __repr__(self):
        return f"<Progress id={self.id} user_id={self.user_id} subject_id={self.subject_id} %={self.completion_percentage}>"
