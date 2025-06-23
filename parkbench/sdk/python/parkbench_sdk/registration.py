"""
ParkBench Registration Client

Handles agent registration, renewal, deactivation, and status checking.
"""

import requests
from typing import Dict, Any, Optional
import json

class RegistrationClient:
    """Client for ParkBench agent registration operations"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize registration client
        
        Args:
            base_url: Base URL of the ParkBench API
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'ParkBench-SDK-Python/0.1.0'
        })
        
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
    
    def register(self, agent_name: str, certificate_pem: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a new agent
        
        Args:
            agent_name: DNS-style agent name (e.g., "agent.example.com")
            certificate_pem: X.509 certificate in PEM format
            metadata: Agent metadata including capabilities and endpoints
            
        Returns:
            dict: Registration response with agent_id and status
            
        Raises:
            requests.HTTPError: If registration fails
        """
        url = f"{self.base_url}/api/v1/register"
        
        payload = {
            "agentName": agent_name,
            "certificatePEM": certificate_pem,
            "metadata": metadata
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def renew(self, agent_name: str, certificate_pem: str) -> Dict[str, Any]:
        """
        Renew an agent's registration
        
        Args:
            agent_name: Name of the agent to renew
            certificate_pem: Updated X.509 certificate in PEM format
            
        Returns:
            dict: Renewal response
            
        Raises:
            requests.HTTPError: If renewal fails
        """
        url = f"{self.base_url}/api/v1/renew"
        
        payload = {
            "agent_name": agent_name,
            "certificate_pem": certificate_pem
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def deactivate(self, agent_name: str) -> Dict[str, Any]:
        """
        Deactivate an agent
        
        Args:
            agent_name: Name of the agent to deactivate
            
        Returns:
            dict: Deactivation response
            
        Raises:
            requests.HTTPError: If deactivation fails
        """
        url = f"{self.base_url}/api/v1/deactivate"
        
        payload = {
            "agent_name": agent_name
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def get_status(self, agent_name: str) -> Dict[str, Any]:
        """
        Get an agent's registration status
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            dict: Agent status information
            
        Raises:
            requests.HTTPError: If status check fails
        """
        url = f"{self.base_url}/api/v1/status"
        
        params = {"agent_name": agent_name}
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def create_metadata_template(self, 
                                description: str,
                                version: str,
                                maintainer_contact: str,
                                api_endpoint: str,
                                skills: list,
                                supported_tasks: list,
                                **kwargs) -> Dict[str, Any]:
        """
        Create a metadata template for agent registration
        
        Args:
            description: Agent description
            version: Agent version
            maintainer_contact: Contact information
            api_endpoint: Agent's API endpoint
            skills: List of skills the agent can perform
            supported_tasks: List of A2A tasks supported
            **kwargs: Additional metadata fields
            
        Returns:
            dict: Complete metadata structure
        """
        metadata = {
            "description": description,
            "version": version,
            "maintainer_contact": maintainer_contact,
            "api_endpoint": api_endpoint,
            "protocols": kwargs.get("protocols", ["REST", "A2A"]),
            "a2a_compliant": kwargs.get("a2a_compliant", True),
            "skills": skills,
            "input_formats": kwargs.get("input_formats", ["JSON"]),
            "output_formats": kwargs.get("output_formats", ["JSON"]),
            "pricing_model": kwargs.get("pricing_model", "free"),
            "public_key": kwargs.get("public_key", ""),
            "a2a": {
                "supported_tasks": supported_tasks,
                "negotiation": kwargs.get("negotiation", True),
                "context_required": kwargs.get("context_required", []),
                "token_budget": kwargs.get("token_budget", 1000)
            }
        }
        
        # Add any additional fields
        for key, value in kwargs.items():
            if key not in metadata:
                metadata[key] = value
        
        return metadata
