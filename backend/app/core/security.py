from fastapi import Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.db.database import supabase

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return user_response.user
    
    except Exception as e:
        print("Auth error:", e)
        raise HTTPException(status_code=401, detail="Unauthorized")

def verify_caregiver_access(caregiver_id: str, senior_id: str):
    """
    Confirms this caregiver is actually linked to this senior
    before allowing access to their data.
    """
    response = supabase.table("caregiver_links") \
        .select("*") \
        .eq("caregiver_id", caregiver_id) \
        .eq("senior_id", senior_id) \
        .execute()

    if not response.data:
        raise HTTPException(status_code=403, detail="Not authorized to access this senior's data")
    return True