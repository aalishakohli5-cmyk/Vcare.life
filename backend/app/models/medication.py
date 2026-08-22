from pydantic import BaseModel
from typing import Optional, Any

class MedicationCreate(BaseModel):
    senior_id: str
    name: str
    dosage: Optional[str] = None
    scheduled_time: str

class MedicationUpdate(BaseModel):
    name: Optional[str] = None
    dosage: Optional[str] = None
    scheduled_time: Optional[str] = None
    taken: Optional[bool] = None
    taken_at: Optional[Any] = None

class Medications(MedicationCreate):
    id: Any
    taken: Optional[bool] = False
    taken_at: Optional[Any] = None
    created_at: Optional[Any] = None
 