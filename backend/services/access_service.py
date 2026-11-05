
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from backend.models import Doctor, Patient, DoctorPatientAccess, User


def request_patient_access(
    patient_id: int,
    current_user: User,
    db: Session,
):
    """Create or renew a doctor's request for patient access."""

    doctor = (
        db.query(Doctor)
        .filter(Doctor.user_id == current_user.id)
        .first()
    )

    if doctor is None:
        raise HTTPException(
            status_code=403,
            detail="Doctor profile not found.",
        )

    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found.",
        )

    if patient.user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot request access to your own profile.",
        )

    access = (
        db.query(DoctorPatientAccess)
        .filter(
            DoctorPatientAccess.doctor_id == doctor.id,
            DoctorPatientAccess.patient_id == patient_id,
        )
        .first()
    )

    if access:
        if access.status == "pending":
            raise HTTPException(
                status_code=409,
                detail="An access request is already pending.",
            )

        if access.status == "approved":
            raise HTTPException(
                status_code=409,
                detail="You already have approved access.",
            )

        # A revoked request can be submitted again.
        access.status = "pending"
        access.created_at = datetime.now(timezone.utc)

    else:
        access = DoctorPatientAccess(
            doctor_id=doctor.id,
            patient_id=patient_id,
            status="pending",
        )
        db.add(access)

    try:
        db.commit()
        db.refresh(access)
        return access

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="An access request already exists.",
        )

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not create the access request.",
        )


def get_patient_access_requests(
    current_user: User,
    db: Session,
):
    """Return all access requests received by the logged-in patient."""

    patient = (
        db.query(Patient)
        .filter(Patient.user_id == current_user.id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=403,
            detail="Patient profile not found.",
        )

    return (
        db.query(DoctorPatientAccess)
        .filter(DoctorPatientAccess.patient_id == patient.id)
        .order_by(DoctorPatientAccess.created_at.desc())
        .all()
    )


def update_access_request(
    request_id: int,
    new_status: str,
    current_user: User,
    db: Session,
):
    """Allow a patient to approve or revoke an access request."""

    patient = (
        db.query(Patient)
        .filter(Patient.user_id == current_user.id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=403,
            detail="Patient profile not found.",
        )

    access = (
        db.query(DoctorPatientAccess)
        .filter(
            DoctorPatientAccess.id == request_id,
            DoctorPatientAccess.patient_id == patient.id,
        )
        .first()
    )

    if access is None:
        raise HTTPException(
            status_code=404,
            detail="Access request not found.",
        )

    if new_status not in ("approved", "revoked"):
        raise HTTPException(
            status_code=400,
            detail="Invalid access status.",
        )

    if access.status == "revoked" and new_status == "approved":
        raise HTTPException(
            status_code=409,
            detail="A revoked request cannot be approved again. The doctor must submit a new request.",
        )

    if access.status == "pending" and new_status == "revoked":
        raise HTTPException(
            status_code=409,
            detail="A pending request cannot be revoked. Rejecting requests is not yet supported.",
        )

    if access.status == new_status:
        raise HTTPException(
            status_code=409,
            detail=f"Access request is already {new_status}.",
        )

    access.status = new_status

    try:
        db.commit()
        db.refresh(access)
        return access

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not update the access request.",
        )
