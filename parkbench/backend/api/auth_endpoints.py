"""
Authentication endpoints for ParkBench API

Provides endpoints for agent login, API key generation, and authentication management.
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from db.models import get_db
from config.settings import get_settings
from .auth import (
    LoginRequest, LoginResponse, APIKeyRequest, APIKeyResponse,
    authenticate_agent_with_certificate, create_access_token, generate_api_key,
    get_current_user, require_permission, rate_limit_middleware, api_keys
)

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate an agent using their certificate and get a JWT token
    """
    try:
        # Rate limiting for login attempts
        # In production, you'd want stricter rate limiting for login
        
        # Authenticate agent with certificate
        agent = authenticate_agent_with_certificate(
            request.agent_name, 
            request.certificate_pem, 
            db
        )
        
        # Create access token
        settings = get_settings()
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        
        token_data = {
            "sub": agent.agent_name,
            "permissions": ["read", "write", "negotiate"],  # Default permissions
            "type": "access"
        }
        
        access_token = create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )
        
        logger.info(f"Agent {agent.agent_name} successfully authenticated")
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,  # Convert to seconds
            agent_name=agent.agent_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for {request.agent_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )

@router.post("/api-key", response_model=APIKeyResponse)
async def generate_api_key_endpoint(
    request: APIKeyRequest,
    current_user: dict = Depends(require_permission("admin")),
    db: Session = Depends(get_db)
):
    """
    Generate a new API key for an agent (requires admin permission)
    """
    try:
        # Verify the target agent exists
        from db.models import Agent
        agent = db.query(Agent).filter(
            Agent.agent_name == request.agent_name,
            Agent.active == True
        ).first()
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{request.agent_name}' not found or inactive"
            )
        
        # Generate API key
        api_key = generate_api_key(
            agent_name=request.agent_name,
            permissions=request.permissions,
            expires_hours=request.expires_hours
        )
        
        key_data = api_keys[api_key]
        
        logger.info(f"API key generated for {request.agent_name} by {current_user['agent_name']}")
        
        return APIKeyResponse(
            api_key=api_key,
            agent_name=request.agent_name,
            permissions=request.permissions,
            expires_at=key_data.expires_at.isoformat() if key_data.expires_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API key generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate API key"
        )

@router.get("/me")
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """
    Get information about the currently authenticated user
    """
    return {
        "agent_name": current_user["agent_name"],
        "agent_id": current_user["agent_id"],
        "permissions": current_user["permissions"],
        "auth_type": current_user["auth_type"],
        "rate_limit": current_user["rate_limit"]
    }

@router.get("/api-keys")
async def list_api_keys(
    current_user: dict = Depends(require_permission("admin"))
):
    """
    List all API keys (admin only)
    """
    keys_info = []
    
    for api_key, key_data in api_keys.items():
        # Don't expose the actual key, just metadata
        keys_info.append({
            "key_id": key_data.key_id,
            "agent_name": key_data.agent_name,
            "permissions": key_data.permissions,
            "created_at": key_data.created_at.isoformat(),
            "expires_at": key_data.expires_at.isoformat() if key_data.expires_at else None,
            "rate_limit": key_data.rate_limit
        })
    
    return {
        "api_keys": keys_info,
        "total": len(keys_info)
    }

@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: dict = Depends(require_permission("admin"))
):
    """
    Revoke an API key (admin only)
    """
    # Find and remove the API key
    for api_key, key_data in list(api_keys.items()):
        if key_data.key_id == key_id:
            del api_keys[api_key]
            logger.info(f"API key {key_id} revoked by {current_user['agent_name']}")
            return {"message": f"API key {key_id} revoked successfully"}
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"API key with ID '{key_id}' not found"
    )

@router.post("/refresh")
async def refresh_token(
    current_user: dict = Depends(get_current_user)
):
    """
    Refresh JWT token (only works with JWT auth, not API keys)
    """
    if current_user["auth_type"] != "jwt":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token refresh only available for JWT authentication"
        )
    
    # Create new access token
    settings = get_settings()
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    
    token_data = {
        "sub": current_user["agent_name"],
        "permissions": current_user["permissions"],
        "type": "access"
    }
    
    access_token = create_access_token(
        data=token_data,
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
        "agent_name": current_user["agent_name"]
    }

@router.get("/permissions")
async def get_permissions():
    """
    Get list of available permissions in the system
    """
    return {
        "permissions": [
            {
                "name": "read",
                "description": "Read access to agent data and discovery"
            },
            {
                "name": "write", 
                "description": "Write access to register and update agents"
            },
            {
                "name": "negotiate",
                "description": "Access to A2A negotiation and session management"
            },
            {
                "name": "admin",
                "description": "Administrative access to manage API keys and system settings"
            }
        ]
    } 