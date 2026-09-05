"""Reusable database query functions - routes/services call these instead of writing raw queries"""
from app.db.database import supabase
from app.core.logging import logger
from typing import Optional, Dict, List, Any

# Profiles
def get_profile(profile_id: str) -> Optional[Dict[str, Any]]:
    try:
        response = supabase.table("profiles").select("*").eq("id", profile_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error fetching profile {profile_id}: {str(e)}")
        return None

def update_profile(profile_id: str, data: dict) -> Optional[Dict[str, Any]]:
    try:
        response = supabase.table("profiles").update(data).eq("id", profile_id).execute()
        if not response.data:
            return None
        return response.data[0]
    except Exception as e:
        logger.error(f"Error updating profile {profile_id}: {str(e)}")
        return None

# Medications
def create_medications(
    senior_id: str,
    name: str,
    dosage: str,
    scheduled_time: str
) -> Optional[Dict[str, Any]]:
    """Insert single medication record for senior"""
    try:
        response = supabase.table("medications").insert({
            "senior_id": senior_id,
            "name": name,
            "dosage": dosage,
            "scheduled_time": scheduled_time
        }).execute()
        if not response.data:
            logger.warning(f"Failed to create medication for senior {senior_id}")
            return None
        return response.data[0]
    except Exception as e:
        logger.error(f"Error creating medication: {str(e)}")
        return None

def get_medications_senior(senior_id: str) -> Optional[List[Dict[str, Any]]]:
    """Fetch all medications for a senior"""
    try:
        response = supabase.table("medications").select("*").eq("senior_id", senior_id).order("scheduled_time", desc=False).execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error fetching medications for senior {senior_id}: {str(e)}")
        return None

def get_medication(medication_id: int) -> Optional[Dict[str, Any]]:
    """Fetch one medication so routes can verify ownership before changing it."""
    try:
        response = supabase.table("medications").select("*").eq("id", medication_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error fetching medication {medication_id}: {str(e)}")
        return None

def update_medication(medication_id: int, data: dict) -> Optional[Dict[str, Any]]:
    """Update medication record (e.g. taken status, name, dosage, time)"""
    try:
        response = supabase.table("medications").update(data).eq("id", medication_id).execute()
        if not response.data:
            return None
        return response.data[0]
    except Exception as e:
        logger.error(f"Error updating medication {medication_id}: {str(e)}")
        return None

def delete_medication(medication_id: int) -> bool:
    """Delete a medication record"""
    try:
        response = supabase.table("medications").delete().eq("id", medication_id).execute()
        return bool(response.data)
    except Exception as e:
        logger.error(f"Error deleting medication {medication_id}: {str(e)}")
        return False

def get_caregivers_for_seniors(senior_id: str) -> Optional[List[Dict[str, Any]]]:
    try:
        response = supabase.table("caregiver_links").select("*").eq("senior_id", senior_id).execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error fetching caregivers for senior {senior_id}: {str(e)}")
        return None

def get_seniors_for_caregiver(caregiver_id: str) -> Optional[List[Dict[str, Any]]]:
    try:
        response = supabase.table("caregiver_links").select("*").eq("caregiver_id", caregiver_id).execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error fetching seniors for caregiver {caregiver_id}: {str(e)}")
        return None

# Call Logs
def create_call_log(
    senior_id: str,
    status: str,
    transcript: Optional[str] = None,
    distress_detected: bool = False
) -> Optional[Dict[str, Any]]:
    try:
        response = supabase.table("call_logs").insert({
            "senior_id": senior_id,
            "status": status,
            "transcript": transcript,
            "distress_detected": distress_detected
        }).execute()
        
        if not response or not response.data:
            logger.warning(f"Failed to create call log for senior {senior_id}")
            return None
        return response.data[0]
    except Exception as e:
        logger.error(f"Error creating call log: {str(e)}")
        return None

def get_call_logs_for_senior(senior_id: str) -> Optional[List[Dict[str, Any]]]:
    try:
        response = supabase.table("call_logs").select("*").eq("senior_id", senior_id).order("created_at", desc=True).execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error fetching call logs for senior {senior_id}: {str(e)}")
        return None

# Caregiver Profile Creation
def create_or_update_caregiver_profile(
    user_id: str,
    full_name: str,
    email: str,
    phone: Optional[str] = None,
    relationship: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Create or update caregiver profile"""
    try:
        data = {
            "id": user_id,
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "emergency_contact_relationship": relationship,
            "role": "caregiver",
            "onboarding_complete": True
        }
        response = supabase.table("profiles").upsert(data).execute()
        if not response.data:
            logger.warning(f"Failed to create caregiver profile for {user_id}")
            return None
        return response.data[0]
    except Exception as e:
        logger.error(f"Error creating caregiver profile: {str(e)}")
        return None

# Senior Profile Creation
def create_or_update_senior_profile(
    user_id: str,
    full_name: str,
    email: str,
    phone: Optional[str] = None,
    date_of_birth: Optional[str] = None,
    gender: Optional[str] = None,
    emergency_contact_name: Optional[str] = None,
    emergency_contact_phone: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Create or update senior profile"""
    try:
        data = {
            "id": user_id,
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "date_of_birth": date_of_birth,
            "gender": gender,
            "emergency_contact_name": emergency_contact_name,
            "emergency_contact_phone": emergency_contact_phone,
            "role": "senior",
            "onboarding_complete": True
        }
        response = supabase.table("profiles").upsert(data).execute()
        if not response.data:
            logger.warning(f"Failed to create senior profile for {user_id}")
            return None
        return response.data[0]
    except Exception as e:
        logger.error(f"Error creating senior profile: {str(e)}")
        return None
