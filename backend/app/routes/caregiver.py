from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from app.models.caregiver import CaregiverCreate, Caregiver
from app.models.senior import Profile
from app.db import crud
from app.core.security import get_current_user

router = APIRouter()

class CaregiverProfileCreate(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    relationship: Optional[str] = None

@router.post("/profile", response_model=Profile)
def create_or_update_caregiver_profile(
    data: CaregiverProfileCreate,
    user=Depends(get_current_user)
):
    """Create or update caregiver profile during onboarding"""
    result = crud.create_or_update_caregiver_profile(
        user_id=user.id,
        full_name=data.full_name,
        email=data.email,
        phone=data.phone,
        relationship=data.relationship
    )
    
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Failed to create caregiver profile"
        )
    return result

@router.post("/")
def create_caregiver(cg: CaregiverCreate):
    result = crud.create_caregiver(cg.name, cg.email, cg.phone)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to create Caregiver")
    return result

@router.get("/{caregiver_id}", response_model=Profile)
def get_caregiver(caregiver_id: str, user=Depends(get_current_user)):
    """Fetch caregiver profile"""
    result = crud.get_profile(caregiver_id)
    if not result:
        raise HTTPException(status_code=404, detail="Caregiver not found")
    return result

@router.get("/{caregiver_id}/seniors", response_model=List[dict])
def get_seniors_for_caregiver(caregiver_id: str, user=Depends(get_current_user)):
    """Fetch all seniors assigned to this caregiver"""
    # Verify the caregiver is requesting their own data
    if user.id != caregiver_id:
        raise HTTPException(
            status_code=403,
            detail="You can only view your own seniors"
        )
    
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
