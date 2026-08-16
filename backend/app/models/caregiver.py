from pydantic import BaseModel
from typing import Optional

class CaregiverCreate(BaseModel):
    name: str
    email: str
    phone: Optional[int] = None

class Caregiver(CaregiverCreate):
    id: int