from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.db import crud
from app.core.logging import logger

router = APIRouter()

class CallResult(BaseModel):
    call_id: str
    senior_id: str
    status: str
    duration: int
    transcript: Optional[str] = None

@router.post("/")
async def receive_call_request(result: CallResult):
    """Receive and log call results from Bland AI"""
    try:
        logger.info(
            f"Processing call result",
            extra={
                "call_id": result.call_id,
                "senior_id": result.senior_id,
                "status": result.status,
                "duration": result.duration
            }
        )

        log = crud.create_call_log(
            senior_id=result.senior_id,
            status=result.status,
            transcript=result.transcript
        )
        
        if not log:
            logger.error(
                f"Failed to save call log for senior {result.senior_id}"
            )
            return {
                "status": "error",
                "detail": "Failed to save call log"
            }
        
        logger.info(f"Call log saved: {log.get('id', 'unknown')}")
        return {
            "status": "received",
            "call_log_id": log["id"]
        }
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        return {
            "status": "error",
            "detail": "Webhook processing failed"
        }