"""
Authentication and authorization module for ParkBench API

Provides JWT-based authentication, API key authentication, and rate limiting
for secure agent interactions and platform access control.
"""

import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging
import time
from collections import defaultdict
import asyncio

from config.settings import get_settings
from db.models import get_db, Agent

logger = logging.getLogger(__name__)

# Security schemes
security = HTTPBearer()

class TokenData(BaseModel):
    agent_name: Optional[str] = None
    permissions: List[str] = []
    token_type: str = "access"

class APIKeyData(BaseModel):
    key_id: str
    agent_name: str
    permissions: List[str]
    created_at: datetime
    expires_at: Optional[datetime] = None
    rate_limit: int = 1000  # requests per hour

class RateLimitInfo(BaseModel):
    requests_remaining: int
    reset_time: datetime
    limit: int

# In-memory store for rate limiting (in production, use Redis)
class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.locks = defaultdict(asyncio.Lock)
    
    async def is_allowed(self, identifier: str, limit: int = 100, window: int = 3600) -> RateLimitInfo:
        """
        Check if request is allowed under rate limit
        
        Args:
            identifier: Unique identifier (IP, API key, agent name)
            limit: Maximum requests allowed in window
            window: Time window in seconds (default 1 hour)
        """
        now = time.time()
        window_start = now - window
        
        async with self.locks[identifier]:
            # Clean old requests
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier] 
                if req_time > window_start
            ]
            
            current_count = len(self.requests[identifier])
            
            if current_count >= limit:
                # Rate limit exceeded
                oldest_request = min(self.requests[identifier]) if self.requests[identifier] else now
                reset_time = datetime.fromtimestamp(oldest_request + window)
                
                return RateLimitInfo(
                    requests_remaining=0,
                    reset_time=reset_time,
                    limit=limit
                )
            
            # Allow request
            self.requests[identifier].append(now)
            remaining = limit - (current_count + 1)
            reset_time = datetime.fromtimestamp(now + window)
            
            return RateLimitInfo(
                requests_remaining=remaining,
                reset_time=reset_time,
                limit=limit
            )

# Global rate limiter instance
rate_limiter = RateLimiter()

# In-memory API key store (in production, use database)
api_keys: Dict[str, APIKeyData] = {}

def generate_api_key(agent_name: str, permissions: List[str] = None, expires_hours: int = 24 * 7) -> str:
    """Generate a new API key for an agent"""
    if permissions is None:
        permissions = ["read", "write"]
    
    key_id = secrets.token_urlsafe(32)
    api_key = f"pk_{key_id}"
    
    expires_at = datetime.utcnow() + timedelta(hours=expires_hours) if expires_hours else None
    
    api_keys[api_key] = APIKeyData(
        key_id=key_id,
        agent_name=agent_name,
        permissions=permissions,
        created_at=datetime.utcnow(),
        expires_at=expires_at
    )
    
    logger.info(f"Generated API key for agent {agent_name} with permissions {permissions}")
    return api_key

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    settings = get_settings()
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token: str) -> TokenData:
    """Verify and decode a JWT token"""
    settings = get_settings()
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        agent_name: str = payload.get("sub")
        permissions: List[str] = payload.get("permissions", [])
        token_type: str = payload.get("type", "access")
        
        if agent_name is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject"
            )
        
        return TokenData(
            agent_name=agent_name,
            permissions=permissions,
            token_type=token_type
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def verify_api_key(api_key: str) -> APIKeyData:
    """Verify an API key"""
    if api_key not in api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    key_data = api_keys[api_key]
    
    # Check expiration
    if key_data.expires_at and datetime.utcnow() > key_data.expires_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has expired"
        )
    
    return key_data

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get current authenticated user from JWT token or API key
    """
    token = credentials.credentials
    
    # Try API key first (if it starts with 'pk_')
    if token.startswith('pk_'):
        try:
            key_data = verify_api_key(token)
            
            # Verify agent exists and is active
            agent = db.query(Agent).filter(
                Agent.agent_name == key_data.agent_name,
                Agent.active == True
            ).first()
            
            if not agent:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Agent not found or inactive"
                )
            
            return {
                "agent_name": key_data.agent_name,
                "agent_id": str(agent.agent_id),
                "permissions": key_data.permissions,
                "auth_type": "api_key",
                "rate_limit": key_data.rate_limit
            }
        except HTTPException:
            raise
    else:
        # Try JWT token
        try:
            token_data = verify_token(token)
            
            # Verify agent exists and is active
            agent = db.query(Agent).filter(
                Agent.agent_name == token_data.agent_name,
                Agent.active == True
            ).first()
            
            if not agent:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Agent not found or inactive"
                )
            
            return {
                "agent_name": token_data.agent_name,
                "agent_id": str(agent.agent_id),
                "permissions": token_data.permissions,
                "auth_type": "jwt",
                "rate_limit": 100  # Default rate limit for JWT tokens
            }
        except HTTPException:
            raise

def require_permission(required_permission: str):
    """Decorator to require specific permission"""
    def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        if required_permission not in current_user.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{required_permission}' required"
            )
        return current_user
    return permission_checker

async def rate_limit_middleware(
    request: Request,
    current_user: Optional[Dict[str, Any]] = None
) -> None:
    """
    Rate limiting middleware
    """
    # Determine identifier and rate limit
    if current_user:
        # Authenticated request
        identifier = f"agent:{current_user['agent_name']}"
        limit = current_user.get("rate_limit", 100)
    else:
        # Unauthenticated request - use IP
        client_ip = request.client.host
        identifier = f"ip:{client_ip}"
        limit = 10  # Much lower limit for unauthenticated requests
    
    # Check rate limit
    rate_info = await rate_limiter.is_allowed(identifier, limit)
    
    if rate_info.requests_remaining == 0:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Limit": str(rate_info.limit),
                "X-RateLimit-Remaining": str(rate_info.requests_remaining),
                "X-RateLimit-Reset": str(int(rate_info.reset_time.timestamp()))
            }
        )
    
    # Add rate limit headers to response (this would be handled by middleware in practice)
    logger.debug(f"Rate limit check for {identifier}: {rate_info.requests_remaining} remaining")

async def optional_authentication(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[Dict[str, Any]]:
    """
    Optional authentication - returns user data if authenticated, None otherwise
    Useful for endpoints that work for both authenticated and unauthenticated users
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None

# Authentication endpoint models
class LoginRequest(BaseModel):
    agent_name: str
    certificate_pem: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    agent_name: str

class APIKeyRequest(BaseModel):
    agent_name: str
    permissions: List[str] = ["read", "write"]
    expires_hours: Optional[int] = 24 * 7  # 1 week default

class APIKeyResponse(BaseModel):
    api_key: str
    agent_name: str
    permissions: List[str]
    expires_at: Optional[str] = None

# Utility functions for authentication endpoints
def authenticate_agent_with_certificate(agent_name: str, certificate_pem: str, db: Session) -> Agent:
    """
    Authenticate an agent using their certificate
    """
    agent = db.query(Agent).filter(
        Agent.agent_name == agent_name,
        Agent.active == True
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Agent not found or inactive"
        )
    
    # Verify certificate matches stored certificate
    # In production, you might want to allow certificate updates with proper validation
    if agent.certificate_pem.strip() != certificate_pem.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Certificate mismatch"
        )
    
    if not agent.verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Agent certificate not verified"
        )
    
    return agent 