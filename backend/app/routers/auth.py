from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.profile import Profile
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(tags=["Authentication"])

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new student account",
    description="Registers a new user, hashes their password, and creates an associated default profile."
)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password securely
    hashed_pwd = hash_password(user_in.password)

    # Create user and default profile
    new_user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=hashed_pwd
    )

    try:
        db.add(new_user)
        db.flush()  # Populates new_user.id

        default_profile = Profile(
            user_id=new_user.id,
            education_level="College",
            daily_study_hours=2.0,
            learning_preference="Visual"
        )
        db.add(default_profile)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        ) from e

@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate and obtain JWT token",
    description="Validates email and password, returning a signed JWT Bearer access token."
)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    return Token(access_token=access_token, token_type="bearer")

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user details",
    description="Returns the authenticated user's safe profile details based on Bearer token."
)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
