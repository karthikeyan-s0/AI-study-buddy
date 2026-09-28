from app.schemas.auth import LoginRequest, Token, TokenPayload
from app.schemas.user import UserCreate, UserResponse
from app.schemas.profile import ProfileUpdate, ProfileResponse
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse
from app.schemas.topic import TopicCreate, TopicUpdate, TopicResponse
from app.schemas.study_plan import StudyPlanGenerateRequest, StudyPlanResponse
from app.schemas.ai import SummarizeRequest, SummarizeResponse, AskRequest, AskResponse
from app.schemas.quiz import (
    QuizGenerateRequest,
    QuizResponse,
    QuizSubmitRequest,
    QuizSubmitResponse,
    QuizAttemptResponse,
    QuestionFeedback,
)
from app.schemas.progress import ProgressCreate, ProgressUpdate, ProgressResponse
from app.schemas.dashboard import (
    DashboardResponse,
    PerformanceAnalysisResponse,
    StudentSummary,
    SubjectProgressItem,
    RecentAttemptItem,
)

__all__ = [
    "LoginRequest",
    "Token",
    "TokenPayload",
    "UserCreate",
    "UserResponse",
    "ProfileUpdate",
    "ProfileResponse",
    "SubjectCreate",
    "SubjectUpdate",
    "SubjectResponse",
    "TopicCreate",
    "TopicUpdate",
    "TopicResponse",
    "StudyPlanGenerateRequest",
    "StudyPlanResponse",
    "SummarizeRequest",
    "SummarizeResponse",
    "AskRequest",
    "AskResponse",
    "QuizGenerateRequest",
    "QuizResponse",
    "QuizSubmitRequest",
    "QuizSubmitResponse",
    "QuizAttemptResponse",
    "QuestionFeedback",
    "ProgressCreate",
    "ProgressUpdate",
    "ProgressResponse",
    "DashboardResponse",
    "PerformanceAnalysisResponse",
    "StudentSummary",
    "SubjectProgressItem",
    "RecentAttemptItem",
]
