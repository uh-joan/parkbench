from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

class A2AMetadata(BaseModel):
    supported_tasks: List[str] = []
    negotiation: Optional[bool] = None
    context_required: List[str] = []
    token_budget: Optional[int] = None

class AgentRegistrationRequest(BaseModel):
    name: str
    description: Optional[str] = None
    version: str
    maintainer_contact: str
    api_endpoint: HttpUrl
    protocols: List[str] # Could be an Enum later: ["REST", "GraphQL", "A2A"]
    a2a_compliant: bool
    skills: List[str] = Field(default_factory=list) # Example: ["travel-booking", "pharma-ci", "market-research"]
    input_formats: List[str] = Field(default_factory=list) # Example: ["JSON", "CSV"]
    output_formats: List[str] = Field(default_factory=list) # Example: ["JSON"]
    pricing_model: Optional[str] = None
    public_key: Optional[str] = None
    a2a: Optional[A2AMetadata] = None # For A2A descriptor compatibility

class AgentDB(AgentRegistrationRequest):
    agent_id: UUID = Field(default_factory=uuid4)
    verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AgentRegistrationResponse(BaseModel):
    agent_id: UUID
    status: str = "registered"

# Example of how AgentDB would be used (in-memory store for now)
# agent_db_internal: Dict[UUID, AgentDB] = {}
