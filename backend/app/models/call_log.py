from pydantic import BaseModel
from typing import Optional

class CallLogCreate(BaseModel):
    id: Optional[int] = None
    status: str
    senior_id: int
    transcript: Optional[str] = None #completed, failed, none
    distress_detected: Optional[bool] = None

class CallLog(CallLogCreate):
    id: int