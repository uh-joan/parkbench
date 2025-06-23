from fastapi import FastAPI, HTTPException, status
from models import AgentRegistrationRequest, AgentRegistrationResponse, AgentDB
from typing import Dict
from uuid import UUID, uuid4

app = FastAPI(
    title="ParkBench API",
    description="AI Agent Discovery and Directory Platform",
    version="0.1.0"
)

# In-memory storage for agents (substitute for a real database)
# Key: agent_id (UUID), Value: AgentDB object
agent_db_internal: Dict[UUID, AgentDB] = {}

@app.post("/agents/register", response_model=AgentRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_agent(agent_data: AgentRegistrationRequest):
    """
    Registers a new agent.
    - Validates registration data.
    - Issues a unique `agent_id`.
    - Stores agent information.
    """
    # Basic check for existing agent by name and version (can be more sophisticated)
    for existing_agent in agent_db_internal.values():
        if existing_agent.name == agent_data.name and existing_agent.version == agent_data.version:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Agent with name '{agent_data.name}' and version '{agent_data.version}' already exists."
            )

    new_agent_id = uuid4()

    # Create the database model instance
    agent_to_store = AgentDB(
        agent_id=new_agent_id,
        **agent_data.model_dump() # Pydantic v2
    )

    agent_db_internal[new_agent_id] = agent_to_store

    return AgentRegistrationResponse(agent_id=new_agent_id, status="registered")

# To run this app (from the terminal):
# uvicorn main:app --reload
