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

class CaregiverLinkRequest(BaseModel):
    senior_id: str

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

@router.post("/{caregiver_id}/link-senior")
def link_senior_to_caregiver(
    caregiver_id: str,
    request: CaregiverLinkRequest,
    user=Depends(get_current_user)
):
    """Link a senior to this caregiver"""
    # Verify the caregiver is linking to their own account
    if user.id != caregiver_id:
        raise HTTPException(
            status_code=403,
            detail="You can only link seniors to your own account"
        )
    
    # Create link
    result = crud.create_caregiver_link(caregiver_id, request.senior_id)
    
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Failed to link senior to caregiver"
        )
    
    return {
        "success": True,
        "message": f"Senior {request.senior_id} linked to caregiver",
        "link": result
    }

class CompleteOnboardingRequest(BaseModel):
    senior_name: str
    senior_phone: str
    relationship: str

@router.post("/{caregiver_id}/complete-onboarding")
def complete_onboarding(
    caregiver_id: str,
    request: CompleteOnboardingRequest,
    user=Depends(get_current_user)
):
    """
    Called at the end of caregiver onboarding.
    Creates a placeholder senior profile + caregiver_links entry
    so the dashboard can immediately fetch data.
    """
    if user.id != caregiver_id:
        raise HTTPException(
            status_code=403,
            detail="You can only complete onboarding for your own account"
        )

    result = crud.complete_caregiver_onboarding(
        caregiver_id=caregiver_id,
        senior_name=request.senior_name,
        senior_phone=request.senior_phone,
        relationship=request.relationship,
    )

    if not result:
        raise HTTPException(
            status_code=400,
            detail="Failed to complete onboarding. Please try again."
        )

    return result