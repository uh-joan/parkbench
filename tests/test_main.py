import pytest
from fastapi.testclient import TestClient # Changed import
from fastapi import status
import uuid
import sys
import os

# Add project root to sys.path to allow importing 'main'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the FastAPI app instance and the in-memory database
from main import app, agent_db_internal
# import pytest_asyncio # Not needed for TestClient

# BASE_URL = "http://test" # Not strictly needed for TestClient if using relative paths

# Using a regular pytest fixture for TestClient
@pytest.fixture(scope="function", autouse=True)
def clear_db_before_each_test():
    agent_db_internal.clear() # Clear the in-memory DB before each test
    yield # Pytest fixtures with autouse=True should yield if they do setup/teardown

# Test functions are now synchronous
def test_register_agent_success(client: TestClient): # client fixture provided by pytest-fastapi implicitly or define one
    agent_data = {
        "name": "Test Agent",
        "description": "An agent for testing",
        "version": "1.0.0",
        "maintainer_contact": "test@example.com",
        "api_endpoint": "http://testagent.com/api",
        "protocols": ["REST"],
        "a2a_compliant": False,
        "skills": ["testing"],
        "input_formats": ["JSON"],
        "output_formats": ["JSON"],
        "public_key": "test_pk"
    }
    response = client.post("/agents/register", json=agent_data)

    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert "agent_id" in response_data
    assert response_data["status"] == "registered"

    # Verify it's in our in-memory DB
    agent_id = uuid.UUID(response_data["agent_id"])
    assert agent_id in agent_db_internal
    stored_agent = agent_db_internal[agent_id]
    assert stored_agent.name == agent_data["name"]
    assert stored_agent.version == agent_data["version"]
    assert str(stored_agent.api_endpoint) == agent_data["api_endpoint"]

def test_register_agent_missing_required_fields(client: TestClient):
    # Missing 'name', 'version', 'maintainer_contact', 'api_endpoint', 'protocols', 'a2a_compliant'
    agent_data_missing_fields = {
        "description": "Agent missing fields"
    }
    response = client.post("/agents/register", json=agent_data_missing_fields)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    response_data = response.json()
    assert "detail" in response_data
    error_locs = [err["loc"][-1] for err in response_data["detail"]]
    assert "name" in error_locs
    assert "version" in error_locs
    assert "maintainer_contact" in error_locs
    assert "api_endpoint" in error_locs
    assert "protocols" in error_locs
    assert "a2a_compliant" in error_locs

def test_register_agent_invalid_api_endpoint_url(client: TestClient):
    agent_data = {
        "name": "Invalid URL Agent",
        "version": "1.0",
        "maintainer_contact": "invalid@example.com",
        "api_endpoint": "not-a-valid-url", # Invalid URL
        "protocols": ["REST"],
        "a2a_compliant": True
    }
    response = client.post("/agents/register", json=agent_data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    response_data = response.json()
    assert "detail" in response_data
    assert any(err["loc"] == ["body", "api_endpoint"] for err in response_data["detail"])

def test_register_agent_duplicate(client: TestClient):
    agent_data = {
        "name": "Duplicate Agent",
        "description": "An agent to test duplication",
        "version": "1.1.0",
        "maintainer_contact": "duplicate@example.com",
        "api_endpoint": "http://duplicate.com/api",
        "protocols": ["GraphQL"],
        "a2a_compliant": True,
        "skills": ["duplication_testing"],
    }
    # First registration - should succeed
    response1 = client.post("/agents/register", json=agent_data)
    assert response1.status_code == status.HTTP_201_CREATED

    # Second registration with same name and version - should fail
    response2 = client.post("/agents/register", json=agent_data)

    assert response2.status_code == status.HTTP_409_CONFLICT
    response_data = response2.json()
    assert "detail" in response_data
    assert "already exists" in response_data["detail"]

def test_register_agent_with_a2a_metadata(client: TestClient):
    agent_data = {
        "name": "A2A Test Agent",
        "description": "An agent with A2A metadata",
        "version": "1.0.1",
        "maintainer_contact": "a2a@example.com",
        "api_endpoint": "http://a2aagent.com/api",
        "protocols": ["A2A"],
        "a2a_compliant": True,
        "skills": ["a2a_skill"],
        "input_formats": ["JSON"],
        "output_formats": ["JSON"],
        "a2a": {
            "supported_tasks": ["task1", "task2"],
            "negotiation": True,
            "context_required": ["user_id"],
            "token_budget": 1000
        }
    }
    response = client.post("/agents/register", json=agent_data)

    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    agent_id = uuid.UUID(response_data["agent_id"])

    assert agent_id in agent_db_internal
    stored_agent = agent_db_internal[agent_id]
    assert stored_agent.name == agent_data["name"]
    assert stored_agent.a2a is not None
    assert stored_agent.a2a.supported_tasks == ["task1", "task2"]
    assert stored_agent.a2a.negotiation is True
    assert stored_agent.a2a.context_required == ["user_id"]
    assert stored_agent.a2a.token_budget == 1000

def test_register_agent_minimal_required_fields(client: TestClient):
    agent_data = {
        "name": "Minimal Agent",
        "version": "0.1.0",
        "maintainer_contact": "minimal@example.com",
        "api_endpoint": "http://minimalagent.com/api",
        "protocols": ["REST"],
        "a2a_compliant": False,
    }
    response = client.post("/agents/register", json=agent_data)

    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert "agent_id" in response_data
    assert response_data["status"] == "registered"

    agent_id = uuid.UUID(response_data["agent_id"])
    assert agent_id in agent_db_internal
    stored_agent = agent_db_internal[agent_id]
    assert stored_agent.name == agent_data["name"]
    assert stored_agent.skills == []
    assert stored_agent.input_formats == []
    assert stored_agent.output_formats == []
    assert stored_agent.description is None
    assert stored_agent.public_key is None
    assert stored_agent.a2a is None

# It's good practice to define a client fixture if not relying on pytest-fastapi's auto one
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
