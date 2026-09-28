from datetime import datetime
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field, ConfigDict

class QuestionOption(BaseModel):
    A: str
    B: str
    C: str
    D: str

class QuizQuestion(BaseModel):
    question: str
    options: Dict[str, str]
    correct_answer: str = Field(..., pattern="^[A-D]$", description="Correct option key (A, B, C, or D)")
    explanation: Optional[str] = "No explanation provided."

class QuizGenerateRequest(BaseModel):
    subject_id: int = Field(..., description="ID of the subject to generate a quiz for")
    topic: str = Field(..., min_length=1, max_length=100, description="Topic name for the quiz")
    difficulty: Optional[str] = Field("medium", pattern="^(easy|medium|hard)$", description="Difficulty level")
    number_of_questions: Optional[int] = Field(5, ge=1, le=20, description="Number of questions (1 to 20)")

class QuizResponse(BaseModel):
    id: int
    subject_id: int
    topic: str
    difficulty: str
    questions_json: List[Dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class QuizSubmitRequest(BaseModel):
    answers: Dict[str, str] = Field(..., description="Map of question index to chosen option, e.g. {'0': 'A', '1': 'C'}")

class QuestionFeedback(BaseModel):
    question_index: int
    question: str
    selected_answer: Optional[str]
    correct_answer: str
    is_correct: bool
    explanation: str

class QuizSubmitResponse(BaseModel):
    attempt_id: int
    quiz_id: int
    score: int
    total_questions: int
    percentage: float
    feedback: List[QuestionFeedback]
    attempted_at: datetime

class QuizAttemptResponse(BaseModel):
    id: int
    quiz_id: int
    user_id: int
    score: int
    total_questions: int
    percentage: float
    answers_json: Dict[str, Any]
    attempted_at: datetime

    model_config = ConfigDict(from_attributes=True)
