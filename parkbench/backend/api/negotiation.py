# Placeholder for negotiation API logic

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import uuid

from db.models import get_db, Agent, A2ASession, SessionStatus
from .validation import validate_negotiation_request, validate_agent_name
from config.settings import get_settings

router = APIRouter()

# Pydantic models
class TaskNegotiationRequest(BaseModel):
    initiating_agent_name: str = Field(alias="initiatingAgentName")
    requested_task: str = Field(alias="requestedTask")
    context: Dict[str, Any]
    preferred_capabilities: Dict[str, Any] = Field(alias="preferredCapabilities")

class CandidateAgent(BaseModel):
    agent_name: str = Field(alias="agentName")
    match_score: float = Field(alias="matchScore", ge=0.0, le=1.0)
    supported_tasks: List[str] = Field(alias="supportedTasks")
    negotiation: bool
    token_budget: int = Field(alias="tokenBudget")

class TaskNegotiationResponse(BaseModel):
    candidate_agents: List[CandidateAgent] = Field(alias="candidateAgents")

class SessionInitiationRequest(BaseModel):
    target_agent_name: str = Field(alias="targetAgentName")
    task: str
    context: Dict[str, Any]
    initiating_agent_name: str = Field(alias="initiatingAgentName")

class SessionInitiationResponse(BaseModel):
    session_id: str = Field(alias="sessionID")
    session_token: str = Field(alias="sessionToken")
    status: str
    target_agent: str = Field(alias="targetAgent")

@router.post("/a2a/negotiate", response_model=TaskNegotiationResponse)
async def negotiate_task(
    request: TaskNegotiationRequest,
    db: Session = Depends(get_db)
):
    """Negotiate a task with candidate agents"""
    
    # Verify initiating agent exists
    initiating_agent = db.query(Agent).filter(
        Agent.agent_name == request.initiating_agent_name,
        Agent.active == True
    ).first()
    
    if not initiating_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Initiating agent '{request.initiating_agent_name}' not found or inactive"
        )
    
    # Find candidate agents that support the requested task
    # This is a simplified matching algorithm - in production, this would be more sophisticated
    candidate_agents = db.query(Agent).filter(
        Agent.active == True,
        Agent.agent_name != request.initiating_agent_name  # Exclude self
    ).all()
    
    candidates = []
    for agent in candidate_agents:
        metadata = agent.agent_metadata
        a2a_data = metadata.get('a2a', {})
        supported_tasks = a2a_data.get('supported_tasks', [])
        
        # Simple task matching (contains check)
        if any(request.requested_task.lower() in task.lower() for task in supported_tasks):
            # Calculate a simple match score based on task relevance and capabilities
            match_score = 0.8  # Base score for task match
            
            # Boost score for negotiation capability if preferred
            if (request.preferred_capabilities.get('negotiation') and 
                a2a_data.get('negotiation', False)):
                match_score += 0.1
            
            # Boost score for adequate token budget
            preferred_budget = request.preferred_capabilities.get('token_budget', 0)
            agent_budget = a2a_data.get('token_budget', 0)
            if agent_budget >= preferred_budget:
                match_score += 0.1
            
            match_score = min(match_score, 1.0)  # Cap at 1.0
            
            candidates.append(CandidateAgent(
                agentName=agent.agent_name,
                matchScore=match_score,
                supportedTasks=supported_tasks,
                negotiation=a2a_data.get('negotiation', False),
                tokenBudget=agent_budget
            ))
    
    # Sort by match score (highest first)
    candidates.sort(key=lambda x: x.match_score, reverse=True)
    
    return TaskNegotiationResponse(candidateAgents=candidates[:10])  # Return top 10

@router.post("/a2a/session/initiate", response_model=SessionInitiationResponse)
async def initiate_a2a_session(
    request: SessionInitiationRequest,
    db: Session = Depends(get_db)
):
    """Initiate an A2A session"""
    
    # Verify both agents exist and are active
    initiating_agent = db.query(Agent).filter(
        Agent.agent_name == request.initiating_agent_name,
        Agent.active == True
    ).first()
    
    target_agent = db.query(Agent).filter(
        Agent.agent_name == request.target_agent_name,
        Agent.active == True
    ).first()
    
    if not initiating_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Initiating agent '{request.initiating_agent_name}' not found or inactive"
        )
    
    if not target_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target agent '{request.target_agent_name}' not found or inactive"
        )
    
    # Check if target agent supports the requested task
    target_metadata = target_agent.agent_metadata
    a2a_data = target_metadata.get('a2a', {})
    supported_tasks = a2a_data.get('supported_tasks', [])
    
    if not any(request.task.lower() in task.lower() for task in supported_tasks):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Target agent does not support task '{request.task}'"
        )
    
    try:
        # Create new session
        session_id = uuid.uuid4()
        session_token = f"pb_session_{session_id.hex}"  # Simple token format
        
        new_session = A2ASession(
            session_id=session_id,
            initiating_agent=request.initiating_agent_name,
            target_agent=request.target_agent_name,
            task=request.task,
            session_token=session_token,
            status=SessionStatus.ACTIVE,
            context=request.context
        )
        
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        return SessionInitiationResponse(
            sessionID=str(session_id),
            sessionToken=session_token,
            status="active",
            targetAgent=request.target_agent_name
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate session: {str(e)}"
        )
