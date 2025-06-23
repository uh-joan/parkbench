from fastapi import FastAPI
from contextlib import asynccontextmanager

from .api import registration as registration_api
# from .api import discovery as discovery_api  # Uncomment when ready
# from .api import negotiation as negotiation_api # Uncomment when ready
# from .api import sessions as sessions_api # Uncomment when ready
from .db.models import init_db, engine # Removed Base as it's not directly used here
from .config.settings import API_PREFIX, DATABASE_URL

# Lifespan context manager for application startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database, etc.
    print(f"Initializing database with URL: {DATABASE_URL}")
    init_db(DATABASE_URL)
    print("Database initialization complete.")
    yield
    # Shutdown: Clean up resources, close connections, etc.
    if engine:
        print("Closing database connection engine.")
        engine.dispose()

app = FastAPI(
    title="ParkBench API",
    description="ParkBench: AI Agent Identity, Discovery, Negotiation, and Orchestration Platform.",
    version="0.1.0",
    lifespan=lifespan
)

# Include API routers
# The path for registration will be {API_PREFIX}/register as defined in registration_api.router
app.include_router(registration_api.router, prefix=API_PREFIX, tags=["Agent Registration"])
# Example: if API_PREFIX = "/api/v1" and registration_api.router has a route @router.post("/register"),
# the full path will be /api/v1/register.

# app.include_router(discovery_api.router, prefix=API_PREFIX, tags=["Agent Discovery"]) # Uncomment when ready
# app.include_router(negotiation_api.router, prefix=API_PREFIX, tags=["A2A Negotiation"]) # Uncomment when ready
# app.include_router(sessions_api.router, prefix=API_PREFIX, tags=["A2A Sessions"]) # Uncomment when ready


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to ParkBench API. Visit /docs for API documentation."}

# To run this application (from the project root, assuming uvicorn is installed):
# cd parkbench
# uvicorn backend.main:app --reload --port 8000
# Ensure .env file with DATABASE_URL is in parkbench/backend/ or env var is set.
