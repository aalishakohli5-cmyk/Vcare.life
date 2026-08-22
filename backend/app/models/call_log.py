from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class CallLogCreate(BaseModel):
    senior_id: str
    status: str
    call_id: Optional[str] = None
    transcript: Optional[str] = None
    duration: Optional[int] = None
    distress_detected: Optional[bool] = False

class CallLog(CallLogCreate):
    id: Any
    created_at: Optional[Any] = None