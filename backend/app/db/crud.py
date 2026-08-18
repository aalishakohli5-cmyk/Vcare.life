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
        response = supabase.table("medications").select("*").eq("senior_id", senior_id).execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error fetching medications for senior {senior_id}: {str(e)}")
        return None

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
        response = supabase.table("call_logs").select("*").eq("senior_id", senior_id).execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error fetching call logs for senior {senior_id}: {str(e)}")
        return None