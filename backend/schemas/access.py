
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class AccessDecision(BaseModel):
    status: Literal["approved", "revoked"]


class AccessRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    doctor_id: int
    patient_id: int
    status: str
    created_at: datetime
