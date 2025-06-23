"""
Enhanced validation utilities for ParkBench API

Provides JSON schema validation, custom validators, and enhanced input validation
beyond what Pydantic provides by default.
"""

import json
import re
import validators
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import logging
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Load JSON schemas
SCHEMA_DIR = Path(__file__).parent / "schemas"

def load_schema(schema_name: str) -> Dict[str, Any]:
    """Load a JSON schema from the schemas directory"""
    schema_path = SCHEMA_DIR / f"{schema_name}.json"
    try:
        with open(schema_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Schema file not found: {schema_path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in schema file {schema_path}: {e}")
        return {}

# Load schemas once at module import
AGENT_REGISTRATION_SCHEMA = load_schema("agent_registration")
A2A_NEGOTIATION_SCHEMA = load_schema("a2a_negotiation")
A2A_DESCRIPTOR_SCHEMA = load_schema("a2a_descriptor")

class ValidationError(Exception):
    """Custom validation error with detailed information"""
    def __init__(self, message: str, field: str = None, value: Any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(message)

class ValidationResult:
    """Result of validation with errors and warnings"""
    def __init__(self):
        self.is_valid = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.field_errors: Dict[str, List[str]] = {}
    
    def add_error(self, message: str, field: str = None):
        """Add a validation error"""
        self.is_valid = False
        self.errors.append(message)
        if field:
            if field not in self.field_errors:
                self.field_errors[field] = []
            self.field_errors[field].append(message)
    
    def add_warning(self, message: str):
        """Add a validation warning"""
        self.warnings.append(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "field_errors": self.field_errors
        }

def validate_agent_name(agent_name: str) -> ValidationResult:
    """
    Validate agent name according to ParkBench specification
    
    Requirements:
    - DNS-style naming (alphanumeric, dots, hyphens)
    - No consecutive dots
    - No leading/trailing dots or hyphens
    - Reasonable length limits
    """
    result = ValidationResult()
    
    if not agent_name:
        result.add_error("Agent name is required", "agent_name")
        return result
    
    # Length validation
    if len(agent_name) < 3:
        result.add_error("Agent name must be at least 3 characters", "agent_name")
    elif len(agent_name) > 253:
        result.add_error("Agent name must not exceed 253 characters", "agent_name")
    
    # Pattern validation
    if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9.-]*[a-zA-Z0-9])?$', agent_name):
        result.add_error("Agent name must contain only alphanumeric characters, dots, and hyphens", "agent_name")
    
    # No consecutive dots
    if '..' in agent_name:
        result.add_error("Agent name must not contain consecutive dots", "agent_name")
    
    # Domain-like structure recommendation
    if '.' not in agent_name:
        result.add_warning("Agent name should follow DNS-style naming (e.g., 'agent.example.com')")
    
    return result

def validate_api_endpoint(endpoint: str) -> ValidationResult:
    """Validate API endpoint URL"""
    result = ValidationResult()
    
    if not endpoint:
        result.add_error("API endpoint is required", "api_endpoint")
        return result
    
    # Basic URL validation
    if not validators.url(endpoint):
        result.add_error("API endpoint must be a valid URL", "api_endpoint")
        return result
    
    parsed = urlparse(endpoint)
    
    # HTTPS recommendation for production
    if parsed.scheme == 'http':
        result.add_warning("Consider using HTTPS for production API endpoints")
    elif parsed.scheme not in ['http', 'https']:
        result.add_error("API endpoint must use HTTP or HTTPS protocol", "api_endpoint")
    
    # Port validation
    if parsed.port and (parsed.port < 1 or parsed.port > 65535):
        result.add_error("API endpoint port must be between 1 and 65535", "api_endpoint")
    
    return result

def validate_skills(skills: List[str]) -> ValidationResult:
    """Validate agent skills list"""
    result = ValidationResult()
    
    if not skills:
        result.add_warning("Agent should specify at least one skill")
        return result
    
    if len(skills) > 50:
        result.add_error("Agent cannot have more than 50 skills", "skills")
    
    for i, skill in enumerate(skills):
        if not skill or not skill.strip():
            result.add_error(f"Skill at index {i} cannot be empty", "skills")
        elif len(skill) > 100:
            result.add_error(f"Skill '{skill}' exceeds 100 character limit", "skills")
        elif not re.match(r'^[a-zA-Z0-9_-]+$', skill.replace(' ', '-')):
            result.add_warning(f"Skill '{skill}' should use alphanumeric characters, hyphens, and underscores")
    
    # Check for duplicates
    unique_skills = set(skills)
    if len(unique_skills) != len(skills):
        result.add_warning("Skills list contains duplicates")
    
    return result

def validate_protocols(protocols: List[str]) -> ValidationResult:
    """Validate supported protocols"""
    result = ValidationResult()
    
    valid_protocols = ["REST", "GraphQL", "A2A", "WebSocket", "gRPC"]
    
    if not protocols:
        result.add_error("At least one protocol must be specified", "protocols")
        return result
    
    for protocol in protocols:
        if protocol not in valid_protocols:
            result.add_error(f"Unsupported protocol '{protocol}'. Valid protocols: {valid_protocols}", "protocols")
    
    # A2A compliance check
    if "A2A" in protocols:
        result.add_warning("A2A protocol support detected - ensure a2a_compliant is set to true")
    
    return result

def validate_a2a_capabilities(a2a_data: Dict[str, Any], a2a_compliant: bool) -> ValidationResult:
    """Validate A2A capabilities"""
    result = ValidationResult()
    
    if a2a_compliant and not a2a_data:
        result.add_error("A2A capabilities must be specified when a2a_compliant is true", "a2a")
        return result
    
    if not a2a_compliant and a2a_data:
        result.add_warning("A2A capabilities specified but a2a_compliant is false")
    
    if a2a_data:
        # Validate supported tasks
        supported_tasks = a2a_data.get('supported_tasks', [])
        if not supported_tasks:
            result.add_error("A2A capabilities must specify at least one supported task", "a2a.supported_tasks")
        elif len(supported_tasks) > 20:
            result.add_error("A2A cannot support more than 20 tasks", "a2a.supported_tasks")
        
        # Validate token budget
        token_budget = a2a_data.get('token_budget', 0)
        if token_budget < 0:
            result.add_error("Token budget cannot be negative", "a2a.token_budget")
        elif token_budget == 0:
            result.add_warning("Token budget is 0 - agent may not be able to perform tasks")
        elif token_budget > 1000000:
            result.add_warning("Token budget is very high - consider if this is intentional")
        
        # Validate context requirements
        context_required = a2a_data.get('context_required', [])
        if len(context_required) > 10:
            result.add_error("A2A cannot require more than 10 context fields", "a2a.context_required")
    
    return result

def validate_version(version: str) -> ValidationResult:
    """Validate semantic version format"""
    result = ValidationResult()
    
    if not version:
        result.add_error("Version is required", "version")
        return result
    
    # Semantic versioning pattern
    semver_pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*))?(?:\+([a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*))?$'
    if not re.match(semver_pattern, version):
        result.add_error("Version must follow semantic versioning (e.g., '1.0.0', '2.1.3-beta')", "version")
    
    return result

def validate_contact_info(contact: str) -> ValidationResult:
    """Validate maintainer contact information"""
    result = ValidationResult()
    
    if not contact:
        result.add_error("Maintainer contact is required", "maintainer_contact")
        return result
    
    # Check if it's an email
    if '@' in contact:
        if not validators.email(contact):
            result.add_error("Invalid email address format", "maintainer_contact")
    # Check if it's a URL
    elif contact.startswith(('http://', 'https://')):
        if not validators.url(contact):
            result.add_error("Invalid URL format", "maintainer_contact")
    else:
        result.add_warning("Contact should be an email address or URL for best practices")
    
    return result

def validate_agent_metadata(metadata: Dict[str, Any]) -> ValidationResult:
    """
    Comprehensive validation of agent metadata
    
    Combines multiple validation checks and provides detailed feedback
    """
    result = ValidationResult()
    
    # Validate individual fields
    validations = [
        validate_api_endpoint(metadata.get('api_endpoint', '')),
        validate_skills(metadata.get('skills', [])),
        validate_protocols(metadata.get('protocols', [])),
        validate_version(metadata.get('version', '')),
        validate_contact_info(metadata.get('maintainer_contact', '')),
        validate_a2a_capabilities(
            metadata.get('a2a', {}), 
            metadata.get('a2a_compliant', False)
        )
    ]
    
    # Combine all validation results
    for validation in validations:
        if not validation.is_valid:
            result.is_valid = False
        result.errors.extend(validation.errors)
        result.warnings.extend(validation.warnings)
        result.field_errors.update(validation.field_errors)
    
    # Cross-field validations
    protocols = metadata.get('protocols', [])
    a2a_compliant = metadata.get('a2a_compliant', False)
    
    if a2a_compliant and 'A2A' not in protocols:
        result.add_warning("Agent is A2A compliant but 'A2A' not listed in protocols")
    
    # Check pricing model
    pricing_model = metadata.get('pricing_model', '')
    valid_pricing = ['free', 'pay-per-use', 'subscription', 'enterprise', 'custom']
    if pricing_model and pricing_model not in valid_pricing:
        result.add_warning(f"Pricing model '{pricing_model}' is not standard. Consider: {valid_pricing}")
    
    return result

def validate_negotiation_request(data: Dict[str, Any]) -> ValidationResult:
    """Validate A2A negotiation request"""
    result = ValidationResult()
    
    # Required fields
    required_fields = ['initiatingAgentName', 'requestedTask', 'context']
    for field in required_fields:
        if field not in data or not data[field]:
            result.add_error(f"Field '{field}' is required", field)
    
    # Validate agent names
    if 'initiatingAgentName' in data:
        agent_validation = validate_agent_name(data['initiatingAgentName'])
        if not agent_validation.is_valid:
            result.add_error("Invalid initiating agent name", 'initiatingAgentName')
    
    # Validate task name
    task = data.get('requestedTask', '')
    if task:
        if len(task) > 100:
            result.add_error("Task name cannot exceed 100 characters", 'requestedTask')
        if not re.match(r'^[a-zA-Z0-9_-]+$', task.replace(' ', '-')):
            result.add_warning("Task name should use alphanumeric characters, hyphens, and underscores")
    
    # Validate context
    context = data.get('context', {})
    if not isinstance(context, dict):
        result.add_error("Context must be an object", 'context')
    elif len(json.dumps(context)) > 10000:  # 10KB limit
        result.add_error("Context size cannot exceed 10KB", 'context')
    
    return result

def enhanced_validation_middleware(validation_func):
    """
    Decorator to add enhanced validation to API endpoints
    
    Usage:
        @enhanced_validation_middleware(validate_agent_metadata)
        async def my_endpoint(data: dict):
            # endpoint logic
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract data from request (this is simplified - in practice, 
            # you'd need to handle different argument patterns)
            data = kwargs.get('request') or (args[0] if args else {})
            
            if hasattr(data, 'dict'):
                data = data.dict()
            
            # Run validation
            validation_result = validation_func(data)
            
            # Log validation results
            if not validation_result.is_valid:
                logger.warning(f"Validation failed for {func.__name__}: {validation_result.errors}")
            if validation_result.warnings:
                logger.info(f"Validation warnings for {func.__name__}: {validation_result.warnings}")
            
            # For strict validation, you could raise an exception here
            # For now, we'll let the endpoint handle the validation result
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator 