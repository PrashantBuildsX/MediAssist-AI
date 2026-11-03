
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from backend.models import User, Patient, Doctor
from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)


def register_user(data, db: Session):
    # Check whether email is already registered
    existing_user = db.query(User).filter(
        User.email == data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered."
        )

    # Create common user account
    new_user = User(
        full_name=data.full_name,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role,
    )

    try:
        db.add(new_user)
        db.flush()

        # Create role-specific profile
        if data.role == "patient":
            profile = Patient(
                user_id=new_user.id,
                date_of_birth=data.date_of_birth,
                gender=data.gender,
            )

        else:
            profile = Doctor(
                user_id=new_user.id,
                specialization=data.specialization,
                license_number=data.license_number,
            )

        db.add(profile)
        db.commit()
        db.refresh(new_user)

        return new_user

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Registration conflicts with an existing record."
        )

    except Exception:
        db.rollback()
        raise


def login_user(data, db: Session):
    # Find user by email
    user = db.query(User).filter(
        User.email == data.email
    ).first()

    # Verify password
    if not user or not verify_password(
        data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive."
        )

    # Generate JWT
    access_token = create_access_token({
        "sub": str(user.id),
        "role": user.role,
    })

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }
