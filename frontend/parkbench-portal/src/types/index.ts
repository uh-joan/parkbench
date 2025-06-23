export interface Agent {
  agent_id: string;
  agentName: string;
  certificatePEM: string;
  agent_metadata: AgentMetadata;
  verified: boolean;
  active: boolean;
  created_at: string;
  updated_at: string;
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
  supported_tasks: string[];
  negotiation: boolean;
  context_required: string[];
  token_budget: number;
}

export interface SearchFilters {
  skill?: string;
  protocol?: string;
  a2a_compliant?: boolean;
  verified?: boolean;
  active?: boolean;
}

export interface A2ASession {
  session_id: string;
  initiating_agent: string;
  target_agent: string;
  task: string;
  context: Record<string, any>;
  session_token: string;
  status: 'active' | 'completed' | 'failed' | 'terminated';
  created_at: string;
  updated_at: string;
}

export interface NegotiationRequest {
  initiatingAgentName: string;
  requestedTask: string;
  context: Record<string, any>;
  preferredCapabilities?: Record<string, any>;
}

export interface CandidateAgent {
  agentName: string;
  matchScore: number;
  supportedTasks: string[];
  negotiation: boolean;
  token_budget: number;
}

export interface NegotiationResponse {
  candidateAgents: CandidateAgent[];
}

export interface RegistrationRequest {
  agentName: string;
  certificatePEM: string;
  metadata: AgentMetadata;
}

export interface RegistrationResponse {
  agent_id: string;
  agentName: string;
  status: string;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
} 