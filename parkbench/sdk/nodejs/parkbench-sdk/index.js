/**
 * ParkBench Node.js SDK
 * 
 * A comprehensive SDK for interacting with the ParkBench AI Agent platform.
 * Provides clients for agent registration, discovery, negotiation, and session management.
 * 
 * @author ParkBench Contributors
 * @version 0.1.0
 */

const ParkBenchClient = require('./client');
const RegistrationClient = require('./registration');
const DiscoveryClient = require('./discovery');
const NegotiationClient = require('./negotiation');
const SessionClient = require('./sessions');
const AuthClient = require('./auth');

// Export the main client and individual components
module.exports = {
    // Main unified client
    ParkBenchClient,
    
    // Individual clients
    RegistrationClient,
    DiscoveryClient,
    NegotiationClient,
    SessionClient,
    AuthClient,
    
    // Convenience exports
    createClient: (config) => new ParkBenchClient(config),
    
    // Version
    version: require('./package.json').version
};

// CommonJS compatibility
module.exports.default = module.exports; 