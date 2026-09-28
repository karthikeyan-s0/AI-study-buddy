from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(String(100), nullable=False)
    difficulty = Column(String(20), default="medium", nullable=False)
    questions_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, server_default=func.now())

    # Relationships
    subject = relationship("Subject", back_populates="quizzes")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Quiz id={self.id} topic='{self.topic}' difficulty='{self.difficulty}'>"
