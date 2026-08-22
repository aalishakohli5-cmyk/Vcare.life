from fastapi import Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.db.database import supabase
from app.core.logging import logger

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Authenticate user via Supabase token"""
    try:
        token = credentials.credentials
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            logger.warning(f"Invalid token attempt")
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        logger.debug(f"User authenticated: {user_response.user.id}")
        return user_response.user
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")

def verify_caregiver_access(user_id: str, senior_id: str):
    """Verify user is either the senior themselves or an authorized linked caregiver"""
    if str(user_id) == str(senior_id):
        return True

    try:
        response = supabase.table("caregiver_links") \
            .select("*") \
            .eq("caregiver_id", user_id) \
            .eq("senior_id", senior_id) \
            .execute()

        if not response.data:
            logger.warning(
                f"Access denied: user {user_id} -> senior {senior_id}"
            )
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access this senior's data"
            )
        
        return True
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Access verification error: {str(e)}")
        raise HTTPException(status_code=500, detail="Authorization check failed")