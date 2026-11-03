
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models import User
from backend.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    TokenResponse,
)
from backend.services.auth_service import register_user, login_user
from backend.core.dependencies import get_current_user


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = register_user(data, db)

    return UserResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        role=user.role,
    )


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    result = login_user(data, db)

    return TokenResponse(
        access_token=result["access_token"],
        token_type=result["token_type"],
        user=UserResponse(
            id=result["user"].id,
            full_name=result["user"].full_name,
            email=result["user"].email,
            role=result["user"].role,
        )
    )


# Protected endpoint: returns the currently authenticated user
@router.get(
    "/me",
    response_model=UserResponse
)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return UserResponse(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        role=current_user.role,
    )
