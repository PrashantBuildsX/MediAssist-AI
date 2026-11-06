
from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse

from backend.database.connection import get_db
from backend.core.dependencies import (
    get_current_patient,
    get_current_doctor,
    get_current_user,
)
from backend.models import User
from backend.schemas.medical_record import MedicalRecordResponse

from backend.services.medical_record_service import (
    upload_medical_record,
    get_patient_medical_records,
    get_all_patient_records,
    get_medical_record_file_path,

)

router = APIRouter(
    prefix="/api/medical-records",
    tags=["Medical Records"],
)


@router.post(
    "/upload",
    response_model=MedicalRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_record(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    """
    Allow an authenticated patient to upload their own medical record.
    """

    record = await upload_medical_record(
        upload_file=file,
        current_user=current_user,
        db=db,
    )

    return record





@router.get(
    "/my-records",
    response_model=list[MedicalRecordResponse],
)
def list_my_records(
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    """
    Retrieve all medical records belonging to the authenticated patient.
    """

    records = get_patient_medical_records(
        current_user=current_user,
        db=db,
    )

    return records



@router.get(
    "/patient/{patient_id}",
    response_model=list[MedicalRecordResponse],
)
def get_patient_records_for_doctor(
    patient_id: int,
    current_user: User = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    """
    Allow an authenticated doctor to view any patient's medical records.
    """

    records = get_all_patient_records(
        patient_id=patient_id,
        current_user=current_user,
        db=db,
    )

    return records




@router.get("/{record_id}/download")
def download_medical_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Allow patients to download their own records
    and doctors to download any patient's records.
    """

    record, file_path = get_medical_record_file_path(
        record_id=record_id,
        current_user=current_user,
        db=db,
    )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=record.original_filename,
    )
