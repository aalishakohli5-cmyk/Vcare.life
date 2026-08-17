from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from app.models.caregiver import CaregiverCreate, Caregiver
from app.models.senior import Profile
from app.db import crud
from app.core.security import get_current_user

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

@router.get("/{caregiver_id}/seniors", response_model=List[dict])
def get_seniors_for_caregiver(caregiver_id: str, user=Depends(get_current_user)):
    """Fetch all seniors assigned to this caregiver"""
    # Get caregiver_links for this caregiver
    links = crud.get_seniors_for_caregiver(caregiver_id)
    if links is None:
        raise HTTPException(status_code=500, detail="Failed to fetch seniors")
    
    # Fetch full profiles for each senior
    seniors = []
    for link in links:
        senior = crud.get_profile(link.get('senior_id'))
        if senior:
            seniors.append(senior)
    
    return seniors