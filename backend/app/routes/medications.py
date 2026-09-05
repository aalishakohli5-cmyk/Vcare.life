from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.medication import MedicationCreate, MedicationUpdate, Medications
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

    if result is None:
        raise HTTPException(status_code=500, detail="Failed to fetch medications")
    return result

@router.put("/{medication_id}", response_model=Medications)
def update_med(
    medication_id: int,
    med: MedicationUpdate,
    user=Depends(get_current_user)
):
    """Update medication details or mark taken/pending"""
    medication = crud.get_medication(medication_id)
    if not medication:
        raise HTTPException(status_code=404, detail="Medication not found")
    verify_caregiver_access(user.id, medication["senior_id"])

    data = med.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    result = crud.update_medication(medication_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Medication not found or update failed")
    return result

@router.delete("/{medication_id}")
def delete_med(
    medication_id: int,
    user=Depends(get_current_user)
):
    """Delete a medication"""
    medication = crud.get_medication(medication_id)
    if not medication:
        raise HTTPException(status_code=404, detail="Medication not found")
    verify_caregiver_access(user.id, medication["senior_id"])

    success = crud.delete_medication(medication_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete medication")
    return {"success": True, "message": f"Medication {medication_id} deleted"}
