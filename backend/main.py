from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.routes import (
    calls, 
    webhooks, 
    medications, 
    caregiver, 
    seniors
)
from app.core.logging import logger

app = FastAPI(
    title="Vcare.life",
    description="Backend service managing seniors, caregivers, and vitals."
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://vcare-life.vercel.app",
        "https://august-hackathon.vercel.app"
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(calls.router, prefix="/calls")
app.include_router(webhooks.router, prefix="/webhooks")
app.include_router(medications.router, prefix="/medications")
app.include_router(caregiver.router, prefix="/caregiver")
app.include_router(seniors.router, prefix="/seniors")

@app.on_event("startup")
def startup():
    logger.info("Vcare.life backend started successfully")

@app.on_event("shutdown")
def shutdown():
    logger.info("Vcare.life backend shutting down")

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "Vcare.life"}

