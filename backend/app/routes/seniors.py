from fastapi import APIRouter, HTTPException, Depends
from app.models.senior import Profile, ProfileUpdate
from app.db import crud
from app.core.security import get_current_user

router = APIRouter()

@router.get("/{senior_id}", response_model=Profile)

def get_senior(senior_id: str, user=Depends(get_current_user)):
    result = crud.get_profile(senior_id)
    if not result:
        raise HTTPException(status_code=404, detail="Senior profile not found")
    return result

@router.put("/{senior_id}", response_model=Profile)

def update_senior_profile(senior_id: str, updates: ProfileUpdate, user=Depends(get_current_user)):
    data = updates.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    result = crud.update_profile(senior_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Senior profile not found")
    return result
