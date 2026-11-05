
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.database.connection import get_db

from backend.core.security import decode_access_token
from backend.models import (
    User,
    Doctor,
    Patient,
    DoctorPatientAccess,
)


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    # Check whether Authorization header contains a token
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify JWT
    payload = decode_access_token(credentials.credentials)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user ID from JWT
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Retrieve user from PostgreSQL
    user = db.query(User).filter(User.id == user_id).first()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or account inactive.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user




def get_current_patient(
    current_user: User = Depends(get_current_user),
):
    """Allow access only to authenticated patients."""

    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patient access required.",
        )

    return current_user


def get_current_doctor(
    current_user: User = Depends(get_current_user),
):
    """Allow access only to authenticated doctors."""

    if current_user.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor access required.",
        )

    return current_user





def verify_doctor_patient_access(
    patient_id: int,
    current_user: User,
    db: Session,
):
    """
    Verify that a doctor has approved access to a patient.
    Returns the patient profile if access is allowed.
    """

    # Find the doctor's profile
    doctor = (
        db.query(Doctor)
        .filter(Doctor.user_id == current_user.id)
        .first()
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor profile not found.",
        )

    # Check whether the patient exists
    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    # Check whether approved access exists
    access = (
        db.query(DoctorPatientAccess)
        .filter(
            DoctorPatientAccess.doctor_id == doctor.id,
            DoctorPatientAccess.patient_id == patient_id,
            DoctorPatientAccess.status == "approved",
        )
        .first()
    )

    if access is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have approved access to this patient's records.",
        )

    return patient



