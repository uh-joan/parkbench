# Placeholder for sessions API logic

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

from db.models import get_db, A2ASession, SessionStatus
from config.settings import get_settings

router = APIRouter()

# Pydantic models
class SessionStatusResponse(BaseModel):
    session_id: str = Field(alias="sessionID")
    initiating_agent: str = Field(alias="initiatingAgent")
    target_agent: str = Field(alias="targetAgent")
    task: str
    status: str
    context: Dict[str, Any]
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

class SessionUpdateRequest(BaseModel):
    status: str
    context: Optional[Dict[str, Any]] = None

class SessionUpdateResponse(BaseModel):
    session_id: str = Field(alias="sessionID")
    status: str
    updated_at: str = Field(alias="updatedAt")

@router.get("/a2a/session/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get the status of an A2A session"""
    
    try:
        # Convert string to UUID for query
        import uuid
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )
    
    session = db.query(A2ASession).filter(A2ASession.session_id == session_uuid).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found"
        )
    
    return SessionStatusResponse(
        sessionID=str(session.session_id),
        initiatingAgent=session.initiating_agent,
        targetAgent=session.target_agent,
        task=session.task,
        status=session.status.value,
        context=session.context or {},
        createdAt=session.created_at.isoformat(),
        updatedAt=session.updated_at.isoformat()
    )

@router.put("/a2a/session/{session_id}", response_model=SessionUpdateResponse)
async def update_session(
    session_id: str,
    request: SessionUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update an A2A session status and context"""
    
    try:
        # Convert string to UUID for query
        import uuid
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )
    
    session = db.query(A2ASession).filter(A2ASession.session_id == session_uuid).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found"
        )
    
    # Validate status transition
    valid_statuses = ["active", "completed", "failed"]
    if request.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    try:
        # Update session
        session.status = SessionStatus(request.status)
        if request.context is not None:
            session.context = request.context
        session.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(session)
        
        return SessionUpdateResponse(
            sessionID=str(session.session_id),
            status=session.status.value,
            updatedAt=session.updated_at.isoformat()
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update session: {str(e)}"
        )

@router.delete("/a2a/session/{session_id}")
async def terminate_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Terminate (mark as failed) an A2A session"""
    
    try:
        # Convert string to UUID for query
        import uuid
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )
    
    session = db.query(A2ASession).filter(A2ASession.session_id == session_uuid).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found"
        )
    
    try:
        # Mark session as failed
        session.status = SessionStatus.FAILED
        session.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "message": f"Session '{session_id}' terminated",
            "status": "failed"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to terminate session: {str(e)}"
        )

@router.get("/a2a/sessions")
async def list_sessions(
    initiating_agent: Optional[str] = None,
    target_agent: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List A2A sessions with optional filtering"""
    
    query = db.query(A2ASession)
    
    # Apply filters
    if initiating_agent:
        query = query.filter(A2ASession.initiating_agent == initiating_agent)
    
    if target_agent:
        query = query.filter(A2ASession.target_agent == target_agent)
    
    if status_filter:
        if status_filter not in ["active", "completed", "failed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status filter. Must be one of: active, completed, failed"
            )
        query = query.filter(A2ASession.status == SessionStatus(status_filter))
    
    # Apply pagination and order by most recent first
    sessions = query.order_by(A2ASession.created_at.desc()).offset(offset).limit(limit).all()
    
    # Convert to response format
    results = []
    for session in sessions:
        results.append({
            "session_id": str(session.session_id),
            "initiating_agent": session.initiating_agent,
            "target_agent": session.target_agent,
            "task": session.task,
            "status": session.status.value,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat()
        })
    
    return {
        "sessions": results,
        "total": len(results),
        "offset": offset,
        "limit": limit
    }
