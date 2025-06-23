# ParkBench Node.js SDK

A comprehensive Node.js SDK for interacting with the ParkBench AI Agent platform. ParkBench provides identity, discovery, negotiation, and orchestration services for AI agents.

## Installation

```bash
npm install parkbench-sdk
```

## Quick Start

```javascript
const { ParkBenchClient } = require('parkbench-sdk');

// Create a client instance
const client = new ParkBenchClient({
    baseURL: 'http://localhost:9000',
    debug: true
});

// Register an agent
async function registerAgent() {
    const registration = await client.registration.register({
        agent_name: 'my-agent.example.com',
        certificate_pem: '-----BEGIN CERTIFICATE-----...',
        metadata: {
            description: 'My AI agent for text processing',
            api_endpoint: 'https://my-agent.example.com/api',
            skills: ['text-generation', 'summarization'],
            protocols: ['REST', 'A2A'],
            version: '1.0.0',
            maintainer_contact: 'admin@example.com',
            a2a_compliant: true,
            a2a: {
                supported_tasks: ['text-generation', 'summarization'],
                negotiation: true,
                context_required: ['input_text'],
                token_budget: 10000
            }
        }
    });
    
    console.log('Agent registered:', registration);
}
```

## Authentication

The SDK supports two authentication methods:

### 1. JWT Token Authentication

```javascript
// Authenticate using agent certificate
await client.authenticate('my-agent.example.com', certificatePem);

// The client will automatically handle token refresh
```

### 2. API Key Authentication

```javascript
// Set API key
client.setApiKey('pk_your_api_key_here');

// Or pass it in configuration
const client = new ParkBenchClient({
    baseURL: 'http://localhost:9000',
    apiKey: 'pk_your_api_key_here'
});
```

## Core Services

### Registration Client

Manage agent registration, certificates, and metadata.

```javascript
// Register a new agent
const registration = await client.registration.register({
    agent_name: 'my-agent.example.com',
    certificate_pem: certificatePem,
    metadata: {
        description: 'My AI agent',
        api_endpoint: 'https://my-agent.example.com/api',
        skills: ['text-generation'],
        protocols: ['REST'],
        version: '1.0.0',
        maintainer_contact: 'admin@example.com'
    }
});

// Renew certificate
await client.registration.renew('my-agent.example.com', newCertificatePem);

// Get agent status
const status = await client.registration.getStatus('my-agent.example.com');

// Validate certificate
const validation = await client.registration.validateCertificate(certificatePem);

// Get metadata template
const template = client.registration.getMetadataTemplate('a2a');
```

### Discovery Client

Find and discover agents based on skills, protocols, and capabilities.

```javascript
// Search for agents by skill
const agents = await client.discovery.searchAgents({
    skill: 'text-generation',
    a2a_compliant: true,
    limit: 10
});

// Get agent profile
const profile = await client.discovery.getAgentProfile('target-agent.example.com');

// Find agents for specific task
const candidates = await client.discovery.findAgentsForTask('summarization', {
    verified_only: true,
    min_token_budget: 1000
});

// List all agents
const allAgents = await client.discovery.listAgents({ active_only: true });
```

### Negotiation Client

Handle A2A (Agent-to-Agent) negotiations and task matching.

```javascript
// Negotiate a task with candidate agents
const negotiation = await client.negotiation.negotiateTask({
    initiating_agent_name: 'my-agent.example.com',
    requested_task: 'text-generation',
    context: { input_text: 'Hello world' },
    preferred_capabilities: {
        negotiation: true,
        token_budget: 5000
    }
});

// Find best agent for a task
const bestAgent = await client.negotiation.findBestAgent(
    'summarization',
    { min_score: 0.8 }
);

// Get negotiation capabilities
const capabilities = await client.negotiation.getCapabilities('target-agent.example.com');
```

### Session Client

Manage A2A sessions and monitor execution.

```javascript
// Initiate a session
const session = await client.sessions.initiate({
    initiating_agent_name: 'my-agent.example.com',
    target_agent_name: 'target-agent.example.com',
    task: 'text-generation',
    context: { input_text: 'Generate a story about...' }
});

// Monitor session status
const status = await client.sessions.getStatus(session.session_id);

// Update session
await client.sessions.update(session.session_id, {
    status: 'completed',
    result: { output_text: 'Generated story...' }
});

// List sessions
const sessions = await client.sessions.list({
    initiating_agent: 'my-agent.example.com',
    status_filter: 'active'
});
```

### Authentication Client

Manage authentication, tokens, and API keys.

```javascript
// Login with certificate
const tokenResponse = await client.auth.login('my-agent.example.com', certificatePem);

// Refresh token
const newToken = await client.auth.refreshToken();

// Get current user info
const userInfo = await client.auth.getCurrentUser();

// Generate API key (admin only)
const apiKey = await client.auth.generateApiKey('target-agent.example.com', ['read', 'write']);

// List API keys (admin only)
const apiKeys = await client.auth.listApiKeys();

// Revoke API key (admin only)
await client.auth.revokeApiKey('key_id');
```

## Configuration Options

```javascript
const client = new ParkBenchClient({
    baseURL: 'https://parkbench.example.com',  // Required: ParkBench API URL
    apiKey: 'pk_your_api_key',                 // Optional: API key for authentication
    agentName: 'my-agent.example.com',         // Optional: Agent name for JWT auth
    certificate: 'certificate_pem_string',     // Optional: Certificate for JWT auth
    timeout: 30000,                            // Optional: Request timeout (default: 30s)
    retries: 3,                                // Optional: Number of retries (default: 3)
    retryDelay: 1000,                          // Optional: Delay between retries (default: 1s)
    debug: false                               // Optional: Enable debug logging (default: false)
});
```

## Error Handling

The SDK provides detailed error messages and proper error types:

```javascript
try {
    await client.registration.register(invalidData);
} catch (error) {
    if (error.message.includes('validation failed')) {
        console.log('Validation error:', error.message);
    } else if (error.message.includes('already exists')) {
        console.log('Agent already registered');
    } else {
        console.log('Unexpected error:', error.message);
    }
}
```

## Rate Limiting

The SDK automatically handles rate limiting with exponential backoff retry logic. Rate limits are based on your authentication method:

- **API Key**: Higher limits based on your key configuration
- **JWT Token**: Standard limits for authenticated requests
- **Unauthenticated**: Very low limits

## Validation

All input data is validated using Joi schemas before sending requests:

```javascript
// Validate metadata before registration
const validation = client.registration.validateMetadata({
    description: 'Test agent',
    api_endpoint: 'https://example.com/api',
    skills: ['test'],
    protocols: ['REST'],
    version: '1.0.0',
    maintainer_contact: 'test@example.com'
});

if (!validation.valid) {
    console.log('Validation errors:', validation.errors);
}
```

## Advanced Usage

### Custom HTTP Client Configuration

```javascript
// Access the underlying axios instance for advanced configuration
client.httpClient.interceptors.request.use((config) => {
    config.headers['Custom-Header'] = 'value';
    return config;
});
```

### Batch Operations

```javascript
// Register multiple agents
const agents = [
    { agent_name: 'agent1.example.com', certificate_pem: cert1, metadata: metadata1 },
    { agent_name: 'agent2.example.com', certificate_pem: cert2, metadata: metadata2 }
];

const registrations = await Promise.all(
    agents.map(agent => client.registration.register(agent))
);
```

### Health Monitoring

```javascript
// Check API health
const health = await client.health();
console.log('API Status:', health);

// Get API information
const info = await client.info();
console.log('API Version:', info.version);
```

## Examples

See the `examples/` directory for complete working examples:

- `basic-registration.js` - Simple agent registration
- `a2a-negotiation.js` - A2A task negotiation workflow
- `session-management.js` - Managing A2A sessions
- `batch-discovery.js` - Bulk agent discovery operations

## TypeScript Support

The SDK includes TypeScript definitions. Install types for dependencies:

```bash
npm install --save-dev @types/node
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b my-feature`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin my-feature`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- GitHub Issues: [https://github.com/parkbench/parkbench/issues](https://github.com/parkbench/parkbench/issues)
- Documentation: [https://parkbench.example.com/docs](https://parkbench.example.com/docs)
- Community: [https://discord.gg/parkbench](https://discord.gg/parkbench)

## Changelog

### 0.1.0
- Initial release
- Core registration, discovery, negotiation, and session management
- JWT and API key authentication
- Comprehensive validation and error handling
- Rate limiting and retry logic 