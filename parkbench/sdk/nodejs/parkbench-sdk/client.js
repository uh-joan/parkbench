/**
 * ParkBench Main Client
 * 
 * Unified client that provides access to all ParkBench services.
 * Handles authentication, configuration, and provides a consistent interface.
 */

const axios = require('axios');
const Joi = require('joi');
const jwt = require('jsonwebtoken');

const RegistrationClient = require('./registration');
const DiscoveryClient = require('./discovery');
const NegotiationClient = require('./negotiation');
const SessionClient = require('./sessions');
const AuthClient = require('./auth');

// Configuration schema
const configSchema = Joi.object({
    baseURL: Joi.string().uri().required().description('ParkBench API base URL'),
    apiKey: Joi.string().optional().description('API key for authentication'),
    agentName: Joi.string().optional().description('Agent name for JWT authentication'),
    certificate: Joi.string().optional().description('Certificate for authentication'),
    timeout: Joi.number().integer().min(1000).default(30000).description('Request timeout in milliseconds'),
    retries: Joi.number().integer().min(0).default(3).description('Number of retries for failed requests'),
    retryDelay: Joi.number().integer().min(100).default(1000).description('Delay between retries in milliseconds'),
    debug: Joi.boolean().default(false).description('Enable debug logging')
});

class ParkBenchClient {
    /**
     * Create a new ParkBench client
     * 
     * @param {Object} config - Configuration object
     * @param {string} config.baseURL - ParkBench API base URL
     * @param {string} [config.apiKey] - API key for authentication
     * @param {string} [config.agentName] - Agent name for JWT authentication
     * @param {string} [config.certificate] - Certificate for authentication
     * @param {number} [config.timeout=30000] - Request timeout in milliseconds
     * @param {number} [config.retries=3] - Number of retries for failed requests
     * @param {number} [config.retryDelay=1000] - Delay between retries in milliseconds
     * @param {boolean} [config.debug=false] - Enable debug logging
     */
    constructor(config) {
        // Validate configuration
        const { error, value } = configSchema.validate(config);
        if (error) {
            throw new Error(`Invalid configuration: ${error.message}`);
        }
        
        this.config = value;
        this.accessToken = null;
        this.tokenExpiration = null;
        
        // Create axios instance with base configuration
        this.httpClient = axios.create({
            baseURL: this.config.baseURL,
            timeout: this.config.timeout,
            headers: {
                'Content-Type': 'application/json',
                'User-Agent': `ParkBench-NodeJS-SDK/0.1.0`
            }
        });
        
        // Add request interceptor for authentication
        this.httpClient.interceptors.request.use(
            this._addAuthenticationHeaders.bind(this),
            (error) => Promise.reject(error)
        );
        
        // Add response interceptor for error handling and retries
        this.httpClient.interceptors.response.use(
            (response) => response,
            this._handleResponseError.bind(this)
        );
        
        // Initialize service clients
        this.registration = new RegistrationClient(this);
        this.discovery = new DiscoveryClient(this);
        this.negotiation = new NegotiationClient(this);
        this.sessions = new SessionClient(this);
        this.auth = new AuthClient(this);
        
        this._debug('ParkBenchClient initialized', { baseURL: this.config.baseURL });
    }
    
    /**
     * Authenticate using agent credentials
     * 
     * @param {string} agentName - Agent name
     * @param {string} certificate - Agent certificate
     * @returns {Promise<Object>} Authentication response
     */
    async authenticate(agentName, certificate) {
        try {
            const response = await this.auth.login(agentName, certificate);
            
            this.accessToken = response.access_token;
            this.tokenExpiration = new Date(Date.now() + (response.expires_in * 1000));
            
            this._debug('Authentication successful', { agentName, expiresAt: this.tokenExpiration });
            
            return response;
        } catch (error) {
            this._debug('Authentication failed', { agentName, error: error.message });
            throw error;
        }
    }
    
    /**
     * Set API key for authentication
     * 
     * @param {string} apiKey - API key
     */
    setApiKey(apiKey) {
        this.config.apiKey = apiKey;
        this._debug('API key set');
    }
    
    /**
     * Check if the client is authenticated
     * 
     * @returns {boolean} True if authenticated
     */
    isAuthenticated() {
        if (this.config.apiKey) {
            return true;
        }
        
        if (this.accessToken && this.tokenExpiration) {
            return new Date() < this.tokenExpiration;
        }
        
        return false;
    }
    
    /**
     * Get current authentication status
     * 
     * @returns {Object} Authentication status information
     */
    getAuthStatus() {
        return {
            authenticated: this.isAuthenticated(),
            authType: this.config.apiKey ? 'api_key' : 'jwt',
            tokenExpiration: this.tokenExpiration,
            agentName: this.config.agentName
        };
    }
    
    /**
     * Refresh JWT token if needed
     * 
     * @returns {Promise<boolean>} True if token was refreshed
     */
    async refreshTokenIfNeeded() {
        if (!this.accessToken || !this.tokenExpiration) {
            return false;
        }
        
        // Refresh if token expires in less than 5 minutes
        const fiveMinutesFromNow = new Date(Date.now() + 5 * 60 * 1000);
        if (this.tokenExpiration < fiveMinutesFromNow) {
            try {
                const response = await this.auth.refreshToken();
                this.accessToken = response.access_token;
                this.tokenExpiration = new Date(Date.now() + (response.expires_in * 1000));
                
                this._debug('Token refreshed', { expiresAt: this.tokenExpiration });
                return true;
            } catch (error) {
                this._debug('Token refresh failed', { error: error.message });
                this.accessToken = null;
                this.tokenExpiration = null;
                return false;
            }
        }
        
        return false;
    }
    
    /**
     * Make an HTTP request with automatic authentication and retry logic
     * 
     * @param {Object} requestConfig - Axios request configuration
     * @returns {Promise<Object>} Response data
     */
    async request(requestConfig) {
        return this.httpClient(requestConfig);
    }
    
    /**
     * Add authentication headers to requests
     * 
     * @private
     */
    async _addAuthenticationHeaders(config) {
        // Skip auth for login endpoint
        if (config.url && config.url.includes('/auth/login')) {
            return config;
        }
        
        // Try to refresh token if needed
        await this.refreshTokenIfNeeded();
        
        // Add authentication header
        if (this.config.apiKey) {
            config.headers.Authorization = `Bearer ${this.config.apiKey}`;
        } else if (this.accessToken) {
            config.headers.Authorization = `Bearer ${this.accessToken}`;
        }
        
        return config;
    }
    
    /**
     * Handle response errors with retry logic
     * 
     * @private
     */
    async _handleResponseError(error) {
        if (!error.config || error.config.__retryCount >= this.config.retries) {
            throw error;
        }
        
        error.config.__retryCount = error.config.__retryCount || 0;
        error.config.__retryCount++;
        
        // Retry on network errors or 5xx status codes
        if (!error.response || error.response.status >= 500) {
            await this._delay(this.config.retryDelay * error.config.__retryCount);
            
            this._debug('Retrying request', { 
                attempt: error.config.__retryCount,
                url: error.config.url 
            });
            
            return this.httpClient(error.config);
        }
        
        // Handle 401 errors by trying to refresh token
        if (error.response && error.response.status === 401 && this.accessToken) {
            const refreshed = await this.refreshTokenIfNeeded();
            if (refreshed) {
                return this.httpClient(error.config);
            }
        }
        
        throw error;
    }
    
    /**
     * Delay execution for the specified number of milliseconds
     * 
     * @private
     * @param {number} ms - Milliseconds to delay
     */
    _delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    /**
     * Debug logging
     * 
     * @private
     */
    _debug(message, data = {}) {
        if (this.config.debug) {
            console.log(`[ParkBench SDK] ${message}`, data);
        }
    }
    
    /**
     * Get health status of the ParkBench API
     * 
     * @returns {Promise<Object>} Health status
     */
    async health() {
        try {
            const response = await this.httpClient.get('/health');
            return response.data;
        } catch (error) {
            throw new Error(`Health check failed: ${error.message}`);
        }
    }
    
    /**
     * Get API information
     * 
     * @returns {Promise<Object>} API information
     */
    async info() {
        try {
            const response = await this.httpClient.get('/');
            return response.data;
        } catch (error) {
            throw new Error(`Failed to get API info: ${error.message}`);
        }
    }
}

module.exports = ParkBenchClient; 