from fastapi import FastAPI
from app.routes import (
    calls, 
    webhooks, 
    medications, 
    caregiver, 
    seniors
)

app = FastAPI(
    title="Vcare.life",
    description="Backend service managing seniors, caregivers, and vitals."
)

app.include_router(calls.router, prefix="/calls")
app.include_router(webhooks.router, prefix="/webhooks")
app.include_router(medications.router, prefix="/medications")
app.include_router(caregiver.router, prefix="/caregiver")
app.include_router(seniors.router, prefix="/seniors")

