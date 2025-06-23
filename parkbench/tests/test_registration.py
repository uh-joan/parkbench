import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from faker import Faker # For generating fake data
import uuid

from parkbench.backend.api.schemas.agent_registration_models import AgentRegistrationRequest, A2AMetadata, AgentMetadata
from parkbench.backend.db import models as db_models # For checking DB directly if needed
from parkbench.backend.config import settings # For API_PREFIX

fake = Faker()

# Helper to create valid agent registration data
def get_valid_agent_data(agent_name_override=None) -> dict:
    agent_name = agent_name_override if agent_name_override else f"{fake.slug()}.{fake.domain_word()}.com"
    return {
        "agentName": agent_name,
        "certificatePEM": f"-----BEGIN CERTIFICATE-----\n{fake.sha256()}\n-----END CERTIFICATE-----",
        "metadata": {
            "description": fake.sentence(),
            "version": "1.0.0",
            "maintainer_contact": fake.email(),
            "api_endpoint": fake.url(),
            "protocols": ["REST", "A2A"],
            "a2a_compliant": True,
            "skills": [fake.word(), fake.word()],
            "input_formats": ["JSON"],
            "output_formats": ["JSON"],
            "pricing_model": "free",
            "public_key": fake.sha256(),
            "a2a": {
                "supported_tasks": [fake.bs()],
                "negotiation": True,
                "context_required": ["session_id"],
                "token_budget": 3000
            }
        }
    }

def test_register_agent_success(client: TestClient, db_session: Session):
    """Test successful agent registration."""
    agent_data = get_valid_agent_data()

    response = client.post(f"{settings.API_PREFIX}/register", json=agent_data)

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["agentName"] == agent_data["agentName"]
    assert response_data["status"] == "registered"
    assert "agent_id" in response_data
    try:
        uuid.UUID(response_data["agent_id"]) # Check if agent_id is a valid UUID
    except ValueError:
        pytest.fail("agent_id is not a valid UUID")

    # Verify in DB (optional, but good for sanity check)
    db_agent = db_session.query(db_models.Agent).filter(db_models.Agent.agentName == agent_data["agentName"]).first()
    assert db_agent is not None
    assert str(db_agent.agent_id) == response_data["agent_id"]
    assert db_agent.metadata_["description"] == agent_data["metadata"]["description"]

def test_register_agent_duplicate_name(client: TestClient, db_session: Session):
    """Test registration with a duplicate agentName."""
    agent_data = get_valid_agent_data()

    # First registration (should succeed)
    response1 = client.post(f"{settings.API_PREFIX}/register", json=agent_data)
    assert response1.status_code == 201

    # Second registration with the same name (should fail)
    response2 = client.post(f"{settings.API_PREFIX}/register", json=agent_data)
    assert response2.status_code == 409 # Conflict
    assert "already exists" in response2.json()["detail"]

def test_register_agent_invalid_payload_missing_field(client: TestClient):
    """Test registration with a missing required field (e.g., agentName)."""
    agent_data = get_valid_agent_data()
    del agent_data["agentName"]

    response = client.post(f"{settings.API_PREFIX}/register", json=agent_data)
    assert response.status_code == 422 # Unprocessable Entity (FastAPI validation error)

def test_register_agent_invalid_agent_name_format(client: TestClient):
    """Test registration with an invalid agentName format."""
    agent_data = get_valid_agent_data()
    agent_data["agentName"] = "invalid name with spaces" # Invalid format

    response = client.post(f"{settings.API_PREFIX}/register", json=agent_data)
    assert response.status_code == 422 # Unprocessable Entity
    # Check for specific error message if Pydantic model validation is detailed
    # For example: response.json()['detail'][0]['msg'] should indicate the pattern mismatch

def test_register_agent_invalid_certificate_format(client: TestClient):
    """Test registration with an invalid certificatePEM format."""
    agent_data = get_valid_agent_data()
    agent_data["certificatePEM"] = "INVALID CERTIFICATE DATA"

    response = client.post(f"{settings.API_PREFIX}/register", json=agent_data)
    assert response.status_code == 422 # Unprocessable Entity
    details = response.json().get("detail", [])
    assert any("certificatePEM must be a valid PEM-formatted certificate" in error.get("msg", "") for error in details)


def test_register_agent_metadata_missing_required_field(client: TestClient):
    """Test registration with missing required field in metadata.a2a."""
    agent_data = get_valid_agent_data()
    del agent_data["metadata"]["a2a"]["token_budget"] # Remove a required field

    response = client.post(f"{settings.API_PREFIX}/register", json=agent_data)
    assert response.status_code == 422

def test_register_agent_metadata_invalid_protocol(client: TestClient):
    """Test registration with an invalid protocol in metadata."""
    agent_data = get_valid_agent_data()
    agent_data["metadata"]["protocols"] = ["REST", "INVALID_PROTOCOL"]

    response = client.post(f"{settings.API_PREFIX}/register", json=agent_data)
    assert response.status_code == 422
    details = response.json().get("detail", [])
    assert any("Invalid protocol: INVALID_PROTOCOL" in error.get("msg", "") for error in details)


# Example of how to add more tests:
# - Test with very long agentName (if there's a max length constraint beyond DB)
# - Test with empty certificatePEM
# - Test various edge cases for metadata fields (e.g., negative token_budget)
#   (Pydantic's `ge=0` for token_budget should handle this)

# To run tests:
# Ensure pytest and httpx are installed (e.g., from requirements-dev.txt)
# From the root of the project (`parkbench/`):
# PYTHONPATH=. pytest tests/
# or simply `pytest` if your project structure is standard.
# The PYTHONPATH=. ensures that `parkbench.backend` can be imported.
# Alternatively, install the parkbench package in editable mode if it were a full package:
# pip install -e . (if setup.py or pyproject.toml exists for the backend as a package)
# For now, PYTHONPATH works.
# Also, ensure the .env file is not interfering, or set test-specific env vars if needed.
# The conftest.py sets DATABASE_URL="sqlite:///:memory:", which should override any .env.
# The `client` fixture handles app creation and overrides `get_db`.
# The `db_session` fixture provides a transactional session for each test.
