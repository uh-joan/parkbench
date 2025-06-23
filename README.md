# ParkBench MVP - Phase 1 Technical Specification (Agent-Executable Version)

## Project Overview

**Project Name**: ParkBench

**Objective**: Build the core foundation for an open, vendor-neutral AI Agent Discovery and Directory platform. Phase 1 includes the full backend and frontend functionality needed for agent registration, discovery, identity verification, and storage of capability descriptors (including A2A compatibility).

---

# Core Components

The following components will be implemented in Phase 1:

1. **Agent Registration System (Web UI & API)**
2. **Discovery API**
3. **Agent Metadata & Capability Schema**
4. **Identity Verification System**
5. **Agent Trust Signals (Basic Reputation Layer)**
6. **Web Frontend Portal**
7. **Administrative Dashboard**
8. **Early A2A Descriptor Compatibility**

---

# Detailed Functional Requirements

## 1. Agent Registration System

### Functionality

- Allow agents (developers) to register agents via:
  - Web UI form
  - REST API endpoint
- Validate and store registration data.
- Issue unique `agent_id` (UUID).

### API Specification (OpenAPI Format)

#### Endpoint: `POST /agents/register`

- **Request Body:**

```json
{
  "name": "string",
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
  "public_key": "string"
}
```

- **Response (201 Created):**

```json
{
  "agent_id": "UUID",
  "status": "registered"
}
```

- **Error Codes:**
  - `400`: Invalid request body
  - `409`: Agent already exists
  - `500`: Internal server error

### Data Validation

- Validate mandatory fields
- Validate URL format for `api_endpoint`
- Validate allowed values for `protocols` and `skills`

### Database Tables

#### `agents`

| Field               | Type         |
| ------------------- | ------------ |
| agent\_id           | UUID (PK)    |
| name                | VARCHAR(255) |
| description         | TEXT         |
| version             | VARCHAR(20)  |
| maintainer\_contact | VARCHAR(255) |
| api\_endpoint       | VARCHAR(255) |
| protocols           | JSONB        |
| a2a\_compliant      | BOOLEAN      |
| skills              | JSONB        |
| input\_formats      | JSONB        |
| output\_formats     | JSONB        |
| pricing\_model      | VARCHAR(255) |
| public\_key         | TEXT         |
| verified            | BOOLEAN      |
| created\_at         | TIMESTAMP    |
| updated\_at         | TIMESTAMP    |

---

## 2. Discovery API

### Functionality

- Expose REST API endpoints allowing:
  - Agent search by capability, protocol, verified status, domain, input/output formats
  - Return structured agent profiles in JSON

### API Endpoints

#### `GET /agents/{agent_id}`

- Returns full agent profile by ID.

#### `GET /agents/search`

- Query Parameters:
  - `skill`
  - `protocol`
  - `verified` (boolean)
  - `a2a_compliant` (boolean)
- Response:

```json
{
  "results": [
    {
      "agent_id": "UUID",
      "name": "string",
      "skills": ["string"],
      "protocols": ["string"],
      "verified": true
    }
  ]
}
```

#### `GET /agents/protocols/{protocol_type}`

#### `GET /agents/skills/{skill_name}`

---

## 3. Agent Metadata & Capability Schema

- JSON Schema v1 (see above structure)
- Stored as JSONB inside PostgreSQL for flexibility
- Indexed via ElasticSearch for full-text search performance

---

## 4. Identity Verification System

### Verification Methods

#### a) Email Verification Flow

- User provides email at registration
- Backend sends signed magic link email
- Clicking link activates `email_verified`
- API: `POST /verify/email` with token

#### b) Domain Ownership

- Backend generates TXT token for domain
- User adds TXT record to DNS
- Verification API queries DNS to validate TXT
- API: `POST /verify/domain`

#### Verification States

- `unverified`
- `email_verified`
- `domain_verified`
- `fully_verified` (both email + domain verified)

### Database Tables

#### `verifications`

| Field            | Type         |
| ---------------- | ------------ |
| verification\_id | UUID (PK)    |
| agent\_id        | UUID (FK)    |
| email\_token     | VARCHAR(255) |
| domain\_token    | VARCHAR(255) |
| email\_verified  | BOOLEAN      |
| domain\_verified | BOOLEAN      |
| fully\_verified  | BOOLEAN      |
| created\_at      | TIMESTAMP    |
| updated\_at      | TIMESTAMP    |

---

## 5. Agent Trust Signals (Basic Reputation Layer)

- Display verification status on profiles
- Placeholder for future rating/reputation mechanisms

---

## 6. Web Frontend Portal

### Features

- Public browse/search page
- Filter by:
  - Skills
  - Protocols
  - Verification status
  - A2A compliance
- View agent profile pages

### UI Design Components

- Search bar (ElasticSearch backend)
- Filter panel (checkboxes)
- Results list (name, skill, protocols, verification)
- Agent detail page (full profile)
- Admin panel (moderation interface)

### Stack

- Frontend: React.js with TailwindCSS
- Deployment: AWS (Vercel optional for frontend)

---

## 7. Administrative Dashboard

### Admin Features

- Login (OAuth-protected)
- View new registrations
- Approve / reject agents
- Manually edit agent metadata
- View system logs (ElasticSearch + Prometheus monitoring)
- Manage verification state overrides

---

## 8. Early A2A Descriptor Compatibility

### Minimum A2A v0.1 Support

- Store and expose Anthropic A2A descriptors for registered agents
- Extend metadata schema with:

```json
{
  "a2a": {
    "supported_tasks": ["string"],
    "negotiation": true,
    "context_required": ["string"],
    "token_budget": integer
  }
}
```

- Expose via API: `GET /agents/{agent_id}/a2a`

---

# Non-Functional Requirements

| Category      | Requirement                                    |
| ------------- | ---------------------------------------------- |
| Scalability   | System should support 10K+ registered agents   |
| Performance   | API search latency < 500ms                     |
| Security      | OAuth2, secure API keys for agent registration |
| Privacy       | GDPR-compliant data storage                    |
| Documentation | Public API Docs via OpenAPI (Swagger)          |

---

# Deployment / CI/CD

| Tool       | Usage                                      |
| ---------- | ------------------------------------------ |
| GitHub     | Code repository                            |
| Docker     | Containerized deployment                   |
| Kubernetes | Cloud-neutral deployment (optional for V1) |
| CI/CD      | GitHub Actions                             |
| Monitoring | Prometheus + Grafana                       |

---

# Testing & Validation

### Automated Tests

- Unit tests for all API endpoints
- Integration tests (registration, search, verification flows)
- Load tests for search scalability

### Test Data

- Generate sample agents for test environment (1000 synthetic records)
- Use mock verification providers

---

# Deliverables Summary (Phase 1 Complete System)

1. Fully functioning **Agent Registration Portal (UI & API)**
2. Publicly available **Discovery API** with full search capability
3. **Metadata Schema v1** published
4. **Early A2A Descriptor Support** implemented and testable
5. Fully functional **Verification System** (email + domain)
6. Publicly browsable **Web Frontend Portal**
7. Fully operational **Admin Dashboard**
8. Complete automated test suite deployed

---

# Target Timeline

| Phase                                  | Duration  |
| -------------------------------------- | --------- |
| Phase 0 - Design & Standards Alignment | Month 1–2 |
| Phase 1 - Core Build                   | Month 3–6 |
| Phase 2 - Developer Integrations       | Month 6+  |

---

# External Dependencies

- Public A2A spec from Anthropic (track v0.1–v0.2 changes)
- Community taxonomy evolution (for skills/capabilities)
- Partnership discussions with LangChain, SuperAGI, CrewAI

---

# Execution Sprint Plan

## Sprint 0 — Project Bootstrap (Weeks 1-2)

- Finalize metadata schema
- Set up GitHub repo, cloud infra, Docker, Kubernetes, CI/CD pipelines
- Deploy PostgreSQL, ElasticSearch, Prometheus & Grafana

## Sprint 1 — Core Backend Foundations (Weeks 3-4)

- Agents table, registration API, OpenAPI spec, UUID logic, backend logs
- Unit tests for registration

## Sprint 2 — Identity Verification (Weeks 5-6)

- Email verification flow
- Domain DNS verification flow
- Verification API endpoints
- Full integration tests

## Sprint 3 — Discovery API (Weeks 7-8)

- ElasticSearch index
- Search API & filters
- Agent profile lookup API
- Load testing search scalability

## Sprint 4 — Frontend Build (Weeks 9-10)

- React frontend with search, filters, profile pages
- Admin portal base UI
- Error handling states

## Sprint 5 — A2A Descriptor Support (Weeks 11-12)

- A2A descriptor schema extension
- A2A metadata storage & API exposure
- A2A schema validation engine

## Sprint 6 — Admin Tools (Weeks 13-14)

- Admin approval workflows
- Logs dashboard
- Verification override controls

## Sprint 7 — Final Testing & Deployment (Weeks 15-16)

- Full end-to-end integration tests
- Security tests, GDPR compliance, backup setup
- Soft launch cluster deployment
- Synthetic agent stress testing (1000 agents)

---

# Mission Reminder

> ParkBench Phase 1 creates the open, neutral, vendor-agnostic discovery backbone that allows any AI agent to find and interact with any other agent across ecosystems.

---

**End of Agent-Executable README for Phase 1 Implementation**

