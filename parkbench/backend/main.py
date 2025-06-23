# Placeholder for main application entry point

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
from typing import Optional, List

from config.settings import get_settings
from db.models import get_db
from api import registration, discovery, negotiation, sessions

# Initialize FastAPI app
app = FastAPI(
    title="ParkBench API",
    version="0.1.0",
    description="An open, vendor-neutral AI agent identity, discovery, negotiation, and orchestration platform"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(registration.router, prefix="/api/v1", tags=["registration"])
app.include_router(discovery.router, prefix="/api/v1", tags=["discovery"])
app.include_router(negotiation.router, prefix="/api/v1", tags=["negotiation"])
app.include_router(sessions.router, prefix="/api/v1", tags=["sessions"])

# Include authentication router
from api import auth_endpoints
app.include_router(auth_endpoints.router, prefix="/api/v1/auth", tags=["authentication"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "ParkBench API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "parkbench-api"}

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
