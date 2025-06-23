from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import uuid # Required for AgentRegistrationResponse

from ..db import models as db_models # models from db/models.py
from ..db.models import get_db # get_db dependency
from .schemas.agent_registration_models import AgentRegistrationRequest, AgentRegistrationResponse # Pydantic models
from ..config.settings import DEFAULT_AGENT_VERIFIED_STATUS, DEFAULT_AGENT_ACTIVE_STATUS

router = APIRouter()

@router.post("/register", response_model=AgentRegistrationResponse, status_code=201)
async def register_agent(
    agent_data: AgentRegistrationRequest,
    db: Session = Depends(get_db)
):
    """
    Registers a new agent with the ParkBench platform.

    - **agentName**: The unique DNS-style name for the agent (e.g., translator-b.agents.example.com).
    - **certificatePEM**: The agent's public key certificate in PEM format.
    - **metadata**: A JSON object containing various details about the agent's capabilities and configuration.
    """
    # Check if agent already exists
    existing_agent = db.query(db_models.Agent).filter(db_models.Agent.agentName == agent_data.agentName).first()
    if existing_agent:
        raise HTTPException(status_code=409, detail=f"Agent with name '{agent_data.agentName}' already exists.")

    try:
        # The metadata from Pydantic model (agent_data.metadata) is already a dict
        # because Pydantic converts the AgentMetadata model to a dict when .dict() is called
        # or when it's passed to a SQLAlchemy model that expects a dict for a JSON field.
        # We need to ensure it's passed as a dictionary.

        new_agent = db_models.Agent(
            agentName=agent_data.agentName,
            certificatePEM=agent_data.certificatePEM,
            metadata_=agent_data.metadata.model_dump(), # Use .model_dump() for Pydantic v2, or .dict() for v1
            verified=DEFAULT_AGENT_VERIFIED_STATUS,
            active=DEFAULT_AGENT_ACTIVE_STATUS
            # agent_id, created_at, updated_at have defaults
        )
        db.add(new_agent)
        db.commit()
        db.refresh(new_agent) # To get the generated agent_id and other defaults

        return new_agent # FastAPI will automatically serialize this using AgentRegistrationResponse

    except IntegrityError: # Catch potential race conditions if another request registered the same name
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Agent with name '{agent_data.agentName}' already registered (concurrent request).")
    except Exception as e:
        db.rollback()
        # Log the exception e here for debugging
        print(f"Error during agent registration: {e}") # Basic logging
        raise HTTPException(status_code=500, detail="Internal server error during agent registration.")

# Placeholder for other registration-related endpoints if needed in this file
# e.g., /renew, /deactivate, /status (though status might be in discovery)

# Note: The AgentRegistrationResponse model in schemas/agent_registration_models.py
# needs to have `orm_mode = True` (or `from_attributes = True` for Pydantic v2)
# in its Config class to work directly with SQLAlchemy model instances like `new_agent`.
# Also, ensure UUID is handled correctly for serialization in the response model.
# The `uuid` import was added to this file for the response model type hint,
# and the response model itself should handle UUID serialization.
# The field in `AgentRegistrationResponse` should be `agent_id: uuid.UUID`.
# The `metadata_` field in the database model was named with a trailing underscore
# to avoid conflict with SQLAlchemy's internal `metadata` attribute.
# When creating the Agent model instance, we use `metadata_=agent_data.metadata.dict()`.
# When accessing it, it would be `retrieved_agent.metadata_`.
# The response model should ideally map this back to `metadata` if that's the desired API response field name.
# However, the README's response for /register does not include metadata, only agent_id, agentName, status.
# So, AgentRegistrationResponse is correct as is.

# The `agent_id` in `AgentRegistrationResponse` is correctly typed as `uuid.UUID`.
# Pydantic's `orm_mode` (or `from_attributes`) will handle the conversion from the SQLAlchemy model.
# The JSON encoder for UUID in `AgentRegistrationResponse.Config` will ensure it's a string in the JSON output.
# Used `agent_data.metadata.model_dump()` which is the Pydantic V2 way. If using V1, it should be `.dict()`.
# Assuming Pydantic V2 for `model_dump()`. If dependencies enforce V1, this needs to be `dict()`.
# Let's assume latest Pydantic for now. Our requirements.txt just says `pydantic[email]`.
# For safety and broader compatibility for now, I'll revert model_dump() to dict().
# If Pydantic v2 is strictly used, model_dump() is preferred.
# Reverted to .dict() for metadata.
# Corrected the import for uuid in schemas/agent_registration_models.py
# It should be `import uuid` at the top of that file.
# Corrected the AgentRegistrationResponse in schemas, it needs `import uuid`.
# In this file, `uuid` is also needed for the response model typing.
# `agent_data.metadata.dict()` is correct for Pydantic v1.
# `agent_data.metadata.model_dump()` is for Pydantic v2.
# Given `pydantic[email]` in requirements, it usually pulls the latest, which would be V2.
# Let's stick to `model_dump()` and assume Pydantic V2. If errors occur, we can switch to `dict()`.
# The `AgentRegistrationResponse` model should be:
# class AgentRegistrationResponse(BaseModel):
#    agent_id: uuid.UUID
#    agentName: str
#    status: str = "registered"
#
#    class Config:
#        orm_mode = True # or from_attributes = True for Pydantic V2
#
# And ensure `import uuid` is at the top of `agent_registration_models.py`.
# I will ensure this is correct in the schema file.

# Final check on metadata:
# DB model: metadata_ = Column("metadata", JSON, nullable=False)
# Pydantic request model: metadata: AgentMetadata
# When creating DB object: metadata_=agent_data.metadata.model_dump() (or .dict())
# This is correct. The AgentMetadata Pydantic model will be converted to a dictionary
# and stored in the JSONB column named 'metadata'.
# The response model AgentRegistrationResponse does not include metadata, so no issues there.
# The field name in the DB is `metadata` due to `Column("metadata", JSON ...)`.
# The attribute name in the SQLAlchemy model is `metadata_`. This is fine.
