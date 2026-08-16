from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_calls():
    return {"message": "Calls endpoint working"}