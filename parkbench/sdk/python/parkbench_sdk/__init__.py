"""
ParkBench Python SDK

A comprehensive SDK for interacting with the ParkBench AI agent identity, 
discovery, negotiation, and orchestration platform.

Usage:
    # Initialize the main client
    client = ParkBenchClient("http://localhost:9000")
    
    # Register an agent
    metadata = client.registration.create_metadata_template(
        description="My AI Agent",
        version="1.0.0",
        maintainer_contact="me@example.com",
        api_endpoint="https://myagent.example.com/api",
        skills=["text-processing", "analysis"],
        supported_tasks=["summarization", "analysis"]
    )
    
    result = client.registration.register(
        agent_name="myagent.example.com",
        certificate_pem=my_cert,
        metadata=metadata
    )
    
    # Search for agents
    agents = client.discovery.search(skill="text-processing")
    
    # Negotiate for a task
    candidates = client.negotiation.negotiate(
        initiating_agent_name="myagent.example.com",
        requested_task="summarization",
        context={"priority": "high"},
        preferred_capabilities={"negotiation": True}
    )
    
    # Initiate an A2A session
    session = client.sessions.initiate(
        initiating_agent_name="myagent.example.com",
        target_agent_name="target.example.com",
        task="summarization",
        context={"input": "Long text to summarize..."}
    )
"""

from typing import Optional
from .registration import RegistrationClient
from .discovery import DiscoveryClient
from .negotiation import NegotiationClient
from .sessions import SessionClient

__version__ = "0.1.0"
__author__ = "ParkBench Team"
__email__ = "team@parkbench.dev"

class ParkBenchClient:
    """
    Main ParkBench SDK client that provides access to all sub-clients.
    
    This is the primary entry point for the ParkBench SDK. It creates
    and manages instances of all the specialized clients for different
    aspects of the ParkBench platform.
    
    Attributes:
        registration: Client for agent registration operations
        discovery: Client for agent discovery and search
        negotiation: Client for A2A task negotiation
        sessions: Client for A2A session management
    """
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize the ParkBench client
        
        Args:
            base_url: Base URL of the ParkBench API (e.g., "http://localhost:9000")
            api_key: Optional API key for authentication
        
        Example:
            # For local development
            client = ParkBenchClient("http://localhost:9000")
            
            # For production with authentication
            client = ParkBenchClient("https://api.parkbench.io", api_key="your-key")
        """
        self.base_url = base_url
        self.api_key = api_key
        
        # Initialize all sub-clients
        self.registration = RegistrationClient(base_url, api_key)
        self.discovery = DiscoveryClient(base_url, api_key)
        self.negotiation = NegotiationClient(base_url, api_key)
        self.sessions = SessionClient(base_url, api_key)
    
    def health_check(self) -> bool:
        """
        Perform a health check on the ParkBench API
        
        Returns:
            bool: True if the API is healthy, False otherwise
        """
        try:
            import requests
            response = requests.get(f"{self.base_url}/health", timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_api_info(self) -> dict:
        """
        Get API information and version
        
        Returns:
            dict: API information including version and status
        """
        try:
            import requests
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "message": "API unavailable"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Convenience imports for direct access
__all__ = [
    'ParkBenchClient',
    'RegistrationClient', 
    'DiscoveryClient',
    'NegotiationClient',
    'SessionClient',
    '__version__'
]
