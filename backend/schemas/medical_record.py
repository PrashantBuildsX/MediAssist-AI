
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MedicalRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    uploaded_by: int
    original_filename: str
    mime_type: str
    file_size: int
    processing_status: str
    created_at: datetime
