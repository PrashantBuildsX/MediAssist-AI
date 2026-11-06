
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.models import Patient, MedicalRecord, User


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Private storage directory
UPLOAD_DIR = PROJECT_ROOT / "uploads" / "medical_records"

# Maximum upload size: 10 MB
MAX_FILE_SIZE = 10 * 1024 * 1024

# Read files in 1 MB chunks
CHUNK_SIZE = 1024 * 1024


async def upload_medical_record(
    upload_file: UploadFile,
    current_user: User,
    db: Session,
):
    # Find the patient's profile
    patient = (
        db.query(Patient)
        .filter(Patient.user_id == current_user.id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found.",
        )

    # Validate filename and extension
    if not upload_file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required.",
        )

    if Path(upload_file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed.",
        )

    if len(upload_file.filename) > 255:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is too long.",
        )

    # Generate a unique server-side filename
    unique_filename = f"{uuid.uuid4().hex}.pdf"

    patient_directory = UPLOAD_DIR / f"patient_{patient.id}"
    final_path = patient_directory / unique_filename
    temp_path = patient_directory / f"{unique_filename}.part"

    file_size = 0
    first_chunk = b""

    try:
        # Create storage directory
        patient_directory.mkdir(parents=True, exist_ok=True)

        # Stream the uploaded file to temporary storage
        with temp_path.open("wb") as destination:
            while True:
                chunk = await upload_file.read(CHUNK_SIZE)

                if not chunk:
                    break

                if not first_chunk:
                    first_chunk = chunk[:5]

                file_size += len(chunk)

                if file_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="File size must not exceed 10 MB.",
                    )

                destination.write(chunk)

        # Validate that the file is actually a PDF
        if not first_chunk.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file is not a valid PDF.",
            )

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        # Move validated file to permanent storage
        temp_path.replace(final_path)

        # Save metadata in PostgreSQL
        record = MedicalRecord(
            patient_id=patient.id,
            uploaded_by=current_user.id,
            original_filename=upload_file.filename,
            storage_path=str(final_path),
            mime_type="application/pdf",
            file_size=file_size,
            processing_status="pending",
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record

    except HTTPException:
        if temp_path.exists():
            temp_path.unlink()

        if final_path.exists():
            final_path.unlink()

        raise

    except SQLAlchemyError:
        db.rollback()

        if temp_path.exists():
            temp_path.unlink()

        if final_path.exists():
            final_path.unlink()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save medical record metadata.",
        )

    except Exception:
        db.rollback()

        if temp_path.exists():
            temp_path.unlink()

        if final_path.exists():
            final_path.unlink()

        raise

    finally:
        await upload_file.close()



def get_patient_medical_records(
    current_user: User,
    db: Session,
):
    # Find the patient's profile
    patient = (
        db.query(Patient)
        .filter(Patient.user_id == current_user.id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found.",
        )

    # Retrieve only this patient's medical records
    records = (
        db.query(MedicalRecord)
        .filter(MedicalRecord.patient_id == patient.id)
        .order_by(MedicalRecord.created_at.desc())
        .all()
    )

    return records



def get_all_patient_records(
    patient_id: int,
    current_user: User,
    db: Session,
):
    # Verify that the patient exists
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

    # Retrieve all records belonging to this patient
    records = (
        db.query(MedicalRecord)
        .filter(MedicalRecord.patient_id == patient_id)
        .order_by(MedicalRecord.created_at.desc())
        .all()
    )

    return records




def get_medical_record_file_path(
    record_id: int,
    current_user: User,
    db: Session,
):
    # Find the requested medical record
    record = (
        db.query(MedicalRecord)
        .filter(MedicalRecord.id == record_id)
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found.",
        )

    # Patients can download only their own records
    if current_user.role == "patient":
        patient = (
            db.query(Patient)
            .filter(Patient.user_id == current_user.id)
            .first()
        )

        if patient is None or record.patient_id != patient.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to access this medical record.",
            )

    # Doctors can access any patient's records
    elif current_user.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to download medical records.",
        )

    # Resolve and validate the stored file path
    storage_root = UPLOAD_DIR.resolve()
    file_path = Path(record.storage_path).resolve()

    if not file_path.is_relative_to(storage_root):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid medical record storage path.",
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record file not found.",
        )

    return record, file_path
