# Placeholder for main application entry point

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
from typing import Optional, List
import logging

from config.settings import get_settings
from db.models import get_db, init_db
from api import registration, discovery, negotiation, sessions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup"""
    try:
        logger.info("Starting ParkBench API...")
        logger.info("Initializing database...")
        
        # Try to initialize database
        init_db()
        
        # Test the database connection by querying table information
        from db.models import get_db
        db = next(get_db())
        result = db.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        tables = [row[0] for row in result]
        logger.info(f"Database tables available: {tables}")
        db.close()
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        logger.error(f"Error type: {type(e)}")
        
        # Try to get more information about the error
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Don't fail startup - continue without database for now
        logger.warning("Continuing without database connection - API will have limited functionality")

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

@app.get("/api/health")
async def api_health_check():
    """API health check endpoint (Railway expects this path)"""
    return {"status": "healthy", "service": "parkbench-api", "version": "0.1.0"}

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
