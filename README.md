
# ParkBench MVP - Unified Specification (Phases 1-3)

## Objective

Provide a complete, unified specification for ParkBench: an open, vendor-neutral AI agent identity, discovery, negotiation, and orchestration platform. This specification includes:
- Agent Name Service (ANS) identity layer
- Agent Registration & Discovery (Phase 1)
- Active A2A Broker & Negotiation (Phase 2)
- Developer SDK & LangChain integration (Phase 3)

# Phase 0: Standards Alignment

- Adopt ANS schema (DNS-style agent names)
- Certificate-based agent identity (X.509 signed by trusted CAs)
- JSON Schema-based capability and metadata definitions
- Taxonomy standards for skills, protocols, and capabilities

# Phase 1: Core MVP Build - Agent Registration & Discovery

## Agent Registration System

### Registration API

**Endpoint:** `POST /register`

#### Request Body
```json
{
  "agentName": "translator-b.agents.example.com",
  "certificatePEM": "string",
  "metadata": {
    "description": "string",
    "version": "string",
    "maintainer_contact": "string",
    "api_endpoint": "string",
    "protocols": ["REST", "GraphQL", "A2A"],
    "a2a_compliant": true,
    "skills": ["travel-booking", "pharma-ci", "market-research"],
    "input_formats": ["JSON", "CSV"],
    "output_formats": ["JSON"],
    "pricing_model": "string",
    "public_key": "string",
    "a2a": {
      "supported_tasks": ["string"],
      "negotiation": true,
      "context_required": ["string"],
      "token_budget": 3000
    }
  }
}
```

#### Response
```json
{
  "agent_id": "UUID",
  "agentName": "translator-b.agents.example.com",
  "status": "registered"
}
```

### Renewal API
**Endpoint:** `POST /renew`

### Deactivation API
**Endpoint:** `POST /deactivate`

### Status API
**Endpoint:** `GET /status?agentName=...`

## Discovery API

### Search Agents
**Endpoint:** `GET /agents/search`

**Query Parameters:**
- `skill`
- `protocol`
- `a2a_compliant`
- `verified`
- `active`

### Get Agent Profile
**Endpoint:** `GET /agents/{agentName}`

### Get A2A Descriptors
**Endpoint:** `GET /agents/{agentName}/a2a`

## Database Tables

### `agents`
| Field | Type |
|---|---|
| agent_id | UUID (PK) |
| agentName | VARCHAR(255) UNIQUE |
| certificatePEM | TEXT |
| metadata | JSONB |
| verified | BOOLEAN |
| active | BOOLEAN |
| created_at | TIMESTAMP |
| updated_at | TIMESTAMP |

# Phase 2: Active A2A Broker

## A2A Session Broker API

### Negotiate Task
**Endpoint:** `POST /a2a/negotiate`

#### Request Body
```json
{
  "initiatingAgentName": "string",
  "requestedTask": "string",
  "context": { "key": "value" },
  "preferredCapabilities": { "negotiation": true, "token_budget": 3000 }
}
```

#### Response
```json
{
  "candidateAgents": [
    {
      "agentName": "string",
      "matchScore": 0.95,
      "supportedTasks": ["string"],
      "negotiation": true,
      "token_budget": 3000
    }
  ]
}
```

### Initiate A2A Session
**Endpoint:** `POST /a2a/session/initiate`

### Session Status
**Endpoint:** `GET /a2a/session/{sessionID}/status`

## A2A Session Identity

- Signed ParkBench-issued session tokens
- Tokens contain:
  - Session ID
  - Initiating agent
  - Target agent
  - Agreed task & context
  - Expiration timestamp

## A2A Negotiation Format

Align fully with Anthropic’s A2A protocol envelope structure:
```json
{
  "type": "a2a/negotiation_request",
  "from": "agentA.agents.example.com",
  "to": "agentB.agents.example.com",
  "context": { "key": "value" },
  "supported_tasks": ["book_hotel"],
  "capability_descriptor": { ... },
  "signature": "signed_by_initiator"
}
```

## A2A Session Table

### `a2a_sessions`
| Field | Type |
|---|---|
| session_id | UUID (PK) |
| initiating_agent | VARCHAR(255) |
| target_agent | VARCHAR(255) |
| task | VARCHAR(255) |
| session_token | TEXT |
| status | ENUM (active, completed, failed) |
| created_at | TIMESTAMP |
| updated_at | TIMESTAMP |

# Phase 3: Developer SDK & LangChain Integration

## SDK Languages
- Python (primary — LangChain)
- Node.js

## SDK Modules

### Agent Registration Client
```python
register_agent(metadata, certificate_pem)
```

### Discovery Client
```python
search_agents(skill=None, protocol=None, a2a_compliant=None, verified=None)
get_agent_profile(agent_name)
```

### A2A Negotiation Client
```python
negotiate_task(initiating_agent_name, requested_task, context, preferred_capabilities)
initiate_a2a_session(target_agent_name, context, task)
```

### A2A Session Handler
```python
start_a2a_session(session_token)
exchange_a2a_messages(session_id, message_envelope)
```

## LangChain Toolkit

```python
from parkbench_sdk import ParkBenchTool

pb = ParkBenchTool(api_key="...")
candidate_agents = pb.find_agents_for_task("pharma-competitive-intelligence")
session = pb.initiate_a2a_workflow("agentA", candidate_agents[0], context)
```

## SDK Deliverables
- Python SDK (PyPI)
- Node.js SDK (NPM)
- Public API Docs (Swagger + SDK)
- LangChain plugin repo
- Open-source examples

# Complete Roadmap Summary

**Phase 0 (Standards Alignment):** ANS + A2A schema adoption

**Phase 1 (Core MVP Build):** Registration system, Discovery API, Web Portal

**Phase 2 (Active A2A Broker):** Negotiation APIs, Real-time sessions, Multi-agent workflows

**Phase 3 (Developer SDK):** SDK toolkits, LangChain integration

# Vision Statement

> ParkBench becomes the open, vendor-neutral Agent Identity, Discovery, Negotiation, and Orchestration Backbone — providing both human and machine discoverability, trusted identity verification, and fully autonomous multi-agent interoperability across any platform.

# Initial Repo Scaffolding Structure

```bash
parkbench/
│
├── backend/
│   ├── api/
│   │   ├── registration.py
│   │   ├── discovery.py
│   │   ├── negotiation.py
│   │   ├── sessions.py
│   │   └── schemas/
│   │       ├── agent_registration.json
│   │       ├── a2a_descriptor.json
│   │       └── a2a_negotiation.json
│   ├── db/
│   │   └── models.py
│   ├── config/
│   │   └── settings.py
│   └── main.py
│
├── frontend/
│   ├── components/
│   ├── pages/
│   └── public/
│
├── sdk/
│   ├── python/
│   │   └── parkbench_sdk/
│   │       ├── registration.py
│   │       ├── discovery.py
│   │       ├── negotiation.py
│   │       └── sessions.py
│   └── nodejs/
│       └── parkbench-sdk/
│           ├── registration.js
│           ├── discovery.js
│           ├── negotiation.js
│           └── sessions.js
│
├── tests/
│
├── docs/
│   └── openapi.yaml
│
└── deployment/
    ├── docker-compose.yml
    ├── k8s/
    └── ci-cd/
```

**End of Unified Agent-Executable README (Phases 0-3)**
