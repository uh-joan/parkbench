/**
 * ParkBench Authentication Client
 * 
 * Handles authentication, token management, and API key operations.
 */

const Joi = require('joi');

// Validation schemas
const loginSchema = Joi.object({
    agent_name: Joi.string().required(),
    certificate_pem: Joi.string().required()
});

const apiKeyRequestSchema = Joi.object({
    agent_name: Joi.string().required(),
    permissions: Joi.array().items(Joi.string()).default(['read', 'write']),
    expires_hours: Joi.number().integer().min(1).optional()
});

class AuthClient {
    /**
     * Create an authentication client
     * 
     * @param {Object} parkbenchClient - Main ParkBench client instance
     */
    constructor(parkbenchClient) {
        this.client = parkbenchClient;
    }
    
    /**
     * Authenticate an agent and get JWT token
     * 
     * @param {string} agentName - Agent name
     * @param {string} certificatePem - Agent certificate in PEM format
     * @returns {Promise<Object>} Authentication response with token
     * @throws {Error} If authentication fails
     * 
     * @example
     * const response = await client.auth.login('my-agent.example.com', certificatePem);
     * console.log('Access token:', response.access_token);
     */
    async login(agentName, certificatePem) {
        // Validate input
        const { error } = loginSchema.validate({ 
            agent_name: agentName, 
            certificate_pem: certificatePem 
        });
        if (error) {
            throw new Error(`Invalid login parameters: ${error.message}`);
        }
        
        try {
            const response = await this.client.request({
                method: 'POST',
                url: '/api/v1/auth/login',
                data: {
                    agent_name: agentName,
                    certificate_pem: certificatePem
                }
            });
            
            return response.data;
        } catch (error) {
            if (error.response) {
                throw new Error(`Authentication failed: ${error.response.data.detail || error.response.statusText}`);
            }
            throw new Error(`Authentication request failed: ${error.message}`);
        }
    }
    
    /**
     * Refresh JWT token
     * 
     * @returns {Promise<Object>} New token response
     * @throws {Error} If token refresh fails
     * 
     * @example
     * const newToken = await client.auth.refreshToken();
     */
    async refreshToken() {
        try {
            const response = await this.client.request({
                method: 'POST',
                url: '/api/v1/auth/refresh'
            });
            
            return response.data;
        } catch (error) {
            if (error.response) {
                throw new Error(`Token refresh failed: ${error.response.data.detail || error.response.statusText}`);
            }
            throw new Error(`Token refresh request failed: ${error.message}`);
        }
    }
    
    /**
     * Get current user information
     * 
     * @returns {Promise<Object>} Current user information
     * @throws {Error} If request fails
     * 
     * @example
     * const userInfo = await client.auth.getCurrentUser();
     * console.log('Current agent:', userInfo.agent_name);
     */
    async getCurrentUser() {
        try {
            const response = await this.client.request({
                method: 'GET',
                url: '/api/v1/auth/me'
            });
            
            return response.data;
        } catch (error) {
            if (error.response) {
                throw new Error(`Failed to get user info: ${error.response.data.detail || error.response.statusText}`);
            }
            throw new Error(`User info request failed: ${error.message}`);
        }
    }
    
    /**
     * Generate a new API key for an agent (requires admin permission)
     * 
     * @param {string} agentName - Agent name to generate key for
     * @param {Array<string>} [permissions=['read', 'write']] - Permissions for the API key
     * @param {number} [expiresHours] - Expiration time in hours
     * @returns {Promise<Object>} API key response
     * @throws {Error} If API key generation fails
     * 
     * @example
     * const apiKey = await client.auth.generateApiKey('agent.example.com', ['read', 'write'], 168);
     * console.log('API Key:', apiKey.api_key);
     */
    async generateApiKey(agentName, permissions = ['read', 'write'], expiresHours = null) {
        // Validate input
        const { error } = apiKeyRequestSchema.validate({
            agent_name: agentName,
            permissions,
            expires_hours: expiresHours
        });
        if (error) {
            throw new Error(`Invalid API key parameters: ${error.message}`);
        }
        
        try {
            const requestData = {
                agent_name: agentName,
                permissions
            };
            
            if (expiresHours !== null) {
                requestData.expires_hours = expiresHours;
            }
            
            const response = await this.client.request({
                method: 'POST',
                url: '/api/v1/auth/api-key',
                data: requestData
            });
            
            return response.data;
        } catch (error) {
            if (error.response) {
                throw new Error(`API key generation failed: ${error.response.data.detail || error.response.statusText}`);
            }
            throw new Error(`API key generation request failed: ${error.message}`);
        }
    }
    
    /**
     * List all API keys (requires admin permission)
     * 
     * @returns {Promise<Object>} List of API keys
     * @throws {Error} If request fails
     * 
     * @example
     * const apiKeys = await client.auth.listApiKeys();
     * console.log('Total API keys:', apiKeys.total);
     */
    async listApiKeys() {
        try {
            const response = await this.client.request({
                method: 'GET',
                url: '/api/v1/auth/api-keys'
            });
            
            return response.data;
        } catch (error) {
            if (error.response) {
                throw new Error(`Failed to list API keys: ${error.response.data.detail || error.response.statusText}`);
            }
            throw new Error(`API key list request failed: ${error.message}`);
        }
    }
    
    /**
     * Revoke an API key (requires admin permission)
     * 
     * @param {string} keyId - API key ID to revoke
     * @returns {Promise<Object>} Revocation response
     * @throws {Error} If revocation fails
     * 
     * @example
     * await client.auth.revokeApiKey('abc123');
     */
    async revokeApiKey(keyId) {
        if (!keyId || typeof keyId !== 'string') {
            throw new Error('Key ID is required and must be a string');
        }
        
        try {
            const response = await this.client.request({
                method: 'DELETE',
                url: `/api/v1/auth/api-keys/${keyId}`
            });
            
            return response.data;
        } catch (error) {
            if (error.response) {
                throw new Error(`Failed to revoke API key: ${error.response.data.detail || error.response.statusText}`);
            }
            throw new Error(`API key revocation request failed: ${error.message}`);
        }
    }
    
    /**
     * Get available permissions in the system
     * 
     * @returns {Promise<Object>} Available permissions
     * @throws {Error} If request fails
     * 
     * @example
     * const permissions = await client.auth.getPermissions();
     * permissions.permissions.forEach(p => {
     *     console.log(`${p.name}: ${p.description}`);
     * });
     */
    async getPermissions() {
        try {
            const response = await this.client.request({
                method: 'GET',
                url: '/api/v1/auth/permissions'
            });
            
            return response.data;
        } catch (error) {
            if (error.response) {
                throw new Error(`Failed to get permissions: ${error.response.data.detail || error.response.statusText}`);
            }
            throw new Error(`Permissions request failed: ${error.message}`);
        }
    }
    
    /**
     * Validate authentication status
     * 
     * @returns {Promise<Object>} Authentication validation result
     * @throws {Error} If validation fails
     * 
     * @example
     * const isValid = await client.auth.validateAuth();
     * if (isValid.authenticated) {
     *     console.log('Authentication is valid');
     * }
     */
    async validateAuth() {
        try {
            const userInfo = await this.getCurrentUser();
            return {
                authenticated: true,
                agent_name: userInfo.agent_name,
                permissions: userInfo.permissions,
                auth_type: userInfo.auth_type
            };
        } catch (error) {
            return {
                authenticated: false,
                error: error.message
            };
        }
    }
}

module.exports = AuthClient; 