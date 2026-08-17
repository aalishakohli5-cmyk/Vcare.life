from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.db import crud
from app.core.security import get_current_user
from app.models.call_log import CallLog

router = APIRouter()

@router.get("/{senior_id}", response_model=List[CallLog])
def get_senior_calls(senior_id: str, user=Depends(get_current_user)):
    """Fetch all call logs for a senior"""
    result = crud.get_call_logs_for_senior(senior_id)
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to fetch call logs")
    return result

@router.get("/")
def health_check():
    """Health check for calls endpoint"""
    return {"status": "healthy", "service": "calls"}