"""
ParkBench Session Client

Handles A2A session management including initiation, monitoring, and updates.
"""

import requests
from typing import Dict, Any, Optional, List
import time

class SessionClient:
    """Client for ParkBench A2A session management"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize session client
        
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
    
    def initiate(self,
                 initiating_agent_name: str,
                 target_agent_name: str,
                 task: str,
                 context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiate an A2A session
        
        Args:
            initiating_agent_name: Name of the requesting agent
            target_agent_name: Name of the target agent
            task: Task to be performed
            context: Session context
            
        Returns:
            dict: Session information with session_id and token
            
        Raises:
            requests.HTTPError: If session initiation fails
        """
        url = f"{self.base_url}/api/v1/a2a/session/initiate"
        
        payload = {
            "initiatingAgentName": initiating_agent_name,
            "targetAgentName": target_agent_name,
            "task": task,
            "context": context
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def get_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get the status of an A2A session
        
        Args:
            session_id: ID of the session
            
        Returns:
            dict: Session status information
            
        Raises:
            requests.HTTPError: If status retrieval fails
        """
        url = f"{self.base_url}/api/v1/a2a/session/{session_id}/status"
        
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.json()
    
    def update(self, 
               session_id: str, 
               status: str, 
               context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Update an A2A session status and context
        
        Args:
            session_id: ID of the session
            status: New status (active, completed, failed)
            context: Updated context (optional)
            
        Returns:
            dict: Update response
            
        Raises:
            requests.HTTPError: If update fails
        """
        url = f"{self.base_url}/api/v1/a2a/session/{session_id}"
        
        payload = {"status": status}
        if context is not None:
            payload["context"] = context
        
        response = self.session.put(url, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def complete(self, session_id: str, results: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Mark a session as completed
        
        Args:
            session_id: ID of the session
            results: Optional results to include in context
            
        Returns:
            dict: Update response
        """
        context = None
        if results:
            context = {"results": results}
        
        return self.update(session_id, "completed", context)
    
    def fail(self, session_id: str, error: Optional[str] = None) -> Dict[str, Any]:
        """
        Mark a session as failed
        
        Args:
            session_id: ID of the session
            error: Optional error message
            
        Returns:
            dict: Update response
        """
        context = None
        if error:
            context = {"error": error}
        
        return self.update(session_id, "failed", context)
    
    def terminate(self, session_id: str) -> Dict[str, Any]:
        """
        Terminate (mark as failed) an A2A session
        
        Args:
            session_id: ID of the session
            
        Returns:
            dict: Termination response
            
        Raises:
            requests.HTTPError: If termination fails
        """
        url = f"{self.base_url}/api/v1/a2a/session/{session_id}"
        
        response = self.session.delete(url)
        response.raise_for_status()
        
        return response.json()
    
    def list_sessions(self,
                     initiating_agent: Optional[str] = None,
                     target_agent: Optional[str] = None,
                     status_filter: Optional[str] = None,
                     limit: int = 50,
                     offset: int = 0) -> Dict[str, Any]:
        """
        List A2A sessions with optional filtering
        
        Args:
            initiating_agent: Filter by initiating agent
            target_agent: Filter by target agent
            status_filter: Filter by status (active, completed, failed)
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            dict: List of sessions with metadata
            
        Raises:
            requests.HTTPError: If listing fails
        """
        url = f"{self.base_url}/api/v1/a2a/sessions"
        
        params = {
            "limit": limit,
            "offset": offset
        }
        
        if initiating_agent:
            params["initiating_agent"] = initiating_agent
        if target_agent:
            params["target_agent"] = target_agent
        if status_filter:
            params["status_filter"] = status_filter
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def wait_for_completion(self,
                           session_id: str,
                           timeout: int = 300,
                           poll_interval: int = 5) -> Dict[str, Any]:
        """
        Wait for a session to complete (or fail)
        
        Args:
            session_id: ID of the session
            timeout: Maximum time to wait in seconds
            poll_interval: How often to check status in seconds
            
        Returns:
            dict: Final session status
            
        Raises:
            TimeoutError: If session doesn't complete within timeout
            requests.HTTPError: If status checks fail
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_status(session_id)
            session_status = status.get('status', '')
            
            if session_status in ['completed', 'failed']:
                return status
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Session {session_id} did not complete within {timeout} seconds")
    
    def create_session_context(self,
                              task_parameters: Dict[str, Any],
                              priority: str = "normal",
                              timeout_minutes: int = 60,
                              **kwargs) -> Dict[str, Any]:
        """
        Create a standardized session context
        
        Args:
            task_parameters: Parameters specific to the task
            priority: Task priority (low, normal, high, urgent)
            timeout_minutes: Session timeout in minutes
            **kwargs: Additional context fields
            
        Returns:
            dict: Session context
        """
        context = {
            "task_parameters": task_parameters,
            "priority": priority,
            "timeout_minutes": timeout_minutes,
            "created_at": time.time()
        }
        
        # Add any additional context
        context.update(kwargs)
        
        return context
    
    def get_session_history(self, agent_name: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get session history for a specific agent
        
        Args:
            agent_name: Name of the agent
            limit: Maximum number of sessions to return
            
        Returns:
            list: List of sessions involving the agent
        """
        # Get sessions where agent is initiator
        initiator_sessions = self.list_sessions(
            initiating_agent=agent_name, 
            limit=limit//2
        ).get('sessions', [])
        
        # Get sessions where agent is target
        target_sessions = self.list_sessions(
            target_agent=agent_name, 
            limit=limit//2
        ).get('sessions', [])
        
        # Combine and deduplicate by session_id
        all_sessions = initiator_sessions + target_sessions
        seen_ids = set()
        unique_sessions = []
        
        for session in all_sessions:
            session_id = session.get('session_id')
            if session_id not in seen_ids:
                seen_ids.add(session_id)
                unique_sessions.append(session)
        
        # Sort by creation time (most recent first)
        return sorted(unique_sessions, 
                     key=lambda x: x.get('created_at', ''), 
                     reverse=True)[:limit]
