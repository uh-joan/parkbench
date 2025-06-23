from typing import List, Dict, Any, Optional
import uuid # Added for agent_id in AgentRegistrationResponse
from pydantic import BaseModel, Field, HttpUrl, validator
import re

# Nested Pydantic models for the 'metadata' field

class A2AMetadata(BaseModel):
    supported_tasks: List[str]
    negotiation: bool
    context_required: List[str]
    token_budget: int = Field(..., ge=0)

class AgentMetadata(BaseModel):
    description: str
    version: str
    maintainer_contact: str # Could be an EmailStr if strict email validation is needed
    api_endpoint: HttpUrl
    protocols: List[str] # Could be Enum if values are fixed: Literal["REST", "GraphQL", "A2A"]
    a2a_compliant: bool
    skills: List[str]
    input_formats: List[str]
    output_formats: List[str]
    pricing_model: str
    public_key: str # This would typically be a more complex structure or validation
    a2a: A2AMetadata

    @validator('protocols')
    def check_protocols(cls, v):
        allowed_protocols = {"REST", "GraphQL", "A2A"}
        for protocol in v:
            if protocol not in allowed_protocols:
                raise ValueError(f"Invalid protocol: {protocol}. Allowed: {allowed_protocols}")
        return v

class AgentRegistrationRequest(BaseModel):
    agentName: str = Field(..., pattern=r"^[a-zA-Z0-9.-]+$") # ANS schema
    certificatePEM: str
    metadata: AgentMetadata

    @validator('agentName')
    def agent_name_format(cls, v):
        # Basic validation for DNS-style names, can be expanded
        if not re.match(r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$", v):
            raise ValueError("agentName must be a valid DNS-style name (e.g., myagent.example.com)")
        if len(v) > 255:
            raise ValueError("agentName must not exceed 255 characters")
        return v

    @validator('certificatePEM')
    def certificate_pem_format(cls, v):
        # Basic check for PEM format, can be made more robust
        if not v.strip().startswith("-----BEGIN CERTIFICATE-----") or \
           not v.strip().endswith("-----END CERTIFICATE-----"):
            raise ValueError("certificatePEM must be a valid PEM-formatted certificate.")
        return v

class AgentRegistrationResponse(BaseModel):
    agent_id: uuid.UUID # Assuming models.py uses uuid.UUID
    agentName: str
    status: str = "registered"

    model_config = {
        "from_attributes": True, # Replaces orm_mode for Pydantic V2
        "json_encoders": {
            uuid.UUID: lambda v: str(v) # Handles UUID serialization to string
        }
    }
