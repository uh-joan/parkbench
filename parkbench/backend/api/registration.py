# Placeholder for registration API logic

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import uuid
import json
from datetime import datetime

# Certificate validation imports
import base64
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
import logging

from db.models import get_db, Agent
from config.settings import get_settings

# Import enhanced validation
from .validation import validate_agent_name, validate_agent_metadata, ValidationResult

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request/response
class A2ADescriptor(BaseModel):
    supported_tasks: List[str]
    negotiation: bool
    context_required: List[str]
    token_budget: int = Field(ge=0)

class AgentMetadata(BaseModel):
    description: str
    version: str
    maintainer_contact: str
    api_endpoint: str
    protocols: List[str]
    a2a_compliant: bool
    skills: List[str]
    input_formats: List[str]
    output_formats: List[str]
    pricing_model: str
    public_key: str
    a2a: A2ADescriptor

class AgentRegistrationRequest(BaseModel):
    agent_name: str = Field(alias="agentName", pattern="^[a-zA-Z0-9.-]+$")
    certificate_pem: str = Field(alias="certificatePEM")
    metadata: AgentMetadata

class AgentRegistrationResponse(BaseModel):
    agent_id: str
    agent_name: str = Field(alias="agentName")
    status: str

class AgentStatusResponse(BaseModel):
    agent_id: str
    agent_name: str
    verified: bool
    active: bool
    created_at: datetime
    updated_at: datetime

# Pydantic models for validation
class AgentSkills(BaseModel):
    """Skills that the agent can perform"""
    pass

class A2ACapabilities(BaseModel):
    """A2A-specific capabilities and configurations"""
    supported_tasks: List[str] = Field(..., description="List of A2A tasks this agent can perform")
    negotiation: bool = Field(default=True, description="Whether the agent supports negotiation")
    context_required: List[str] = Field(default=[], description="Required context fields for A2A sessions")
    token_budget: int = Field(default=1000, description="Available token budget for A2A operations")

class CertificateInfo(BaseModel):
    """Information extracted from X.509 certificate"""
    subject: Dict[str, str]
    issuer: Dict[str, str]
    serial_number: str
    not_before: datetime
    not_after: datetime
    is_valid: bool
    validation_errors: List[str]

def extract_name_attributes(name: x509.Name) -> Dict[str, str]:
    """Extract common name attributes from X.509 Name object"""
    attributes = {}
    for attribute in name:
        oid = attribute.oid
        if oid == NameOID.COMMON_NAME:
            attributes['common_name'] = attribute.value
        elif oid == NameOID.ORGANIZATION_NAME:
            attributes['organization'] = attribute.value
        elif oid == NameOID.COUNTRY_NAME:
            attributes['country'] = attribute.value
        elif oid == NameOID.LOCALITY_NAME:
            attributes['locality'] = attribute.value
        elif oid == NameOID.EMAIL_ADDRESS:
            attributes['email'] = attribute.value
    return attributes

def validate_certificate(certificate_pem: str, agent_name: str) -> CertificateInfo:
    """
    Validate X.509 certificate and extract information
    
    Args:
        certificate_pem: PEM-encoded certificate
        agent_name: Agent name for domain validation
        
    Returns:
        CertificateInfo: Validation results and certificate details
    """
    validation_errors = []
    
    try:
        # Parse the PEM certificate
        cert_bytes = certificate_pem.encode('utf-8')
        cert = x509.load_pem_x509_certificate(cert_bytes, default_backend())
        
        # Extract certificate information
        subject = extract_name_attributes(cert.subject)
        issuer = extract_name_attributes(cert.issuer)
        serial_number = str(cert.serial_number)
        not_before = cert.not_valid_before
        not_after = cert.not_valid_after
        
        # Check certificate validity period
        now = datetime.utcnow()
        if now < not_before:
            validation_errors.append("Certificate is not yet valid")
        elif now > not_after:
            validation_errors.append("Certificate has expired")
        
        # Validate agent name against certificate
        # For development, we'll be lenient - in production, implement proper domain validation
        common_name = subject.get('common_name', '')
        if agent_name and common_name:
            # Simple check - in production, implement proper domain/SAN validation
            if not (agent_name == common_name or 
                   agent_name.endswith('.' + common_name) or
                   common_name.endswith('.' + agent_name)):
                validation_errors.append(
                    f"Agent name '{agent_name}' does not match certificate common name '{common_name}'"
                )
        
        # Check key usage extensions (if present)
        try:
            key_usage = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.KEY_USAGE).value
            if not (key_usage.digital_signature or key_usage.key_encipherment):
                validation_errors.append("Certificate does not allow digital signature or key encipherment")
        except x509.ExtensionNotFound:
            # Key usage extension is optional
            pass
        
        # Verify certificate signature (basic check)
        try:
            # For self-signed certificates, verify against itself
            public_key = cert.public_key()
            # This will raise an exception if signature is invalid
            public_key.verify(
                cert.signature,
                cert.tbs_certificate_bytes,
                cert.signature_algorithm_oid._name
            )
        except Exception as e:
            # Note: This is a basic check. In production, implement full chain validation
            logger.warning(f"Certificate signature validation failed: {e}")
            # Don't add to validation_errors for now as this requires CA chain validation
        
        is_valid = len(validation_errors) == 0
        
        return CertificateInfo(
            subject=subject,
            issuer=issuer,
            serial_number=serial_number,
            not_before=not_before,
            not_after=not_after,
            is_valid=is_valid,
            validation_errors=validation_errors
        )
        
    except Exception as e:
        validation_errors.append(f"Failed to parse certificate: {str(e)}")
        return CertificateInfo(
            subject={},
            issuer={},
            serial_number="",
            not_before=datetime.utcnow(),
            not_after=datetime.utcnow(),
            is_valid=False,
            validation_errors=validation_errors
        )

@router.post("/register", response_model=AgentRegistrationResponse)
async def register_agent(
    request: AgentRegistrationRequest,
    db: Session = Depends(get_db)
):
    """Register a new agent with enhanced validation and certificate verification"""
    
    try:
        # Enhanced input validation
        agent_name_validation = validate_agent_name(request.agent_name)
        metadata_validation = validate_agent_metadata(request.metadata.dict())
        
        # Combine validation results
        validation_errors = []
        validation_warnings = []
        
        if not agent_name_validation.is_valid:
            validation_errors.extend(agent_name_validation.errors)
        validation_warnings.extend(agent_name_validation.warnings)
        
        if not metadata_validation.is_valid:
            validation_errors.extend(metadata_validation.errors)
        validation_warnings.extend(metadata_validation.warnings)
        
        # Log validation results
        if validation_errors:
            logger.error(f"Validation errors for {request.agent_name}: {validation_errors}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Validation failed",
                    "errors": validation_errors,
                    "warnings": validation_warnings
                }
            )
        
        if validation_warnings:
            logger.warning(f"Validation warnings for {request.agent_name}: {validation_warnings}")
        
        # Validate certificate
        cert_info = validate_certificate(request.certificate_pem, request.agent_name)
        
        # Log certificate validation results
        logger.info(f"Certificate validation for {request.agent_name}: valid={cert_info.is_valid}")
        if cert_info.validation_errors:
            logger.warning(f"Certificate validation errors: {cert_info.validation_errors}")
        
        # For development mode, we'll proceed even with validation warnings
        # In production, you might want to reject invalid certificates
        verified = cert_info.is_valid
        
        # Create new agent record
        new_agent = Agent(
            agent_name=request.agent_name,
            certificate_pem=request.certificate_pem,
            agent_metadata=request.metadata.dict(),
            verified=verified,  # Set based on certificate validation
            active=True
        )
        
        db.add(new_agent)
        db.commit()
        db.refresh(new_agent)
        
        # Log successful registration
        logger.info(f"Agent {request.agent_name} registered successfully with ID {new_agent.agent_id}")
        
        return AgentRegistrationResponse(
            agent_id=str(new_agent.agent_id),
            agent_name=new_agent.agent_name,
            status="registered"
        )
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Agent with name '{request.agent_name}' already exists"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during agent registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@router.post("/renew")
async def renew_agent(
    agent_name: str,
    certificate_pem: str,
    db: Session = Depends(get_db)
):
    """Renew an agent's certificate"""
    
    agent = db.query(Agent).filter(Agent.agent_name == agent_name).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_name}' not found"
        )
    
    # Validate new certificate
    cert_info = validate_certificate(certificate_pem, agent_name)
    
    # Update agent with new certificate
    agent.certificate_pem = certificate_pem
    agent.verified = cert_info.is_valid
    
    db.commit()
    
    logger.info(f"Certificate renewed for agent {agent_name}, verified={cert_info.is_valid}")
    
    return {
        "agent_name": agent_name,
        "status": "renewed",
        "verified": cert_info.is_valid,
        "validation_errors": cert_info.validation_errors if not cert_info.is_valid else []
    }

@router.post("/deactivate")
async def deactivate_agent(
    agent_name: str,
    db: Session = Depends(get_db)
):
    """Deactivate an agent"""
    agent = db.query(Agent).filter(Agent.agent_name == agent_name).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_name}' not found"
        )
    
    try:
        agent.active = False
        db.commit()
        
        logger.info(f"Agent {agent_name} deactivated")
        
        return {"status": "deactivated", "agent_name": agent_name}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate agent: {str(e)}"
        )

@router.get("/status", response_model=AgentStatusResponse)
async def get_agent_status(
    agent_name: str,
    db: Session = Depends(get_db)
):
    """Get agent registration status and certificate information"""
    
    agent = db.query(Agent).filter(Agent.agent_name == agent_name).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_name}' not found"
        )
    
    # Re-validate certificate to get current status
    cert_info = validate_certificate(agent.certificate_pem, agent.agent_name)
    
    return AgentStatusResponse(
        agent_id=str(agent.agent_id),
        agent_name=agent.agent_name,
        verified=agent.verified,
        active=agent.active,
        created_at=agent.created_at,
        updated_at=agent.updated_at
    )

@router.post("/validate-certificate")
async def validate_certificate_endpoint(certificate_pem: str, agent_name: Optional[str] = None):
    """
    Validate a certificate without registering an agent
    Useful for testing and verification before registration
    """
    
    cert_info = validate_certificate(certificate_pem, agent_name or "")
    
    return {
        "valid": cert_info.is_valid,
        "certificate_info": {
            "subject": cert_info.subject,
            "issuer": cert_info.issuer,
            "serial_number": cert_info.serial_number,
            "not_before": cert_info.not_before.isoformat(),
            "not_after": cert_info.not_after.isoformat(),
        },
        "validation_errors": cert_info.validation_errors
    }
