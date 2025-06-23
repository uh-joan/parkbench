"""
ParkBench Negotiation Client

Handles A2A task negotiation and candidate agent discovery.
"""

import requests
from typing import Dict, Any, List, Optional

class NegotiationClient:
    """Client for ParkBench A2A negotiation operations"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize negotiation client
        
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
    
    def negotiate(self, 
                  initiating_agent_name: str,
                  requested_task: str,
                  context: Dict[str, Any],
                  preferred_capabilities: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Find candidate agents for a task through negotiation
        
        Args:
            initiating_agent_name: Name of the requesting agent
            requested_task: Task to be performed
            context: Task context and requirements
            preferred_capabilities: Preferred agent capabilities
            
        Returns:
            dict: Negotiation response with candidate agents
            
        Raises:
            requests.HTTPError: If negotiation fails
        """
        url = f"{self.base_url}/api/v1/a2a/negotiate"
        
        payload = {
            "initiatingAgentName": initiating_agent_name,
            "requestedTask": requested_task,
            "context": context,
            "preferredCapabilities": preferred_capabilities or {}
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def find_best_match(self,
                        initiating_agent_name: str,
                        requested_task: str,
                        context: Dict[str, Any],
                        preferred_capabilities: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Find the best matching agent for a task
        
        Args:
            initiating_agent_name: Name of the requesting agent
            requested_task: Task to be performed
            context: Task context and requirements
            preferred_capabilities: Preferred agent capabilities
            
        Returns:
            dict: Best matching agent or None if no matches
        """
        result = self.negotiate(
            initiating_agent_name, 
            requested_task, 
            context, 
            preferred_capabilities
        )
        
        candidates = result.get('candidateAgents', [])
        if not candidates:
            return None
        
        # Return the highest scoring candidate
        return max(candidates, key=lambda x: x.get('matchScore', 0))
    
    def filter_candidates(self,
                         candidates: List[Dict[str, Any]],
                         min_score: float = 0.0,
                         requires_negotiation: bool = False,
                         min_token_budget: int = 0) -> List[Dict[str, Any]]:
        """
        Filter candidate agents based on criteria
        
        Args:
            candidates: List of candidate agents
            min_score: Minimum match score required
            requires_negotiation: Whether negotiation capability is required
            min_token_budget: Minimum token budget required
            
        Returns:
            list: Filtered candidates
        """
        filtered = []
        
        for candidate in candidates:
            # Check minimum score
            if candidate.get('matchScore', 0) < min_score:
                continue
            
            # Check negotiation requirement
            if requires_negotiation and not candidate.get('negotiation', False):
                continue
            
            # Check token budget requirement
            if candidate.get('tokenBudget', 0) < min_token_budget:
                continue
            
            filtered.append(candidate)
        
        return filtered
    
    def rank_by_criteria(self,
                        candidates: List[Dict[str, Any]],
                        criteria: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Rank candidates by multiple criteria with weights
        
        Args:
            candidates: List of candidate agents
            criteria: Dict of criteria names to weights
                     Supported: 'match_score', 'negotiation', 'token_budget'
            
        Returns:
            list: Candidates sorted by weighted score (highest first)
        """
        def calculate_weighted_score(candidate):
            score = 0.0
            
            # Match score
            if 'match_score' in criteria:
                score += candidate.get('matchScore', 0) * criteria['match_score']
            
            # Negotiation capability
            if 'negotiation' in criteria:
                negotiation_bonus = 1.0 if candidate.get('negotiation', False) else 0.0
                score += negotiation_bonus * criteria['negotiation']
            
            # Token budget (normalized to 0-1 scale)
            if 'token_budget' in criteria:
                max_budget = max(c.get('tokenBudget', 0) for c in candidates) or 1
                normalized_budget = candidate.get('tokenBudget', 0) / max_budget
                score += normalized_budget * criteria['token_budget']
            
            return score
        
        # Calculate weighted scores and sort
        scored_candidates = [
            {**candidate, '_weighted_score': calculate_weighted_score(candidate)}
            for candidate in candidates
        ]
        
        return sorted(scored_candidates, key=lambda x: x['_weighted_score'], reverse=True)
    
    def create_negotiation_context(self,
                                  task_type: str,
                                  priority: str = "normal",
                                  deadline: Optional[str] = None,
                                  budget_limit: Optional[int] = None,
                                  **kwargs) -> Dict[str, Any]:
        """
        Create a standardized negotiation context
        
        Args:
            task_type: Type of task being requested
            priority: Task priority (low, normal, high, urgent)
            deadline: Task deadline (ISO format string)
            budget_limit: Maximum budget for the task
            **kwargs: Additional context fields
            
        Returns:
            dict: Negotiation context
        """
        context = {
            "task_type": task_type,
            "priority": priority
        }
        
        if deadline:
            context["deadline"] = deadline
        
        if budget_limit:
            context["budget_limit"] = budget_limit
        
        # Add any additional context
        context.update(kwargs)
        
        return context
    
    def create_preferred_capabilities(self,
                                    negotiation: bool = True,
                                    min_token_budget: int = 1000,
                                    required_protocols: Optional[List[str]] = None,
                                    **kwargs) -> Dict[str, Any]:
        """
        Create a standardized preferred capabilities specification
        
        Args:
            negotiation: Whether negotiation capability is preferred
            min_token_budget: Minimum token budget preferred
            required_protocols: List of required protocols
            **kwargs: Additional capability preferences
            
        Returns:
            dict: Preferred capabilities
        """
        capabilities = {
            "negotiation": negotiation,
            "token_budget": min_token_budget
        }
        
        if required_protocols:
            capabilities["protocols"] = required_protocols
        
        # Add any additional capabilities
        capabilities.update(kwargs)
        
        return capabilities
