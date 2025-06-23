export interface Agent {
  agent_name: string;
  agent_id: string;
  a2a_descriptor: A2ADescriptor;
  active: boolean;
  created_at: string;
  last_seen?: string;
  description?: string;
  tags?: string[];
  status: 'active' | 'inactive' | 'pending';
}

export interface AgentMetadata {
  description: string;
  version: string;
  maintainer_contact: string;
  api_endpoint: string;
  protocols: string[];
  a2a_compliant: boolean;
  skills: string[];
  input_formats: string[];
  output_formats: string[];
  pricing_model: string;
  public_key: string;
  a2a?: A2ADescriptor;
}

export interface A2ADescriptor {
  description: string;
  protocols: string[];
  interfaces: Record<string, any>;
  capabilities: string[];
  constraints?: Record<string, any>;
}

export interface SearchFilters {
  name?: string;
  tags?: string[];
  capabilities?: string[];
  status?: 'active' | 'inactive' | 'pending';
  protocol?: string;
}

export interface A2ASession {
  session_id: string;
  initiating_agent: string;
  target_agent: string;
  task: string;
  status: 'initiated' | 'negotiating' | 'active' | 'completed' | 'failed' | 'terminated';
  created_at: string;
  updated_at: string;
  context: Record<string, any>;
  messages: SessionMessage[];
}

export interface SessionMessage {
  timestamp: string;
  sender: string;
  message_type: string;
  content: any;
}

export interface NegotiationRequest {
  initiating_agent: string;
  target_agent: string;
  task: string;
  requirements: Record<string, any>;
  constraints?: Record<string, any>;
}

export interface NegotiationResponse {
  session_id: string;
  status: 'accepted' | 'rejected' | 'counter_proposal';
  terms?: Record<string, any>;
  message?: string;
}

export interface RegistrationRequest {
  agent_name: string;
  certificate_pem: string;
  a2a_descriptor: A2ADescriptor;
  description?: string;
  tags?: string[];
}

export interface RegistrationResponse {
  agent_id: string;
  agent_name: string;
  status: string;
  message?: string;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface User {
  agent_name: string;
  agent_id: string;
  permissions: string[];
  auth_type: string;
  rate_limit: number;
}

export interface LoginRequest {
  agent_name: string;
  certificate_pem: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  agent_name: string;
} 