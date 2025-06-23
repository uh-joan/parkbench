# ParkBench Backend

FastAPI-based backend for the ParkBench AI agent identity, discovery, negotiation, and orchestration platform.

## Quick Start

### Option 1: Docker Compose (Recommended)

1. **Start all services**:
   ```bash
   cd ../deployment
   docker-compose up --build
   ```

2. **Access the services**:
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Database Admin (optional): `docker-compose --profile admin up`
   - PgAdmin: http://localhost:5050 (admin@parkbench.dev / admin)

### Option 2: Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start PostgreSQL** (using Docker):
   ```bash
   docker run --name parkbench-db \
     -e POSTGRES_USER=parkbenchuser \
     -e POSTGRES_PASSWORD=parkbenchpassword \
     -e POSTGRES_DB=parkbenchdb \
     -p 5432:5432 \
     -d postgres:15
   ```

3. **Set environment variables**:
   ```bash
   export DATABASE_URL="postgresql://parkbenchuser:parkbenchpassword@localhost:5432/parkbenchdb"
   export API_DEBUG="true"
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

## Testing

### Run the test suite:
```bash
# Make sure the API is running first
python test_api.py
```

### Manual API testing:
Visit http://localhost:8000/docs for the interactive API documentation.

## API Endpoints

### Core Registration & Discovery
- `POST /api/v1/register` - Register a new agent
- `GET /api/v1/agents/search` - Search for agents
- `GET /api/v1/agents/{agentName}` - Get agent profile
- `GET /api/v1/agents/{agentName}/a2a` - Get A2A descriptors
- `GET /api/v1/status` - Get agent status

### A2A Negotiation & Sessions
- `POST /api/v1/a2a/negotiate` - Negotiate tasks with candidate agents
- `POST /api/v1/a2a/session/initiate` - Initiate A2A session
- `GET /api/v1/a2a/session/{sessionID}/status` - Get session status
- `PUT /api/v1/a2a/session/{sessionID}` - Update session
- `GET /api/v1/a2a/sessions` - List sessions

### Health & Info
- `GET /health` - Health check
- `GET /` - API information

## Example Agent Registration

```json
{
  "agentName": "translator-b.agents.example.com",
  "certificatePEM": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
  "metadata": {
    "description": "Language translation agent",
    "version": "1.0.0",
    "maintainer_contact": "dev@example.com",
    "api_endpoint": "https://translator-b.example.com/api",
    "protocols": ["REST", "A2A"],
    "a2a_compliant": true,
    "skills": ["translation", "language-detection"],
    "input_formats": ["JSON", "text"],
    "output_formats": ["JSON"],
    "pricing_model": "pay-per-use",
    "public_key": "ssh-rsa AAAAB3...",
    "a2a": {
      "supported_tasks": ["translate", "detect-language"],
      "negotiation": true,
      "context_required": ["source_language", "target_language"],
      "token_budget": 5000
    }
  }
}
```

## Database Schema

### Agents Table
- `agent_id` (UUID, PK)
- `agent_name` (VARCHAR, UNIQUE)
- `certificate_pem` (TEXT)
- `metadata` (JSONB)
- `verified` (BOOLEAN)
- `active` (BOOLEAN)
- `created_at`, `updated_at` (TIMESTAMP)

### A2A Sessions Table
- `session_id` (UUID, PK)
- `initiating_agent`, `target_agent` (VARCHAR)
- `task` (VARCHAR)
- `session_token` (TEXT)
- `status` (ENUM: active, completed, failed)
- `context` (JSONB)
- `created_at`, `updated_at` (TIMESTAMP)

## Configuration

Environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `API_DEBUG` - Enable debug mode (true/false)
- `DATABASE_ECHO` - Enable SQL query logging (true/false)
- `SECRET_KEY` - JWT signing key
- `VERIFY_CERTIFICATES` - Enable certificate validation (true/false)

## Development

### Adding new endpoints:
1. Create/modify routers in `api/`
2. Add database models to `db/models.py`
3. Update tests in `test_api.py`

### Database migrations:
```bash
# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

## Architecture

```
backend/
├── api/           # FastAPI routers
├── db/            # Database models and connections
├── config/        # Application configuration
├── schemas/       # JSON schemas for validation
├── main.py        # Application entry point
└── test_api.py    # API validation tests
```

The backend implements the ParkBench specification with:
- **Phase 1**: Agent registration and discovery
- **Phase 2**: A2A negotiation and session management
- **Phase 3**: Ready for SDK integration

## Next Steps

1. **Certificate Validation**: Implement X.509 certificate verification
2. **Authentication**: Add JWT-based API authentication
3. **Monitoring**: Add logging and metrics collection
4. **Rate Limiting**: Implement API rate limiting
5. **SDK Development**: Build Python and Node.js SDKs 