from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class ProfileBase(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    date_of_birth: Optional[date] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    preferred_language: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    onboarding_complete: Optional[bool] = False

class ProfileUpdate(ProfileBase):
    pass

class Profile(ProfileBase):
    id: str          # uuid, comes from Supabase Auth
    role: str
    updated_at: Optional[datetime] = None