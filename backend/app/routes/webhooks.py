from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.db import crud

router = APIRouter()

class CallResult(BaseModel):
    call_id: str
    senior_id: str
    status: str
    duration: int
    transcript: Optional[str] = None

@router.post("/")
async def receive_call_request(result: CallResult):

    print("Received call request", result)

    log = crud.create_call_log(
        senior_id= result.senior_id,
        status= result.status,
        transcript= result.transcript
    )
    if not log:
        return {"status": "error", "detail": "failed to save call log"}
    
    return {"status": "received", "call_log_id": log["id"]}