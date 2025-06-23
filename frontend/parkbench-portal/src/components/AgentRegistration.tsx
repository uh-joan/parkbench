import React, { useState } from 'react';
import { RegistrationRequest, RegistrationResponse } from '../types';
import api from '../services/api';

const AgentRegistration: React.FC = () => {
  const [formData, setFormData] = useState<RegistrationRequest>({
    agent_name: '',
    certificate_pem: '',
    a2a_descriptor: {
      description: '',
      protocols: [],
      interfaces: {},
      capabilities: [],
      constraints: {}
    },
    description: '',
    tags: []
  });

  const [submitting, setSubmitting] = useState(false);
  const [response, setResponse] = useState<RegistrationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const result = await api.registerAgent(formData);
      setResponse(result);
      
      // Reset form on success
      setFormData({
        agent_name: '',
        certificate_pem: '',
        a2a_descriptor: {
          description: '',
          protocols: [],
          interfaces: {},
          capabilities: [],
          constraints: {}
        },
        description: '',
        tags: []
      });
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Registration failed');
    } finally {
      setSubmitting(false);
    }
  };

  const handleArrayInput = (field: 'protocols' | 'capabilities', value: string) => {
    const array = value.split(',').map(item => item.trim()).filter(item => item.length > 0);
    setFormData(prev => ({
      ...prev,
      a2a_descriptor: {
        ...prev.a2a_descriptor,
        [field]: array
      }
    }));
  };

  const handleTagsInput = (value: string) => {
    const tags = value.split(',').map(item => item.trim()).filter(item => item.length > 0);
    setFormData(prev => ({
      ...prev,
      tags
    }));
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">Agent Registration</h1>
          
          {/* Success/Error Messages */}
          {response && (
            <div className="mb-6 bg-green-50 border border-green-200 rounded-md p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-green-800">
                    Registration Successful!
                  </h3>
                  <div className="mt-2 text-sm text-green-700">
                    <p>Agent registered with ID: {response.agent_id}</p>
                    {response.message && <p>{response.message}</p>}
                  </div>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Registration Failed</h3>
                  <div className="mt-2 text-sm text-red-700">
                    <p>{error}</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Information */}
            <div className="bg-gray-50 px-4 py-3 rounded-lg">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="agent_name" className="block text-sm font-medium text-gray-700">
                    Agent Name *
                  </label>
                  <input
                    type="text"
                    id="agent_name"
                    required
                    placeholder="my-agent.agents.example.com"
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    value={formData.agent_name}
                    onChange={(e) => setFormData(prev => ({ ...prev, agent_name: e.target.value }))}
                  />
                </div>

                <div>
                  <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                    Description
                  </label>
                  <input
                    type="text"
                    id="description"
                    placeholder="Brief description of the agent"
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    value={formData.description || ''}
                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  />
                </div>

                <div className="md:col-span-2">
                  <label htmlFor="tags" className="block text-sm font-medium text-gray-700">
                    Tags
                  </label>
                  <input
                    type="text"
                    id="tags"
                    placeholder="ai, nlp, classification (comma-separated)"
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    value={formData.tags?.join(', ') || ''}
                    onChange={(e) => handleTagsInput(e.target.value)}
                  />
                </div>
              </div>
            </div>

            {/* A2A Descriptor */}
            <div className="bg-gray-50 px-4 py-3 rounded-lg">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Agent Capabilities</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="a2a_description" className="block text-sm font-medium text-gray-700">
                    Capability Description *
                  </label>
                  <textarea
                    id="a2a_description"
                    rows={3}
                    required
                    placeholder="Describe what this agent can do..."
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    value={formData.a2a_descriptor.description}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      a2a_descriptor: { ...prev.a2a_descriptor, description: e.target.value }
                    }))}
                  />
                </div>

                <div>
                  <label htmlFor="protocols" className="block text-sm font-medium text-gray-700">
                    Supported Protocols *
                  </label>
                  <input
                    type="text"
                    id="protocols"
                    required
                    placeholder="REST, GraphQL, WebSocket (comma-separated)"
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    value={formData.a2a_descriptor.protocols.join(', ')}
                    onChange={(e) => handleArrayInput('protocols', e.target.value)}
                  />
                </div>

                <div className="md:col-span-2">
                  <label htmlFor="capabilities" className="block text-sm font-medium text-gray-700">
                    Capabilities *
                  </label>
                  <input
                    type="text"
                    id="capabilities"
                    required
                    placeholder="text-analysis, image-processing, data-transformation (comma-separated)"
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    value={formData.a2a_descriptor.capabilities.join(', ')}
                    onChange={(e) => handleArrayInput('capabilities', e.target.value)}
                  />
                </div>
              </div>
            </div>

            {/* Certificate */}
            <div className="bg-gray-50 px-4 py-3 rounded-lg">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Authentication Certificate</h3>
              <div>
                <label htmlFor="certificate" className="block text-sm font-medium text-gray-700">
                  Certificate (PEM Format) *
                </label>
                <textarea
                  id="certificate"
                  rows={8}
                  required
                  placeholder="-----BEGIN CERTIFICATE-----&#10;...&#10;-----END CERTIFICATE-----"
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 font-mono text-xs"
                  value={formData.certificate_pem}
                  onChange={(e) => setFormData(prev => ({ ...prev, certificate_pem: e.target.value }))}
                />
                <p className="mt-2 text-sm text-gray-500">
                  Paste your X.509 certificate in PEM format. This will be used for agent authentication.
                </p>
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={submitting}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center"
              >
                {submitting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
                    Registering...
                  </>
                ) : (
                  'Register Agent'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default AgentRegistration; 