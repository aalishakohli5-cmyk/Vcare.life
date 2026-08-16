#resuable db query functions - routes/services call these 
# instead of writing raw queries
from app.db.database import supabase

# Profiles
def get_profile(profile_id: str):
    response = supabase.table("profiles").select("*").eq("id", profile_id).execute()
    return response.data[0] if response.data else None

def update_profile(profile_id: str, data: dict):
    response = supabase.table("profiles").update(data).eq("id", profile_id).execute()
    if not response.data:
        return None
    return response.data[0]

# Medications
def create_medications(senior_id: str, name: str, dosage: str, scheduled_time: str):
    #Insert single medication record for senior
    response = supabase.table("medications").insert({
        "senior_id": senior_id,
        "name": name,
        "dosage": dosage,
        "scheduled_time": scheduled_time
    }).execute()
    if not response.data:
        return None
    return response.data[0]

def get_medications_senior(senior_id: str):
    #Fetch all medications associated with a specific senior ID
    response = supabase.table("medications").select("*").eq("senior_id", senior_id).execute()
    return response.data

# Caregiver links
def create_caregiver_link(caregiver_id: str, senior_id: str):
    response = supabase.table("caregiver_links").insert({
        "caregiver_id": caregiver_id,
        "senior_id": senior_id
    }).execute()
    if not response.data:
        return None
    return response.data[0]

def get_caregivers_for_seniors(senior_id: str):
    response = supabase.table("caregiver_links").select("*").eq("senior_id", senior_id).execute()
    return response.data

def get_seniors_for_caregiver(caregiver_id: str):
    response = supabase.table("caregiver_links").select("*").eq("caregiver_id", caregiver_id).execute()
    return response.data

# Call Logs
def create_call_log(senior_id: str, status: str, transcript: str = None, distress_detected: bool = False):
    response = supabase.table("call_logs").insert({
        "senior_id": senior_id,
        "status": status,
        "transcript": transcript,
        "distress_detected": distress_detected
    }).execute()
    if not response:
        return None
    return response.data[0]

def get_call_logs_for_senior(senior_id: str):
    response = supabase.table("call_logs").select("*").eq("senior_id", senior_id).execute()
    return response.data