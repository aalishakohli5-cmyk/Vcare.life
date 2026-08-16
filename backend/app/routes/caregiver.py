from fastapi import APIRouter, HTTPException
from app.models.caregiver import CaregiverCreate, Caregiver
from app.db import crud

router = APIRouter()

@router.post("/", response_model=Caregiver)

def create_caregiver(cg: CaregiverCreate):
    result = crud.create_caregiver(cg.name, cg.email, cg.phone)

    if not result:
        raise HTTPException(status_code=400, detail="Failed to create Caregiver")
    return result

@router.get("/{caregiver_id}", response_model=Caregiver)

def get_caregiver(caregiver_id: int):
    result = crud.get_caregiver(caregiver_id)

    if not result:
        raise HTTPException(status_code=404, detail="Caregiver not found")
    return result