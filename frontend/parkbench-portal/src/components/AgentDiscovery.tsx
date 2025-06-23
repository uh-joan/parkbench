import React, { useState, useEffect } from 'react';
import { 
  MagnifyingGlassIcon as SearchIcon, 
  FunnelIcon as FilterIcon,
  UserIcon,
  CheckCircleIcon,
  ClockIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { Agent, SearchFilters } from '../types';
import api from '../services/api';

const AgentDiscovery: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [filteredAgents, setFilteredAgents] = useState<Agent[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState<SearchFilters>({});
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadAgents();
  }, []);

  useEffect(() => {
    filterAgents();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [agents, searchTerm, filters]);

  const loadAgents = async () => {
    try {
      setIsLoading(true);
      const agentList = await api.searchAgents();
      setAgents(agentList);
    } catch (error) {
      console.error('Error loading agents:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filterAgents = () => {
    let filtered = [...agents];

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(agent =>
        agent.agent_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (agent.description && agent.description.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (agent.tags && agent.tags.some(tag => 
          tag.toLowerCase().includes(searchTerm.toLowerCase())
        ))
      );
    }

    // Apply filters
    if (filters.status !== undefined) {
      filtered = filtered.filter(agent => agent.status === filters.status);
    }
    if (filters.capabilities) {
      filtered = filtered.filter(agent =>
        agent.a2a_descriptor.capabilities.some(capability =>
          filters.capabilities!.includes(capability)
        )
      );
    }

    setFilteredAgents(filtered);
  };

  const AgentCard: React.FC<{ agent: Agent }> = ({ agent }) => (
    <div 
      key={agent.agent_id}
      className="bg-white rounded-lg shadow-md p-6 cursor-pointer hover:shadow-lg transition-shadow duration-200"
      onClick={() => setSelectedAgent(agent)}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center">
          <UserIcon className="h-8 w-8 text-gray-400 mr-3" />
          <div>
            <h3 className="text-lg font-medium text-gray-900">{agent.agent_name}</h3>
            <p className="text-sm text-gray-500">{agent.description || 'No description available'}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${
            agent.active ? 'bg-green-400' : 'bg-gray-400'
          }`}></div>
          {agent.status === 'active' && <CheckCircleIcon className="h-5 w-5 text-green-500" />}
        </div>
      </div>

      {/* Capabilities */}
      <div className="mt-4">
        <div className="flex flex-wrap gap-2">
          {agent.a2a_descriptor.capabilities.slice(0, 3).map((capability: string, index: number) => (
            <span key={index} className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
              {capability}
            </span>
          ))}
          {agent.a2a_descriptor.capabilities.length > 3 && (
            <span className="px-2 py-1 text-xs bg-gray-100 text-gray-500 rounded">
              +{agent.a2a_descriptor.capabilities.length - 3} more
            </span>
          )}
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between text-xs text-gray-500">
        <span>Status: {agent.status}</span>
        <span className="flex items-center">
          <ClockIcon className="h-3 w-3 mr-1" />
          {new Date(agent.created_at).toLocaleDateString()}
        </span>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">Agent Discovery</h1>
          
          {/* Search and Filter Bar */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="flex-1 relative">
              <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search agents..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            
            <div className="flex gap-3">
              <div className="flex items-center space-x-2">
                <FilterIcon className="h-5 w-5 text-gray-400" />
                <select
                  className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
                  value={filters.status || ''}
                  onChange={(e) => setFilters(prev => ({
                    ...prev,
                    status: e.target.value === '' ? undefined : e.target.value as 'active' | 'inactive' | 'pending'
                  }))}
                >
                  <option value="">All Status</option>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="pending">Pending</option>
                </select>
              </div>
              
              <button 
                onClick={() => {
                  setSearchTerm('');
                  setFilters({});
                }}
                className="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
              >
                Clear
              </button>
            </div>
          </div>

          {/* Results */}
          {isLoading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-500">Loading agents...</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredAgents.map(agent => (
                <AgentCard key={agent.agent_id} agent={agent} />
              ))}
              {filteredAgents.length === 0 && (
                <div className="col-span-full text-center py-12">
                  <UserIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">No agents found matching your criteria.</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Agent Details Modal */}
      {selectedAgent && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-screen overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  {selectedAgent.agent_name}
                </h3>
                <button
                  className="text-gray-400 hover:text-gray-600"
                  onClick={() => setSelectedAgent(null)}
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>

              <div className="space-y-4">
                {/* Basic Info */}
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Description</h4>
                  <p className="text-sm text-gray-600">{selectedAgent.description || 'No description available'}</p>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-gray-900">Capabilities</h4>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {selectedAgent.a2a_descriptor.capabilities.map((capability: string, index: number) => (
                      <span key={index} className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                        {capability}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-gray-900">Protocols</h4>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {selectedAgent.a2a_descriptor.protocols.map((protocol: string, index: number) => (
                      <span key={index} className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded">
                        {protocol}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Technical Details */}
                <div className="border-t pt-4">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Technical Details</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Agent ID:</span> {selectedAgent.agent_id}
                    </div>
                    <div>
                      <span className="font-medium">Status:</span>
                      <span className={`ml-1 px-2 py-1 text-xs rounded ${
                        selectedAgent.active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {selectedAgent.active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                    <div>
                      <span className="font-medium">Created:</span> {new Date(selectedAgent.created_at).toLocaleDateString()}
                    </div>
                    {selectedAgent.last_seen && (
                      <div>
                        <span className="font-medium">Last Seen:</span> {new Date(selectedAgent.last_seen).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentDiscovery; 