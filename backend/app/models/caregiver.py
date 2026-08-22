from pydantic import BaseModel
from typing import Optional, Any

class CaregiverCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    relationship: Optional[str] = None

class Caregiver(CaregiverCreate):
    id: str