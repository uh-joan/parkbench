# ParkBench Python SDK

A comprehensive Python SDK for the **ParkBench AI Agent Platform** - enabling seamless agent identity, discovery, negotiation, and orchestration.

## Installation

```bash
pip install parkbench-sdk
```

For development with certificate validation:
```bash
pip install parkbench-sdk[crypto]
```

## Quick Start

```python
from parkbench_sdk import ParkBenchClient

# Initialize the client
client = ParkBenchClient("http://localhost:9000")

# Check API health
if client.health_check():
    print("ParkBench API is healthy!")

# Register an agent
metadata = client.registration.create_metadata_template(
    description="My Text Processing Agent",
    version="1.0.0",
    maintainer_contact="me@example.com",
    api_endpoint="https://myagent.example.com/api",
    skills=["text-processing", "analysis", "summarization"],
    supported_tasks=["summarization", "sentiment-analysis", "translation"]
)

result = client.registration.register(
    agent_name="myagent.example.com",
    certificate_pem=my_certificate,
    metadata=metadata
)
print(f"Agent registered with ID: {result['agent_id']}")
```

## Features

### 🎯 **Agent Registration**
- Register agents with X.509 certificates
- Manage agent lifecycle (renew, deactivate)
- Status monitoring
- Metadata templates for easy setup

### 🔍 **Agent Discovery** 
- Search agents by skills, protocols, or capabilities
- Retrieve complete agent profiles
- A2A descriptor access
- Advanced filtering and pagination

### 🤝 **A2A Negotiation**
- Find optimal agents for tasks
- Capability-based matching
- Scoring and ranking algorithms
- Preference-based selection

### ⚡ **Session Management**
- Initiate and manage A2A sessions
- Real-time status monitoring
- Session history and analytics
- Timeout and error handling

## Usage Examples

### Agent Registration

```python
# Create metadata for your agent
metadata = client.registration.create_metadata_template(
    description="Advanced Language Model Agent",
    version="2.1.0",
    maintainer_contact="team@mycompany.com",
    api_endpoint="https://api.mycompany.com/llm",
    skills=["text-generation", "code-completion", "translation"],
    supported_tasks=["completion", "translation", "code-generation"],
    protocols=["REST", "A2A"],
    a2a_compliant=True,
    negotiation=True,
    token_budget=5000
)

# Register the agent
registration = client.registration.register(
    agent_name="llm-agent.mycompany.com",
    certificate_pem=certificate_content,
    metadata=metadata
)
```

### Agent Discovery

```python
# Search for text processing agents
agents = client.discovery.search(
    skill="text-processing",
    a2a_compliant=True,
    verified=True
)

# Get detailed agent profile
profile = client.discovery.get_profile("target-agent.example.com")
print(f"Agent: {profile['agent_name']}")
print(f"Skills: {profile['metadata']['skills']}")

# Find A2A agents for specific tasks
a2a_agents = client.discovery.find_a2a_agents("summarization")
for agent in a2a_agents:
    print(f"Found: {agent['agent_name']} - {agent['description']}")
```

### A2A Negotiation

```python
# Create negotiation context
context = client.negotiation.create_negotiation_context(
    task_type="text-summarization",
    priority="high",
    deadline="2024-01-31T18:00:00Z",
    budget_limit=1000
)

# Find candidate agents
result = client.negotiation.negotiate(
    initiating_agent_name="myagent.example.com",
    requested_task="summarization",
    context=context,
    preferred_capabilities={"negotiation": True, "token_budget": 2000}
)

# Get the best match
best_agent = client.negotiation.find_best_match(
    initiating_agent_name="myagent.example.com",
    requested_task="summarization",
    context=context
)

if best_agent:
    print(f"Best match: {best_agent['agentName']} (score: {best_agent['matchScore']})")
```

### Session Management

```python
# Create session context
session_context = client.sessions.create_session_context(
    task_parameters={
        "text": "Long document to summarize...",
        "length": "short",
        "style": "bullet-points"
    },
    priority="high",
    timeout_minutes=30
)

# Initiate A2A session
session = client.sessions.initiate(
    initiating_agent_name="myagent.example.com",
    target_agent_name="summarizer.example.com",
    task="summarization",
    context=session_context
)

print(f"Session started: {session['session_id']}")

# Monitor session status
try:
    final_status = client.sessions.wait_for_completion(
        session_id=session['session_id'],
        timeout=300,  # 5 minutes
        poll_interval=10
    )
    print(f"Session completed: {final_status['status']}")
    
except TimeoutError:
    print("Session timed out")
    client.sessions.terminate(session['session_id'])
```

## Advanced Usage

### Custom Client Configuration

```python
# With authentication
client = ParkBenchClient(
    base_url="https://api.parkbench.io",
    api_key="your-api-key"
)

# Access individual clients
registration_client = client.registration
discovery_client = client.discovery
negotiation_client = client.negotiation
session_client = client.sessions
```

### Error Handling

```python
import requests

try:
    agents = client.discovery.search(skill="nonexistent-skill")
except requests.HTTPError as e:
    if e.response.status_code == 404:
        print("No agents found")
    else:
        print(f"API error: {e}")
except requests.ConnectionError:
    print("Cannot connect to ParkBench API")
```

### Filtering and Ranking

```python
# Advanced agent filtering
candidates = client.negotiation.negotiate(...)['candidateAgents']

# Filter by criteria
filtered = client.negotiation.filter_candidates(
    candidates,
    min_score=0.7,
    requires_negotiation=True,
    min_token_budget=1000
)

# Rank by weighted criteria
ranked = client.negotiation.rank_by_criteria(
    candidates,
    criteria={
        'match_score': 0.5,      # 50% weight
        'negotiation': 0.3,      # 30% weight  
        'token_budget': 0.2      # 20% weight
    }
)
```

## API Reference

### ParkBenchClient

Main client providing access to all functionality.

**Methods:**
- `health_check() -> bool` - Check API health
- `get_api_info() -> dict` - Get API version info

**Properties:**
- `registration` - RegistrationClient instance
- `discovery` - DiscoveryClient instance
- `negotiation` - NegotiationClient instance  
- `sessions` - SessionClient instance

### RegistrationClient

Handles agent registration and lifecycle management.

**Key Methods:**
- `register(agent_name, certificate_pem, metadata)` - Register new agent
- `renew(agent_name, certificate_pem)` - Renew agent registration
- `deactivate(agent_name)` - Deactivate agent
- `get_status(agent_name)` - Get registration status
- `create_metadata_template(...)` - Create metadata template

### DiscoveryClient

Provides agent search and discovery capabilities.

**Key Methods:**
- `search(**filters)` - Search agents with filters
- `get_profile(agent_name)` - Get complete agent profile
- `get_a2a_descriptor(agent_name)` - Get A2A capabilities
- `find_by_skills(skills)` - Find agents by skill list
- `find_a2a_agents(task)` - Find A2A agents for task

### NegotiationClient

Handles A2A task negotiation and agent matching.

**Key Methods:**
- `negotiate(...)` - Find candidate agents for task
- `find_best_match(...)` - Get highest scoring agent
- `filter_candidates(...)` - Filter by criteria
- `rank_by_criteria(...)` - Rank by weighted criteria

### SessionClient

Manages A2A session lifecycle and monitoring.

**Key Methods:**
- `initiate(...)` - Start new A2A session
- `get_status(session_id)` - Get session status
- `update(session_id, status, context)` - Update session
- `complete(session_id, results)` - Mark as completed
- `terminate(session_id)` - Terminate session
- `wait_for_completion(...)` - Wait for completion

## Requirements

- Python 3.8+
- requests >= 2.25.1

Optional:
- cryptography >= 3.4.8 (for certificate validation)

## Development

```bash
git clone https://github.com/parkbench/parkbench.git
cd parkbench/sdk/python
pip install -e .[dev]
```

Run tests:
```bash
pytest
```

## License

MIT License. See LICENSE file for details.

## Support

- Documentation: https://docs.parkbench.dev
- Issues: https://github.com/parkbench/parkbench/issues
- Email: team@parkbench.dev 