
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models import User
from backend.core.dependencies import (
    get_current_doctor,
    get_current_patient,
)
from backend.schemas.access import (
    AccessDecision,
    AccessRequestResponse,
)
from backend.services.access_service import (
    request_patient_access,
    get_patient_access_requests,
    update_access_request,
)


router = APIRouter(
    prefix="/api/access",
    tags=["Doctor-Patient Access"],
)


# Doctor requests access to a patient's records
@router.post(
    "/request/{patient_id}",
    response_model=AccessRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_access_request(
    patient_id: int,
    current_user: User = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    return request_patient_access(
        patient_id=patient_id,
        current_user=current_user,
        db=db,
    )


# Patient views incoming access requests
@router.get(
    "/requests",
    response_model=list[AccessRequestResponse],
)
def get_access_requests(
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    return get_patient_access_requests(
        current_user=current_user,
        db=db,
    )


# Patient approves or revokes a request
@router.patch(
    "/requests/{request_id}",
    response_model=AccessRequestResponse,
)
def update_request(
    request_id: int,
    decision: AccessDecision,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    return update_access_request(
        request_id=request_id,
        new_status=decision.status,
        current_user=current_user,
        db=db,
    )
