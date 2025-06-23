import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { 
  KeyIcon, 
  RocketLaunchIcon,
  EyeIcon,
  EyeSlashIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

const Login: React.FC = () => {
  const [agentName, setAgentName] = useState('');
  const [certificatePem, setCertificatePem] = useState('');
  const [showCertificate, setShowCertificate] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [useMockAuth, setUseMockAuth] = useState(false);
  const { login, error } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      // Always use the AuthContext login method for consistent state management
      await login(agentName, certificatePem);
      navigate('/dashboard');
    } catch (error) {
      // Error is handled by AuthContext
    } finally {
      setIsLoading(false);
    }
  };

  const loadSampleCertificate = () => {
    // Realistic demo certificate for testing
    const sampleCert = `-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAKXxxxxxxxxxxxxxx
MIIDXTCCAkWgAwIBAgIJAKoK/heBjcOuMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV
BAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBX
aWRnaXRzIFB0eSBMdGQwHhcNMjQwMTAxMDAwMDAwWhcNMjUwMTAxMDAwMDAwWjBF
MQswCQYDVQQGEwJBVTETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UECgwYSW50
ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIB
CgKCAQEAu1SU1LfVLPHCozMxH2Mo4lgOEePzNm0tRgeLezV6ffAt0gunVTLw7onL
Rnrqxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
-----END CERTIFICATE-----`;
    setCertificatePem(sampleCert);
    setAgentName('demo-agent');
    setUseMockAuth(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center justify-center">
            <RocketLaunchIcon className="h-10 w-10 text-blue-600 mr-3" />
            <h1 className="text-3xl font-bold text-gray-900">ParkBench</h1>
          </Link>
          <p className="mt-4 text-gray-600">
            Sign in to access the AI agent platform
          </p>
        </div>

        {/* Login Form */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Error Message */}
            {error && !useMockAuth && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start">
                <ExclamationTriangleIcon className="h-5 w-5 text-red-400 mt-0.5 mr-3 flex-shrink-0" />
                <div className="text-sm text-red-700">{error}</div>
              </div>
            )}

            {/* Demo Mode Notice */}
            {useMockAuth && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start">
                <div className="text-sm text-blue-700">
                  <strong>Demo Mode:</strong> Using mock authentication for demonstration. 
                  In production, this would authenticate against the backend server.
                </div>
              </div>
            )}

            {/* Agent Name Field */}
            <div>
              <label htmlFor="agentName" className="block text-sm font-medium text-gray-700 mb-2">
                Agent Name
              </label>
              <input
                id="agentName"
                type="text"
                value={agentName}
                onChange={(e) => setAgentName(e.target.value)}
                className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                placeholder="Enter your agent name"
                required
              />
            </div>

            {/* Certificate Field */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label htmlFor="certificate" className="block text-sm font-medium text-gray-700">
                  Certificate (PEM Format)
                </label>
                <button
                  type="button"
                  onClick={() => setShowCertificate(!showCertificate)}
                  className="text-sm text-blue-600 hover:text-blue-700 flex items-center"
                >
                  {showCertificate ? (
                    <>
                      <EyeSlashIcon className="h-4 w-4 mr-1" />
                      Hide
                    </>
                  ) : (
                    <>
                      <EyeIcon className="h-4 w-4 mr-1" />
                      Show
                    </>
                  )}
                </button>
              </div>
              <textarea
                id="certificate"
                value={certificatePem}
                onChange={(e) => setCertificatePem(e.target.value)}
                className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors font-mono text-sm"
                rows={showCertificate ? 8 : 3}
                placeholder="Paste your PEM certificate here..."
                style={{ resize: 'vertical' }}
                required={false}
              />
            </div>

            {/* Demo Toggle */}
            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                id="mockAuth"
                checked={useMockAuth}
                onChange={(e) => setUseMockAuth(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="mockAuth" className="text-sm text-gray-700">
                Use demo mode (bypass backend authentication)
              </label>
            </div>

            {/* Demo Button */}
            <div className="text-center">
              <button
                type="button"
                onClick={loadSampleCertificate}
                className="text-sm text-blue-600 hover:text-blue-700 underline"
              >
                Load demo credentials for testing
              </button>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading || !agentName.trim() || (!useMockAuth && !certificatePem.trim())}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white py-3 px-4 rounded-lg font-medium transition-colors flex items-center justify-center"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent mr-2"></div>
                  Authenticating...
                </>
              ) : (
                <>
                  <KeyIcon className="h-5 w-5 mr-2" />
                  {useMockAuth ? 'Sign In (Demo)' : 'Sign In'}
                </>
              )}
            </button>
          </form>

          {/* Footer */}
          <div className="mt-6 pt-6 border-t border-gray-200 text-center">
            <p className="text-sm text-gray-600">
              Need access?{' '}
              <button type="button" className="text-blue-600 hover:text-blue-700 font-medium">
                Contact your administrator
              </button>
            </p>
            <p className="text-xs text-gray-500 mt-2">
              <Link to="/" className="hover:text-gray-700">
                ← Back to home
              </Link>
            </p>
          </div>
        </div>

        {/* Security Notice */}
        <div className="mt-6 text-center">
          <p className="text-xs text-gray-500">
            Your certificate is used for secure authentication and is never stored on our servers.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login; 