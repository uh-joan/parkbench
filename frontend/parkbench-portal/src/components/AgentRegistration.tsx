import React, { useState } from 'react';
import { PlusCircleIcon } from '@heroicons/react/24/outline';
import api from '../services/api';
import { RegistrationRequest, AgentMetadata } from '../types';

const AgentRegistration: React.FC = () => {
  const [formData, setFormData] = useState<RegistrationRequest>({
    agentName: '',
    certificatePEM: '',
    metadata: {
      description: '',
      version: '1.0.0',
      maintainer_contact: '',
      api_endpoint: '',
      protocols: ['REST'],
      a2a_compliant: false,
      skills: [],
      input_formats: ['JSON'],
      output_formats: ['JSON'],
      pricing_model: 'free',
      public_key: '',
      a2a: {
        supported_tasks: [],
        negotiation: false,
        context_required: [],
        token_budget: 1000
      }
    }
  });

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const response = await api.registerAgent(formData);
      setMessage({ type: 'success', text: `Agent registered successfully! ID: ${response.agent_id}` });
      // Reset form on success
      setFormData({
        agentName: '',
        certificatePEM: '',
        metadata: {
          description: '',
          version: '1.0.0',
          maintainer_contact: '',
          api_endpoint: '',
          protocols: ['REST'],
          a2a_compliant: false,
          skills: [],
          input_formats: ['JSON'],
          output_formats: ['JSON'],
          pricing_model: 'free',
          public_key: '',
          a2a: {
            supported_tasks: [],
            negotiation: false,
            context_required: [],
            token_budget: 1000
          }
        }
      });
    } catch (error: any) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Registration failed. Please check your input.' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleArrayInput = (field: keyof AgentMetadata, value: string) => {
    const array = value.split(',').map(item => item.trim()).filter(item => item);
    setFormData(prev => ({
      ...prev,
      metadata: {
        ...prev.metadata,
        [field]: array
      }
    }));
  };

  return (
    <div className="space-y-6">
      <div className="md:flex md:items-center md:justify-between">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            Agent Registration
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Register a new AI agent in the ParkBench network
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Basic Information
            </h3>
            
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Agent Name (DNS format)
                </label>
                <input
                  type="text"
                  required
                  placeholder="my-agent.agents.example.com"
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  value={formData.agentName}
                  onChange={(e) => setFormData(prev => ({ ...prev, agentName: e.target.value }))}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Version
                </label>
                <input
                  type="text"
                  required
                  placeholder="1.0.0"
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  value={formData.metadata.version}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    metadata: { ...prev.metadata, version: e.target.value }
                  }))}
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block text-sm font-medium text-gray-700">
                  Description
                </label>
                <textarea
                  required
                  rows={3}
                  placeholder="Describe what this agent does..."
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  value={formData.metadata.description}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    metadata: { ...prev.metadata, description: e.target.value }
                  }))}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Maintainer Contact
                </label>
                <input
                  type="email"
                  required
                  placeholder="maintainer@example.com"
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  value={formData.metadata.maintainer_contact}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    metadata: { ...prev.metadata, maintainer_contact: e.target.value }
                  }))}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  API Endpoint
                </label>
                <input
                  type="url"
                  required
                  placeholder="https://api.example.com/agent"
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  value={formData.metadata.api_endpoint}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    metadata: { ...prev.metadata, api_endpoint: e.target.value }
                  }))}
                />
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Capabilities
            </h3>
            
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Skills (comma-separated)
                </label>
                <input
                  type="text"
                  placeholder="translation, summarization, analysis"
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  onChange={(e) => handleArrayInput('skills', e.target.value)}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Protocols (comma-separated)
                </label>
                <input
                  type="text"
                  placeholder="REST, GraphQL, A2A"
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  value={formData.metadata.protocols.join(', ')}
                  onChange={(e) => handleArrayInput('protocols', e.target.value)}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Input Formats (comma-separated)
                </label>
                <input
                  type="text"
                  placeholder="JSON, CSV, XML"
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  value={formData.metadata.input_formats.join(', ')}
                  onChange={(e) => handleArrayInput('input_formats', e.target.value)}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Output Formats (comma-separated)
                </label>
                <input
                  type="text"
                  placeholder="JSON, CSV, PDF"
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  value={formData.metadata.output_formats.join(', ')}
                  onChange={(e) => handleArrayInput('output_formats', e.target.value)}
                />
              </div>

              <div className="sm:col-span-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                    checked={formData.metadata.a2a_compliant}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      metadata: { ...prev.metadata, a2a_compliant: e.target.checked }
                    }))}
                  />
                  <span className="ml-2 text-sm text-gray-700">A2A Compliant</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Certificate
            </h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">
                X.509 Certificate (PEM format)
              </label>
              <textarea
                required
                rows={10}
                placeholder="-----BEGIN CERTIFICATE-----&#10;...&#10;-----END CERTIFICATE-----"
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 font-mono text-xs"
                value={formData.certificatePEM}
                onChange={(e) => setFormData(prev => ({ ...prev, certificatePEM: e.target.value }))}
              />
              <p className="mt-2 text-sm text-gray-500">
                Paste your X.509 certificate in PEM format. This will be used for identity verification.
              </p>
            </div>
          </div>
        </div>

        {message && (
          <div className={`rounded-md p-4 ${
            message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
          }`}>
            {message.text}
          </div>
        )}

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {loading ? (
              <>
                <div className="animate-spin -ml-1 mr-3 h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                Registering...
              </>
            ) : (
              <>
                <PlusCircleIcon className="-ml-1 mr-2 h-4 w-4" />
                Register Agent
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AgentRegistration; 