# Placeholder for discovery API logic

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json

from db.models import get_db, Agent
from config.settings import get_settings

router = APIRouter()

# Pydantic models for responses
class AgentSearchResult(BaseModel):
    agent_id: str
    agent_name: str
    description: str
    skills: List[str]
    protocols: List[str]
    a2a_compliant: bool
    verified: bool
    active: bool
    api_endpoint: str

class AgentProfile(BaseModel):
    agent_id: str
    agent_name: str
    certificate_pem: str
    metadata: Dict[str, Any]
    verified: bool
    active: bool
    created_at: str
    updated_at: str

class A2ADescriptorResponse(BaseModel):
    agent_name: str
    supported_tasks: List[str]
    negotiation: bool
    context_required: List[str]
    token_budget: int

@router.get("/agents/search", response_model=List[AgentSearchResult])
async def search_agents(
    skill: Optional[str] = Query(None, description="Filter by skill"),
    protocol: Optional[str] = Query(None, description="Filter by protocol"),
    a2a_compliant: Optional[bool] = Query(None, description="Filter by A2A compliance"),
    verified: Optional[bool] = Query(None, description="Filter by verification status"),
    active: Optional[bool] = Query(True, description="Filter by active status"),
    limit: int = Query(50, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """Search for agents based on criteria"""
    
    query = db.query(Agent)
    
    # Apply filters
    filters = []
    
    if active is not None:
        filters.append(Agent.active == active)
    
    if verified is not None:
        filters.append(Agent.verified == verified)
    
    if a2a_compliant is not None:
        from sqlalchemy import Boolean
        filters.append(Agent.agent_metadata['a2a_compliant'].astext.cast(Boolean) == a2a_compliant)
    
    if skill:
        # Search in skills array within metadata
        filters.append(Agent.agent_metadata['skills'].astext.contains(f'"{skill}"'))
    
    if protocol:
        # Search in protocols array within metadata
        filters.append(Agent.agent_metadata['protocols'].astext.contains(f'"{protocol}"'))
    
    if filters:
        query = query.filter(and_(*filters))
    
    # Apply pagination
    agents = query.offset(offset).limit(limit).all()
    
    # Convert to response format
    results = []
    for agent in agents:
        metadata = agent.agent_metadata
        results.append(AgentSearchResult(
            agent_id=str(agent.agent_id),
            agent_name=agent.agent_name,
            description=metadata.get('description', ''),
            skills=metadata.get('skills', []),
            protocols=metadata.get('protocols', []),
            a2a_compliant=metadata.get('a2a_compliant', False),
            verified=agent.verified,
            active=agent.active,
            api_endpoint=metadata.get('api_endpoint', '')
        ))
    
    return results

@router.get("/agents/{agent_name}", response_model=AgentProfile)
async def get_agent_profile(
    agent_name: str,
    db: Session = Depends(get_db)
):
    """Get an agent's complete profile"""
    
    agent = db.query(Agent).filter(Agent.agent_name == agent_name).first()
    
    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_name}' not found"
        )
    
    return AgentProfile(
        agent_id=str(agent.agent_id),
        agent_name=agent.agent_name,
        certificate_pem=agent.certificate_pem,
        metadata=agent.agent_metadata,
        verified=agent.verified,
        active=agent.active,
        created_at=agent.created_at.isoformat(),
        updated_at=agent.updated_at.isoformat()
    )

@router.get("/agents/{agent_name}/a2a", response_model=A2ADescriptorResponse)
async def get_agent_a2a_descriptor(
    agent_name: str,
    db: Session = Depends(get_db)
):
    """Get A2A descriptors for an agent"""
    
    agent = db.query(Agent).filter(Agent.agent_name == agent_name).first()
    
    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_name}' not found"
        )
    
    if not agent.active:
        raise HTTPException(
            status_code=410,
            detail=f"Agent '{agent_name}' is not active"
        )
    
    a2a_metadata = agent.agent_metadata.get('a2a')
    if not a2a_metadata:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_name}' does not have A2A descriptors"
        )
    
    return A2ADescriptorResponse(
        agent_name=agent.agent_name,
        supported_tasks=a2a_metadata.get('supported_tasks', []),
        negotiation=a2a_metadata.get('negotiation', False),
        context_required=a2a_metadata.get('context_required', []),
        token_budget=a2a_metadata.get('token_budget', 0)
    )

@router.get("/agents", response_model=List[AgentSearchResult])
async def list_all_agents(
    active_only: bool = Query(True, description="Only return active agents"),
    limit: int = Query(50, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """List all agents (with optional filtering)"""
    
    query = db.query(Agent)
    
    if active_only:
        query = query.filter(Agent.active == True)
    
    agents = query.offset(offset).limit(limit).all()
    
    results = []
    for agent in agents:
        metadata = agent.agent_metadata
        results.append(AgentSearchResult(
            agent_id=str(agent.agent_id),
            agent_name=agent.agent_name,
            description=metadata.get('description', ''),
            skills=metadata.get('skills', []),
            protocols=metadata.get('protocols', []),
            a2a_compliant=metadata.get('a2a_compliant', False),
            verified=agent.verified,
            active=agent.active,
            api_endpoint=metadata.get('api_endpoint', '')
        ))
    
    return results
