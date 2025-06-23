import React, { useState, useEffect } from 'react';
import { 
  MagnifyingGlassIcon as SearchIcon, 
  FunnelIcon as FilterIcon, 
  UserIcon, 
  CheckCircleIcon,
  ClockIcon 
} from '@heroicons/react/24/outline';
import api from '../services/api';
import { Agent, SearchFilters } from '../types';

const AgentDiscovery: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [filteredAgents, setFilteredAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState<SearchFilters>({});
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        setLoading(true);
        const data = await api.searchAgents();
        setAgents(data);
        setFilteredAgents(data);
      } catch (error) {
        console.error('Error fetching agents:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAgents();
  }, []);

  useEffect(() => {
    let filtered = agents;

    // Apply search term
    if (searchTerm) {
      filtered = filtered.filter(agent =>
        agent.agentName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        agent.agent_metadata.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        agent.agent_metadata.skills.some(skill => 
          skill.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    // Apply filters
    if (filters.verified !== undefined) {
      filtered = filtered.filter(agent => agent.verified === filters.verified);
    }
    if (filters.active !== undefined) {
      filtered = filtered.filter(agent => agent.active === filters.active);
    }
    if (filters.a2a_compliant !== undefined) {
      filtered = filtered.filter(agent => agent.agent_metadata.a2a_compliant === filters.a2a_compliant);
    }
    if (filters.skill) {
      filtered = filtered.filter(agent =>
        agent.agent_metadata.skills.some(skill =>
          skill.toLowerCase().includes(filters.skill!.toLowerCase())
        )
      );
    }

    setFilteredAgents(filtered);
  }, [agents, searchTerm, filters]);

  const AgentCard: React.FC<{ agent: Agent }> = ({ agent }) => (
    <div 
      className="bg-white rounded-lg shadow-md p-6 card-hover cursor-pointer"
      onClick={() => setSelectedAgent(agent)}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center">
          <UserIcon className="h-8 w-8 text-gray-400 mr-3" />
          <div>
            <h3 className="text-lg font-medium text-gray-900">{agent.agentName}</h3>
            <p className="text-sm text-gray-500">{agent.agent_metadata.description}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${
            agent.active ? 'bg-green-400' : 'bg-gray-400'
          }`}></div>
          {agent.verified && <CheckCircleIcon className="h-5 w-5 text-green-500" />}
          {agent.agent_metadata.a2a_compliant && (
            <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">A2A</span>
          )}
        </div>
      </div>

      <div className="mt-4">
        <div className="flex flex-wrap gap-2">
          {agent.agent_metadata.skills.slice(0, 3).map((skill, index) => (
            <span key={index} className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
              {skill}
            </span>
          ))}
          {agent.agent_metadata.skills.length > 3 && (
            <span className="px-2 py-1 text-xs bg-gray-100 text-gray-500 rounded">
              +{agent.agent_metadata.skills.length - 3} more
            </span>
          )}
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between text-xs text-gray-500">
        <span>Version {agent.agent_metadata.version}</span>
        <span className="flex items-center">
          <ClockIcon className="h-3 w-3 mr-1" />
          {new Date(agent.created_at).toLocaleDateString()}
        </span>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            Agent Discovery
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Find and explore registered AI agents in the ParkBench network
          </p>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Search */}
          <div className="lg:col-span-2">
            <div className="relative">
              <SearchIcon className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search agents by name, description, or skills..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>

          {/* Filters */}
          <div className="flex items-center space-x-4">
            <FilterIcon className="h-5 w-5 text-gray-400" />
            <select
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
              value={filters.verified !== undefined ? String(filters.verified) : ''}
              onChange={(e) => setFilters(prev => ({
                ...prev,
                verified: e.target.value === '' ? undefined : e.target.value === 'true'
              }))}
            >
              <option value="">All Agents</option>
              <option value="true">Verified Only</option>
              <option value="false">Unverified Only</option>
            </select>

            <select
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
              value={filters.a2a_compliant !== undefined ? String(filters.a2a_compliant) : ''}
              onChange={(e) => setFilters(prev => ({
                ...prev,
                a2a_compliant: e.target.value === '' ? undefined : e.target.value === 'true'
              }))}
            >
              <option value="">All Types</option>
              <option value="true">A2A Compliant</option>
              <option value="false">Non-A2A</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-medium text-gray-900">
            Agents ({filteredAgents.length})
          </h3>
          <div className="text-sm text-gray-500">
            {loading ? 'Loading...' : `${filteredAgents.length} of ${agents.length} agents`}
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        ) : filteredAgents.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAgents.map((agent) => (
              <AgentCard key={agent.agent_id} agent={agent} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <UserIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No agents found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Try adjusting your search terms or filters.
            </p>
          </div>
        )}
      </div>

      {/* Agent Detail Modal */}
      {selectedAgent && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  {selectedAgent.agentName}
                </h3>
                <button
                  className="text-gray-400 hover:text-gray-600"
                  onClick={() => setSelectedAgent(null)}
                >
                  <span className="sr-only">Close</span>
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Description</h4>
                  <p className="text-sm text-gray-600">{selectedAgent.agent_metadata.description}</p>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-gray-900">Skills</h4>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {selectedAgent.agent_metadata.skills.map((skill, index) => (
                      <span key={index} className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-gray-900">Protocols</h4>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {selectedAgent.agent_metadata.protocols.map((protocol, index) => (
                      <span key={index} className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded">
                        {protocol}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Version:</span> {selectedAgent.agent_metadata.version}
                  </div>
                  <div>
                    <span className="font-medium">Status:</span>
                    <span className={`ml-1 ${selectedAgent.active ? 'text-green-600' : 'text-gray-600'}`}>
                      {selectedAgent.active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  <div>
                    <span className="font-medium">Verified:</span>
                    <span className={`ml-1 ${selectedAgent.verified ? 'text-green-600' : 'text-red-600'}`}>
                      {selectedAgent.verified ? 'Yes' : 'No'}
                    </span>
                  </div>
                  <div>
                    <span className="font-medium">A2A Compliant:</span>
                    <span className={`ml-1 ${selectedAgent.agent_metadata.a2a_compliant ? 'text-blue-600' : 'text-gray-600'}`}>
                      {selectedAgent.agent_metadata.a2a_compliant ? 'Yes' : 'No'}
                    </span>
                  </div>
                </div>

                <div className="mt-6 flex justify-end space-x-3">
                  <button
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                    onClick={() => setSelectedAgent(null)}
                  >
                    Close
                  </button>
                  <button className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700">
                    Initiate A2A Session
                  </button>
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