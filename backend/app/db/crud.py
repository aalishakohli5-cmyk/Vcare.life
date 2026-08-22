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
        return True
    except Exception as e:
        logger.error(f"Error deleting medication {medication_id}: {str(e)}")
        return False

# Caregiver links
def create_caregiver_link(caregiver_id: str, senior_id: str) -> Optional[Dict[str, Any]]:
    try:
        response = supabase.table("caregiver_links").insert({
            "caregiver_id": caregiver_id,
            "senior_id": senior_id
        }).execute()
        if not response.data:
            return None
        return response.data[0]
    except Exception as e:
        logger.error(f"Error creating caregiver link: {str(e)}")
        return None

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
            "relationship": relationship,
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

# Complete Caregiver Onboarding (creates senior + link in one go)
def complete_caregiver_onboarding(
    caregiver_id: str,
    senior_name: str,
    senior_phone: str,
    relationship: str
) -> Optional[Dict[str, Any]]:
    """
    Called after the caregiver profile is saved during onboarding.
    Creates a placeholder auth user for the senior, their profile row,
    and a caregiver_links entry connecting the two.
    """
    import uuid

    senior_id = str(uuid.uuid4())
    placeholder_email = f"senior-{senior_id[:8]}@vcare.placeholder"

    try:
        # 1. Create placeholder auth user so the FK on profiles(id) is satisfied
        auth_response = supabase.auth.admin.create_user({
            "email": placeholder_email,
            "email_confirm": True,
            "user_metadata": {"full_name": senior_name, "role": "senior"},
        })
        if auth_response and auth_response.user:
            senior_id = auth_response.user.id  # use the real auth uid
        else:
            logger.error("Failed to create placeholder auth user for senior")
            return None

        # 2. Create senior profile
        senior_profile = {
            "id": senior_id,
            "full_name": senior_name,
            "email": placeholder_email,
            "phone": senior_phone,
            "role": "senior",
            "onboarding_complete": False,
        }
        supabase.table("profiles").upsert(senior_profile).execute()

        # 3. Create caregiver link
        link = {
            "caregiver_id": caregiver_id,
            "senior_id": senior_id,
        }
        supabase.table("caregiver_links").upsert(link, on_conflict="caregiver_id,senior_id").execute()

        logger.info(
            f"Onboarding complete: caregiver={caregiver_id}, senior={senior_id}"
        )

        return {
            "senior_id": senior_id,
            "senior_name": senior_name,
            "link_created": True,
        }

    except Exception as e:
        logger.error(f"Error completing caregiver onboarding: {str(e)}")
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