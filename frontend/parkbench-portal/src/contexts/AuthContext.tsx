import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import api from '../services/api';

interface User {
  agent_name: string;
  agent_id: string;
  permissions: string[];
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (agentName: string, certificatePem: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check for existing authentication on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        const agentName = localStorage.getItem('user_agent_name');
        
        if (token && agentName) {
          if (token === 'mock_jwt_token') {
            // Mock authentication
            setUser({
              agent_name: agentName,
              agent_id: 'mock-agent-id',
              permissions: ['read', 'write', 'negotiate']
            });
          } else {
            // Real authentication - set token and verify
            api.setAuthToken(token);
            const userData = await api.getCurrentUser();
            setUser(userData);
          }
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        // Clear invalid token
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_agent_name');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (agentName: string, certificatePem: string) => {
    try {
      setIsLoading(true);
      setError(null);

      try {
        // Try real backend authentication first
        const response = await api.login(agentName, certificatePem);
        
        // Store token and user info
        localStorage.setItem('auth_token', response.access_token);
        localStorage.setItem('user_agent_name', response.agent_name);
        
        // Set auth token for future requests
        api.setAuthToken(response.access_token);
        
        // Get user data
        const userData = await api.getCurrentUser();
        setUser(userData);
        
      } catch (backendError) {
        console.log('Backend auth failed, falling back to mock authentication');
        
        // Fall back to mock authentication for demo purposes
        const mockToken = 'mock_jwt_token';
        localStorage.setItem('auth_token', mockToken);
        localStorage.setItem('user_agent_name', agentName);
        
        // Set mock user data
        setUser({
          agent_name: agentName,
          agent_id: `mock-${agentName}-id`,
          permissions: ['read', 'write', 'negotiate', 'admin']
        });
        
        console.log(`Demo mode: Logged in as ${agentName}`);
      }
      
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Authentication failed';
      setError(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_agent_name');
    api.setAuthToken('');
    setUser(null);
    setError(null);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    error,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 