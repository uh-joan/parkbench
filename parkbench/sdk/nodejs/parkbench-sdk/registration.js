/**
 * ParkBench Registration Client
 * 
 * Handles agent registration, certificate management, and registration status operations.
 */

const Joi = require('joi');

// Validation schemas
const agentRegistrationSchema = Joi.object({
    agent_name: Joi.string().min(3).max(253).required(),
    certificate_pem: Joi.string().required(),
    metadata: Joi.object({
        description: Joi.string().max(500).required(),
        api_endpoint: Joi.string().uri().required(),
        skills: Joi.array().items(Joi.string()).min(1).max(50).required(),
        protocols: Joi.array().items(Joi.string().valid('REST', 'GraphQL', 'A2A', 'WebSocket', 'gRPC')).min(1).required(),
        version: Joi.string().pattern(/^\d+\.\d+\.\d+/).required(),
        maintainer_contact: Joi.string().required(),
        a2a_compliant: Joi.boolean().default(false),
        pricing_model: Joi.string().valid('free', 'pay-per-use', 'subscription', 'enterprise', 'custom').optional(),
        a2a: Joi.object({
            supported_tasks: Joi.array().items(Joi.string()).min(1).max(20),
            negotiation: Joi.boolean().default(false),
            context_required: Joi.array().items(Joi.string()).max(10),
            token_budget: Joi.number().integer().min(0).max(1000000)
        }).optional()
    }).required()
});

const certificateRenewalSchema = Joi.object({
    agent_name: Joi.string().required(),
    certificate_pem: Joi.string().required()
});

class RegistrationClient {
    /**
     * Create a registration client
     * 
     * @param {Object} parkbenchClient - Main ParkBench client instance
     */
    constructor(parkbenchClient) {
        this.client = parkbenchClient;
    }
    
    /**
     * Register a new agent
     * 
     * @param {Object} registrationData - Agent registration data
     * @param {string} registrationData.agent_name - Unique agent name (DNS-style)
     * @param {string} registrationData.certificate_pem - Agent certificate in PEM format
     * @param {Object} registrationData.metadata - Agent metadata
     * @returns {Promise<Object>} Registration response
     * @throws {Error} If registration fails
     * 
     * @example
     * const registration = await client.registration.register({
     *   agent_name: 'my-agent.example.com',
     *   certificate_pem: '-----BEGIN CERTIFICATE-----...',
     *   metadata: {
     *     description: 'My AI agent',
     *     api_endpoint: 'https://my-agent.example.com/api',
     *     skills: ['text-generation', 'analysis'],
     *     protocols: ['REST', 'A2A'],
     *     version: '1.0.0',
     *     maintainer_contact: 'admin@example.com',
     *     a2a_compliant: true,
     *     a2a: {
     *       supported_tasks: ['text-generation', 'summarization'],
     *       negotiation: true,
     *       context_required: ['input_text'],
     *       token_budget: 10000
     *     }
     *   }
     * });
     */
    async register(registrationData) {
        // Validate input
        const { error, value } = agentRegistrationSchema.validate(registrationData);
        if (error) {
            throw new Error(`Invalid registration data: ${error.message}`);
        }
        
        try {
            const response = await this.client.request({
                method: 'POST',
                url: '/api/v1/register',
                data: value
            });
            
            return response.data;
        } catch (error) {
            if (error.response) {
                // Handle validation errors from the server
                if (error.response.status === 422) {
                    const detail = error.response.data.detail;
                    if (detail && detail.errors) {
                        throw new Error(`Registration validation failed: ${detail.errors.join(', ')}`);
                    }
                }
                throw new Error(`Registration failed: ${error.response.data.detail || error.response.statusText}`);
            }
            throw new Error(`Registration request failed: ${error.message}`);
        }
    }
    
    /**
     * Renew an agent's certificate
     * 
     * @param {string} agentName - Agent name
     * @param {string} certificatePem - New certificate in PEM format
     * @returns {Promise<Object>} Renewal response
     * @throws {Error} If renewal fails
     * 
     * @example
     * const renewal = await client.registration.renew('my-agent.example.com', newCertificatePem);
     */
    async renew(agentName, certificatePem) {
        // Validate input
        const { error } = certificateRenewalSchema.validate({
            agent_name: agentName,
            certificate_pem: certificatePem
        });
        if (error) {
            throw new Error(`Invalid renewal data: ${error.message}`);
        }
        
        try {
            const response = await this.client.request({
                method: 'POST',
                url: '/api/v1/renew',
                data: {
                    agent_name: agentName,
                    certificate_pem: certificatePem
                }
            });
            
            return response.data;
        } catch (error) {
            if (error.response) {
                throw new Error(`Certificate renewal failed: ${error.response.data.detail || error.response.statusText}`);
            }
            throw new Error(`Certificate renewal request failed: ${error.message}`);
        }
    }
    
    /**
     * Deactivate an agent (requires authentication as the agent or admin)
     * 
     * @param {string} agentName - Agent name to deactivate
     * @returns {Promise<Object>} Deactivation response
     * @throws {Error} If deactivation fails
     * 
     * @example
     * await client.registration.deactivate('my-agent.example.com');
     */
    async deactivate(agentName) {
        if (!agentName || typeof agentName !== 'string') {
            throw new Error('Agent name is required and must be a string');
        }
        
        try {
            const response = await this.client.request({
                method: 'POST',
                url: '/api/v1/deactivate',
                data: { agent_name: agentName }
            });
            
            return response.data;
        } catch (error) {
            if (error.response) {
                throw new Error(`Agent deactivation failed: ${error.response.data.detail || error.response.statusText}`);
            }
            throw new Error(`Agent deactivation request failed: ${error.message}`);
        }
    }
    
    /**
     * Get agent registration status and information
     * 
     * @param {string} agentName - Agent name
     * @returns {Promise<Object>} Agent status information
     * @throws {Error} If status check fails
     * 
     * @example
     * const status = await client.registration.getStatus('my-agent.example.com');
     * console.log('Agent verified:', status.verified);
     * console.log('Agent active:', status.active);
     */
    async getStatus(agentName) {
        if (!agentName || typeof agentName !== 'string') {
            throw new Error('Agent name is required and must be a string');
        }
        
        try {
            const response = await this.client.request({
                method: 'GET',
                url: '/api/v1/status',
                params: { agent_name: agentName }
            });
            
            return response.data;
        } catch (error) {
            if (error.response) {
                throw new Error(`Failed to get agent status: ${error.response.data.detail || error.response.statusText}`);
            }
            throw new Error(`Agent status request failed: ${error.message}`);
        }
    }
    
    /**
     * Validate a certificate without registering
     * 
     * @param {string} certificatePem - Certificate in PEM format
     * @param {string} [agentName] - Optional agent name for validation
     * @returns {Promise<Object>} Certificate validation result
     * @throws {Error} If validation fails
     * 
     * @example
     * const validation = await client.registration.validateCertificate(certificatePem, 'my-agent.example.com');
     * console.log('Certificate valid:', validation.valid);
     * if (!validation.valid) {
     *   console.log('Validation errors:', validation.validation_errors);
     * }
     */
    async validateCertificate(certificatePem, agentName = null) {
        if (!certificatePem || typeof certificatePem !== 'string') {
            throw new Error('Certificate PEM is required and must be a string');
        }
        
        try {
            const requestData = { certificate_pem: certificatePem };
            if (agentName) {
                requestData.agent_name = agentName;
            }
            
            const response = await this.client.request({
                method: 'POST',
                url: '/api/v1/validate-certificate',
                data: requestData
            });
            
            return response.data;
        } catch (error) {
            if (error.response) {
                throw new Error(`Certificate validation failed: ${error.response.data.detail || error.response.statusText}`);
            }
            throw new Error(`Certificate validation request failed: ${error.message}`);
        }
    }
    
    /**
     * Get metadata template for agent registration
     * 
     * @param {string} [agentType='basic'] - Type of agent ('basic', 'a2a', 'enterprise')
     * @returns {Object} Metadata template
     * 
     * @example
     * const template = client.registration.getMetadataTemplate('a2a');
     * console.log('Template:', template);
     */
    getMetadataTemplate(agentType = 'basic') {
        const baseTemplate = {
            description: '',
            api_endpoint: '',
            skills: [],
            protocols: ['REST'],
            version: '1.0.0',
            maintainer_contact: '',
            pricing_model: 'free'
        };
        
        if (agentType === 'a2a' || agentType === 'enterprise') {
            baseTemplate.a2a_compliant = true;
            baseTemplate.protocols.push('A2A');
            baseTemplate.a2a = {
                supported_tasks: [],
                negotiation: false,
                context_required: [],
                token_budget: 0
            };
        }
        
        if (agentType === 'enterprise') {
            baseTemplate.pricing_model = 'enterprise';
            baseTemplate.a2a.negotiation = true;
            baseTemplate.a2a.token_budget = 100000;
        }
        
        return baseTemplate;
    }
    
    /**
     * Update agent metadata (requires authentication as the agent)
     * 
     * @param {string} agentName - Agent name
     * @param {Object} metadata - Updated metadata
     * @returns {Promise<Object>} Update response
     * @throws {Error} If update fails
     * 
     * @example
     * await client.registration.updateMetadata('my-agent.example.com', {
     *   description: 'Updated description',
     *   skills: ['new-skill', 'existing-skill']
     * });
     */
    async updateMetadata(agentName, metadata) {
        if (!agentName || typeof agentName !== 'string') {
            throw new Error('Agent name is required and must be a string');
        }
        
        if (!metadata || typeof metadata !== 'object') {
            throw new Error('Metadata is required and must be an object');
        }
        
        try {
            const response = await this.client.request({
                method: 'PUT',
                url: '/api/v1/update-metadata',
                data: {
                    agent_name: agentName,
                    metadata: metadata
                }
            });
            
            return response.data;
        } catch (error) {
            if (error.response) {
                throw new Error(`Metadata update failed: ${error.response.data.detail || error.response.statusText}`);
            }
            throw new Error(`Metadata update request failed: ${error.message}`);
        }
    }
    
    /**
     * Validate agent metadata without updating
     * 
     * @param {Object} metadata - Metadata to validate
     * @returns {Object} Validation result
     * 
     * @example
     * const validation = client.registration.validateMetadata({
     *   description: 'Test agent',
     *   api_endpoint: 'https://example.com/api',
     *   skills: ['test'],
     *   protocols: ['REST'],
     *   version: '1.0.0',
     *   maintainer_contact: 'test@example.com'
     * });
     */
    validateMetadata(metadata) {
        const metadataSchema = agentRegistrationSchema.extract('metadata');
        const { error, value } = metadataSchema.validate(metadata);
        
        if (error) {
            return {
                valid: false,
                errors: error.details.map(detail => detail.message),
                value: null
            };
        }
        
        return {
            valid: true,
            errors: [],
            value: value
        };
    }
}

module.exports = RegistrationClient;
