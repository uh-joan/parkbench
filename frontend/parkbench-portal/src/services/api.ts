import axios, { AxiosInstance } from 'axios';
import {
  Agent,
  SearchFilters,
  A2ASession,
  NegotiationRequest,
  NegotiationResponse,
  RegistrationRequest,
  RegistrationResponse,
  ApiResponse
} from '../types';

interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  agent_name: string;
}

interface User {
  agent_name: string;
  agent_id: string;
  permissions: string[];
  auth_type: string;
  rate_limit: number;
}

class ParkBenchAPI {
  private client: AxiosInstance;

  constructor(baseURL: string = 'https://parkbench-backend-production.up.railway.app') {
    this.client = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // Authentication methods
  setAuthToken(token: string | null): void {
    if (token) {
      this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete this.client.defaults.headers.common['Authorization'];
    }
  }

  async login(agentName: string, certificatePem: string): Promise<LoginResponse> {
    const response = await this.client.post('/api/v1/auth/login', {
      agent_name: agentName,
      certificate_pem: certificatePem
    });
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get('/api/v1/auth/me');
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  // Agent Registration
  async registerAgent(request: RegistrationRequest): Promise<RegistrationResponse> {
    const response = await this.client.post('/api/v1/register', request);
    return response.data;
  }

  async renewAgent(agentName: string): Promise<ApiResponse<string>> {
    const response = await this.client.post('/api/v1/renew', { agentName });
    return response.data;
  }

  async deactivateAgent(agentName: string): Promise<ApiResponse<string>> {
    const response = await this.client.post('/api/v1/deactivate', { agentName });
    return response.data;
  }

  async getAgentStatus(agentName: string): Promise<Agent> {
    const response = await this.client.get(`/api/v1/status`, {
      params: { agentName }
    });
    return response.data;
  }

  // Agent Discovery
  async searchAgents(filters: SearchFilters = {}): Promise<Agent[]> {
    const response = await this.client.get('/api/v1/agents/search', {
      params: filters
    });
    return response.data;
  }

  async getAgentProfile(agentName: string): Promise<Agent> {
    const response = await this.client.get(`/api/v1/agents/${agentName}`);
    return response.data;
  }

  async getAgentA2ADescriptor(agentName: string): Promise<any> {
    const response = await this.client.get(`/api/v1/agents/${agentName}/a2a`);
    return response.data;
  }

  // A2A Negotiation
  async negotiateTask(request: NegotiationRequest): Promise<NegotiationResponse> {
    const response = await this.client.post('/api/v1/a2a/negotiate', request);
    return response.data;
  }

  async initiateA2ASession(
    initiatingAgent: string,
    targetAgent: string,
    task: string,
    context: Record<string, any> = {}
  ): Promise<A2ASession> {
    const response = await this.client.post('/api/v1/a2a/session/initiate', {
      initiating_agent: initiatingAgent,
      target_agent: targetAgent,
      task,
      context
    });
    return response.data;
  }

  // Session Management
  async getSessionStatus(sessionId: string): Promise<A2ASession> {
    const response = await this.client.get(`/api/v1/a2a/session/${sessionId}/status`);
    return response.data;
  }

  async updateSession(
    sessionId: string,
    updates: Partial<A2ASession>
  ): Promise<A2ASession> {
    const response = await this.client.put(`/api/v1/a2a/session/${sessionId}`, updates);
    return response.data;
  }

  async terminateSession(sessionId: string): Promise<ApiResponse<string>> {
    const response = await this.client.delete(`/api/v1/a2a/session/${sessionId}`);
    return response.data;
  }

  async getAllSessions(): Promise<A2ASession[]> {
    const response = await this.client.get('/api/v1/a2a/sessions');
    // Backend returns {sessions: [], total: 0, offset: 0, limit: 50}
    return response.data.sessions || response.data;
  }
}

// Create and export a singleton instance
const api = new ParkBenchAPI();
export default api; 