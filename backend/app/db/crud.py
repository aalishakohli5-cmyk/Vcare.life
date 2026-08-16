#resuable db query functions - routes/services call these 
# instead of writing raw queries
from app.db.database import supabase

def create_senior(name: str, age: int):
    #Insert a new senior record into the database
    response = supabase.table("seniors").insert({"name": name, "age": age}).execute()
    if not response.data:
        return None
    return response.data[0]

def get_senior(senior_id: int):
    #Retrieve a single senior ID
    response = supabase.table("seniors").select("*").eq("id", senior_id).execute()
    return response.data[0] if response.data else None

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

def create_caregiver(name: str, email: str, phone: str = None):
    response = supabase.table("caregivers").insert({
        "name": name,
        "email": email,
        "phone": phone
    }).execute()
    if not response.data:
        return None
    return response.data[0]

def get_caregiver(caregiver_id: int):
    response = supabase.table("caregivers").select("*").eq("id", caregiver_id).execute()
    return response.data[0] if response.data else None

def create_call_log(senior_id: int, status: str, transcript: str = None, distress_detected: bool = False):
    response = supabase.table("call_logs").insert({
        "senior_id": senior_id,
        "status": status,
        "transcript": transcript,
        "distress_detected": distress_detected
    }).execute()
    if not response:
        return None
    return response.data[0]

def get_call_log(senior_id: int):
    response = supabase.table("call_log").select("*").eq("senior_id", senior_id).execute()
    return response.data