from fastapi import APIRouter, HTTPException, Depends
from app.models.senior import Profile, ProfileUpdate
from app.db import crud
from app.core.security import get_current_user, verify_caregiver_access
from typing import Optional

router = APIRouter()

@router.post("/", response_model=Profile)
def create_or_update_senior_profile(
    full_name: str,
    email: str,
    phone: Optional[str] = None,
    date_of_birth: Optional[str] = None,
    gender: Optional[str] = None,
    emergency_contact_name: Optional[str] = None,
    emergency_contact_phone: Optional[str] = None,
    user=Depends(get_current_user)
):
    """Create or update senior profile during onboarding"""
    result = crud.create_or_update_senior_profile(
        user_id=user.id,
        full_name=full_name,
        email=email,
        phone=phone,
        date_of_birth=date_of_birth,
        gender=gender,
        emergency_contact_name=emergency_contact_name,
        emergency_contact_phone=emergency_contact_phone
    )
    
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Failed to create senior profile"
        )
    return result

@router.get("/{senior_id}", response_model=Profile)
def get_senior(senior_id: str, user=Depends(get_current_user)):
    verify_caregiver_access(user.id, senior_id)
    result = crud.get_profile(senior_id)
    if not result:
        raise HTTPException(status_code=404, detail="Senior profile not found")
    return result

@router.put("/{senior_id}", response_model=Profile)
def update_senior_profile(senior_id: str, updates: ProfileUpdate, user=Depends(get_current_user)):
    verify_caregiver_access(user.id, senior_id)
    data = updates.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    result = crud.update_profile(senior_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Senior profile not found")
    return result
