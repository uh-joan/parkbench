import axios, { AxiosInstance, AxiosResponse } from 'axios';
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

class ParkBenchAPI {
  private client: AxiosInstance;

  constructor(baseURL: string = 'http://localhost:9000') {
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

  // Health check
  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  // Agent Registration
  async registerAgent(request: RegistrationRequest): Promise<RegistrationResponse> {
    const response = await this.client.post('/register', request);
    return response.data;
  }

  async renewAgent(agentName: string): Promise<ApiResponse<string>> {
    const response = await this.client.post('/renew', { agentName });
    return response.data;
  }

  async deactivateAgent(agentName: string): Promise<ApiResponse<string>> {
    const response = await this.client.post('/deactivate', { agentName });
    return response.data;
  }

  async getAgentStatus(agentName: string): Promise<Agent> {
    const response = await this.client.get(`/status`, {
      params: { agentName }
    });
    return response.data;
  }

  // Agent Discovery
  async searchAgents(filters: SearchFilters = {}): Promise<Agent[]> {
    const response = await this.client.get('/agents/search', {
      params: filters
    });
    return response.data;
  }

  async getAgentProfile(agentName: string): Promise<Agent> {
    const response = await this.client.get(`/agents/${agentName}`);
    return response.data;
  }

  async getAgentA2ADescriptor(agentName: string): Promise<any> {
    const response = await this.client.get(`/agents/${agentName}/a2a`);
    return response.data;
  }

  // A2A Negotiation
  async negotiateTask(request: NegotiationRequest): Promise<NegotiationResponse> {
    const response = await this.client.post('/a2a/negotiate', request);
    return response.data;
  }

  async initiateA2ASession(
    initiatingAgent: string,
    targetAgent: string,
    task: string,
    context: Record<string, any> = {}
  ): Promise<A2ASession> {
    const response = await this.client.post('/a2a/session/initiate', {
      initiating_agent: initiatingAgent,
      target_agent: targetAgent,
      task,
      context
    });
    return response.data;
  }

  // Session Management
  async getSessionStatus(sessionId: string): Promise<A2ASession> {
    const response = await this.client.get(`/a2a/session/${sessionId}/status`);
    return response.data;
  }

  async updateSession(
    sessionId: string,
    updates: Partial<A2ASession>
  ): Promise<A2ASession> {
    const response = await this.client.put(`/a2a/session/${sessionId}`, updates);
    return response.data;
  }

  async terminateSession(sessionId: string): Promise<ApiResponse<string>> {
    const response = await this.client.delete(`/a2a/session/${sessionId}`);
    return response.data;
  }

  async getAllSessions(): Promise<A2ASession[]> {
    const response = await this.client.get('/a2a/sessions');
    return response.data;
  }
}

// Create and export a singleton instance
const api = new ParkBenchAPI();
export default api; 