"""
ParkBench Discovery Client

Handles agent search, profile retrieval, and A2A descriptor access.
"""

import requests
from typing import Dict, Any, List, Optional
import urllib.parse

class DiscoveryClient:
    """Client for ParkBench agent discovery operations"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize discovery client
        
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
    
    def search(self, 
               skill: Optional[str] = None,
               protocol: Optional[str] = None,
               a2a_compliant: Optional[bool] = None,
               verified: Optional[bool] = None,
               active: Optional[bool] = True,
               limit: int = 50,
               offset: int = 0) -> List[Dict[str, Any]]:
        """
        Search for agents based on criteria
        
        Args:
            skill: Filter by specific skill
            protocol: Filter by protocol (REST, GraphQL, A2A)
            a2a_compliant: Filter by A2A compliance
            verified: Filter by verification status
            active: Filter by active status
            limit: Maximum number of results (default: 50)
            offset: Offset for pagination (default: 0)
            
        Returns:
            list: List of matching agents
            
        Raises:
            requests.HTTPError: If search fails
        """
        url = f"{self.base_url}/api/v1/agents/search"
        
        params = {}
        if skill is not None:
            params['skill'] = skill
        if protocol is not None:
            params['protocol'] = protocol
        if a2a_compliant is not None:
            params['a2a_compliant'] = a2a_compliant
        if verified is not None:
            params['verified'] = verified
        if active is not None:
            params['active'] = active
        if limit != 50:
            params['limit'] = limit
        if offset != 0:
            params['offset'] = offset
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def get_profile(self, agent_name: str) -> Dict[str, Any]:
        """
        Get complete agent profile
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            dict: Complete agent profile including metadata
            
        Raises:
            requests.HTTPError: If profile retrieval fails
        """
        # URL encode the agent name to handle special characters
        encoded_name = urllib.parse.quote(agent_name, safe='')
        url = f"{self.base_url}/api/v1/agents/{encoded_name}"
        
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.json()
    
    def get_a2a_descriptor(self, agent_name: str) -> Dict[str, Any]:
        """
        Get A2A descriptors for an agent
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            dict: A2A descriptors including supported tasks and capabilities
            
        Raises:
            requests.HTTPError: If A2A descriptor retrieval fails
        """
        # URL encode the agent name to handle special characters
        encoded_name = urllib.parse.quote(agent_name, safe='')
        url = f"{self.base_url}/api/v1/agents/{encoded_name}/a2a"
        
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.json()
    
    def list_all(self, 
                 active_only: bool = True,
                 limit: int = 50,
                 offset: int = 0) -> List[Dict[str, Any]]:
        """
        List all agents (with optional filtering)
        
        Args:
            active_only: Only return active agents
            limit: Maximum number of results (default: 50)
            offset: Offset for pagination (default: 0)
            
        Returns:
            list: List of agents
            
        Raises:
            requests.HTTPError: If listing fails
        """
        url = f"{self.base_url}/api/v1/agents"
        
        params = {
            'active_only': active_only,
            'limit': limit,
            'offset': offset
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def find_by_skills(self, skills: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Find agents that have any of the specified skills
        
        Args:
            skills: List of skills to search for
            **kwargs: Additional search parameters
            
        Returns:
            list: Agents matching any of the skills
        """
        all_agents = []
        for skill in skills:
            agents = self.search(skill=skill, **kwargs)
            # Avoid duplicates by checking agent_id
            existing_ids = {agent['agent_id'] for agent in all_agents}
            for agent in agents:
                if agent['agent_id'] not in existing_ids:
                    all_agents.append(agent)
        
        return all_agents
    
    def find_a2a_agents(self, task: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Find A2A-compliant agents that support a specific task
        
        Args:
            task: Task to search for
            **kwargs: Additional search parameters
            
        Returns:
            list: A2A agents supporting the task
        """
        # First find A2A compliant agents
        agents = self.search(a2a_compliant=True, **kwargs)
        
        # Filter by those that support the specific task
        matching_agents = []
        for agent in agents:
            try:
                a2a_desc = self.get_a2a_descriptor(agent['agent_name'])
                supported_tasks = a2a_desc.get('supported_tasks', [])
                if any(task.lower() in supported_task.lower() for supported_task in supported_tasks):
                    matching_agents.append(agent)
            except requests.HTTPError:
                # Skip agents that don't have A2A descriptors
                continue
        
        return matching_agents
    
    def get_agent_capabilities(self, agent_name: str) -> Dict[str, Any]:
        """
        Get summarized capabilities of an agent
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            dict: Summary of agent capabilities
        """
        profile = self.get_profile(agent_name)
        metadata = profile.get('metadata', {})
        
        capabilities = {
            'agent_name': agent_name,
            'description': metadata.get('description', ''),
            'skills': metadata.get('skills', []),
            'protocols': metadata.get('protocols', []),
            'a2a_compliant': metadata.get('a2a_compliant', False),
            'verified': profile.get('verified', False),
            'active': profile.get('active', False),
            'api_endpoint': metadata.get('api_endpoint', ''),
            'pricing_model': metadata.get('pricing_model', 'unknown')
        }
        
        # Add A2A specific capabilities if available
        if capabilities['a2a_compliant']:
            try:
                a2a_desc = self.get_a2a_descriptor(agent_name)
                capabilities['a2a'] = {
                    'supported_tasks': a2a_desc.get('supported_tasks', []),
                    'negotiation': a2a_desc.get('negotiation', False),
                    'context_required': a2a_desc.get('context_required', []),
                    'token_budget': a2a_desc.get('token_budget', 0)
                }
            except requests.HTTPError:
                capabilities['a2a'] = None
        
        return capabilities
