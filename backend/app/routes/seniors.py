from fastapi import APIRouter, HTTPException
from app.models.senior import SeniorCreate, Senior
from app.db import crud

router = APIRouter()

@router.post("/", response_model=Senior)
def create_seniors(senior: SeniorCreate):
    result = crud.create_senior(senior.name, senior.age)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to create senior")
    return result

@router.get("/{senior_id}", response_model=Senior)
def get_senior(senior_id: int):
    result = crud.get_senior(senior_id)
    if not result:
        raise HTTPException(status_code=404, detail="Senior not found")
    return result