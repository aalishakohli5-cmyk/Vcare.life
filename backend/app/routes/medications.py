from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.medication import MedicationCreate, Medications
from app.db import crud
from app.core.security import get_current_user, verify_caregiver_access


router = APIRouter()

@router.post("/", response_model=Medications)
def create_meds(
    med: MedicationCreate,
    user=Depends(get_current_user)
):
    """Create medication for a senior (requires valid auth token)"""
    # Verify the caregiver has access to this senior
    try:
        verify_caregiver_access(user.id, med.senior_id)
    except HTTPException:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to create medications for this senior"
        )
    
    result = crud.create_medications(
        med.senior_id,
        med.name,
        med.dosage,
        med.scheduled_time
    )
    
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Failed to create medication"
        )
    
    return result

@router.get("/{senior_id}", response_model=List[Medications])

def get_meds(senior_id: str, user=Depends(get_current_user)):
    verify_caregiver_access(user.id, senior_id)
    result = crud.get_medications_senior(senior_id)

    if not result:
        raise HTTPException(status_code=404, detail="Medications not found")
    return result