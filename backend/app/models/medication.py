from pydantic import BaseModel
#from typing import Optional

class MedicationCreate(BaseModel):
    senior_id: str
    name: str
    dosage: str
    scheduled_time: str

class Medications(MedicationCreate):
    id: int 