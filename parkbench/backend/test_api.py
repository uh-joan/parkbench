#!/usr/bin/env python3
"""
Simple test script to validate ParkBench API functionality
"""

import requests
import json
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:9000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ Health check passed")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_register_agent():
    """Test agent registration"""
    print("🔍 Testing agent registration...")
    
    # Sample agent registration data
    agent_data = {
        "agentName": "test-agent.agents.example.com",
        "certificatePEM": "-----BEGIN CERTIFICATE-----\nMIIC...EXAMPLE...CERT\n-----END CERTIFICATE-----",
        "metadata": {
            "description": "Test agent for validation",
            "version": "1.0.0",
            "maintainer_contact": "test@example.com",
            "api_endpoint": "https://test-agent.example.com/api",
            "protocols": ["REST", "A2A"],
            "a2a_compliant": True,
            "skills": ["test-task", "validation"],
            "input_formats": ["JSON"],
            "output_formats": ["JSON"],
            "pricing_model": "free",
            "public_key": "ssh-rsa AAAAB3...EXAMPLE...KEY",
            "a2a": {
                "supported_tasks": ["test-task", "validation", "demo"],
                "negotiation": True,
                "context_required": ["task_type"],
                "token_budget": 1000
            }
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/register", json=agent_data)
        if response.status_code == 201 or response.status_code == 200:
            data = response.json()
            print(f"✅ Agent registered successfully: {data['agentName']}")
            return data
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return None

def test_search_agents():
    """Test agent search functionality"""
    print("🔍 Testing agent search...")
    
    try:
        # Search for all agents
        response = requests.get(f"{BASE_URL}/api/v1/agents/search")
        if response.status_code == 200:
            agents = response.json()
            print(f"✅ Found {len(agents)} agents")
            
            # Search with skill filter
            response = requests.get(f"{BASE_URL}/api/v1/agents/search?skill=test-task")
            if response.status_code == 200:
                filtered_agents = response.json()
                print(f"✅ Found {len(filtered_agents)} agents with 'test-task' skill")
                return True
            
        print(f"❌ Search failed: {response.status_code} - {response.text}")
        return False
        
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return False

def test_get_agent_profile():
    """Test getting agent profile"""
    print("🔍 Testing agent profile retrieval...")
    
    agent_name = "test-agent.agents.example.com"
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/agents/{agent_name}")
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ Retrieved profile for: {profile['agent_name']}")
            return profile
        else:
            print(f"❌ Profile retrieval failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Profile retrieval failed: {e}")
        return None

def test_a2a_negotiation():
    """Test A2A task negotiation"""
    print("🔍 Testing A2A negotiation...")
    
    negotiation_data = {
        "initiatingAgentName": "test-agent.agents.example.com",
        "requestedTask": "test-task",
        "context": {"priority": "high", "deadline": "2024-01-01"},
        "preferredCapabilities": {"negotiation": True, "token_budget": 500}
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/a2a/negotiate", json=negotiation_data)
        if response.status_code == 200:
            result = response.json()
            candidates = result.get("candidateAgents", [])
            print(f"✅ Found {len(candidates)} candidate agents for negotiation")
            return result
        else:
            print(f"❌ Negotiation failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Negotiation failed: {e}")
        return None

def main():
    """Run all tests"""
    print("🚀 Starting ParkBench API Tests\n")
    
    # Test sequence
    tests = [
        test_health_check,
        test_register_agent,
        test_search_agents,
        test_get_agent_profile,
        test_a2a_negotiation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Add spacing between tests
        except Exception as e:
            print(f"❌ Test failed with exception: {e}\n")
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! ParkBench API is working correctly.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the API implementation.")
        sys.exit(1)

if __name__ == "__main__":
    main() 