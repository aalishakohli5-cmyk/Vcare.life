from fastapi import APIRouter, Depends, HTTPException

from app.core.logging import logger
from app.core.security import get_current_user
from app.db.database import supabase


router = APIRouter()


@router.delete("/")
def delete_account(user=Depends(get_current_user)):
    """Permanently delete the authenticated user and all cascading profile data."""
    user_id = str(user.id)

    try:
        supabase.auth.admin.delete_user(user_id)
        logger.info("Deleted account for authenticated user %s", user_id)
        return {"success": True, "message": "Account permanently deleted"}
    except Exception as error:
        logger.error("Failed to delete account for user %s: %s", user_id, str(error))
        raise HTTPException(
            status_code=500,
            detail="We could not delete your account. Please try again."
        ) from error
