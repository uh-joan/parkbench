import React, { useState, useEffect } from 'react';
import { 
  ChartBarIcon, 
  UserGroupIcon, 
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon 
} from '@heroicons/react/24/outline';
import { Agent, A2ASession } from '../types';
import api from '../services/api';

interface DashboardStats {
  totalAgents: number;
  activeAgents: number;
  totalSessions: number;
  activeSessions: number;
  apiHealth: boolean;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalAgents: 0,
    activeAgents: 0,
    totalSessions: 0,
    activeSessions: 0,
    apiHealth: false
  });
  const [recentAgents, setRecentAgents] = useState<Agent[]>([]);
  const [recentSessions, setRecentSessions] = useState<A2ASession[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      try {
        // Try to load real data from backend (works even with mock auth)
        const [health, agents, sessions] = await Promise.all([
          api.healthCheck(),
          api.searchAgents(),
          api.getAllSessions()
        ]);

        // Calculate stats from real data
        const dashboardStats: DashboardStats = {
          totalAgents: agents.length,
          activeAgents: agents.filter(agent => agent.active).length,
          activeSessions: sessions.filter(session => session.status === 'active').length,
          totalSessions: sessions.length,
          apiHealth: health.status === 'healthy',
        };

        setStats(dashboardStats);
        setRecentAgents(agents.slice(0, 5));
        setRecentSessions(sessions.slice(0, 5));
        
        console.log('Dashboard loaded real data from backend');
        
      } catch (backendError) {
        console.log('Backend unavailable, using mock data for dashboard');
        
        // Fall back to mock data only if backend is completely unavailable
        const mockAgents: Agent[] = [
          {
            agent_id: 'mock-1',
            agent_name: 'demo-agent',
            active: true,
            status: 'active',
            created_at: new Date().toISOString(),
            a2a_descriptor: {
              description: 'Demo agent for text processing and data analysis',
              protocols: ['REST', 'WebSocket'],
              interfaces: { api: '/api/v1' },
              capabilities: ['text-processing', 'data-analysis', 'task-automation']
            }
          },
          {
            agent_id: 'mock-2', 
            agent_name: 'analysis-bot',
            active: true,
            status: 'active',
            created_at: new Date().toISOString(),
            a2a_descriptor: {
              description: 'Specialized agent for data analysis and reporting',
              protocols: ['REST', 'GraphQL'],
              interfaces: { api: '/api/v1' },
              capabilities: ['data-analysis', 'reporting', 'visualization']
            }
          },
          {
            agent_id: 'mock-3',
            agent_name: 'task-helper',
            active: false,
            status: 'inactive',
            created_at: new Date(Date.now() - 86400000).toISOString(),
            a2a_descriptor: {
              description: 'Task management and scheduling assistant',
              protocols: ['REST'],
              interfaces: { api: '/api/v1' },
              capabilities: ['task-management', 'scheduling']
            }
          }
        ];

        const mockSessions: A2ASession[] = [
          {
            session_id: 'session-1',
            initiating_agent: 'demo-agent',
            target_agent: 'analysis-bot',
            task: 'Analyze quarterly sales data',
            status: 'active',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            context: { data_type: 'sales', quarter: 'Q4' },
            messages: []
          },
          {
            session_id: 'session-2',
            initiating_agent: 'analysis-bot',
            target_agent: 'task-helper',
            task: 'Schedule follow-up meeting',
            status: 'completed',
            created_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
            updated_at: new Date(Date.now() - 86400000).toISOString(),
            context: { meeting_type: 'follow-up', participants: 2 },
            messages: []
          }
        ];

        // Calculate stats from mock data
        const mockStats: DashboardStats = {
          totalAgents: mockAgents.length,
          activeAgents: mockAgents.filter(agent => agent.active).length,
          activeSessions: mockSessions.filter(session => session.status === 'active').length,
          totalSessions: mockSessions.length,
          apiHealth: false, // Backend is down
        };

        setStats(mockStats);
        setRecentAgents(mockAgents.slice(0, 5));
        setRecentSessions(mockSessions.slice(0, 5));
      }
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const StatCard: React.FC<{ 
    title: string; 
    value: number | string; 
    icon: React.ElementType; 
    color: string;
    trend?: string;
  }> = ({ title, value, icon: Icon, color, trend }) => (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <Icon className={`h-6 w-6 ${color}`} />
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
              <dd className="text-lg font-medium text-gray-900">{value}</dd>
            </dl>
          </div>
        </div>
        {trend && (
          <div className="mt-3">
            <div className="text-sm text-gray-600">{trend}</div>
          </div>
        )}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Overview of your ParkBench platform status and activity
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Agents"
          value={stats.totalAgents}
          icon={UserGroupIcon}
          color="text-blue-600"
        />
        <StatCard
          title="Active Agents"
          value={stats.activeAgents}
          icon={CheckCircleIcon}
          color="text-green-600"
        />
        <StatCard
          title="Active Sessions"
          value={stats.activeSessions}
          icon={ChartBarIcon}
          color="text-purple-600"
        />
        <StatCard
          title="API Health"
          value={stats.apiHealth ? "Healthy" : "Down"}
          icon={stats.apiHealth ? CheckCircleIcon : ExclamationTriangleIcon}
          color={stats.apiHealth ? "text-green-600" : "text-red-600"}
        />
      </div>

      {/* Recent Activity Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Agents */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Recent Agents
            </h3>
            {recentAgents.length > 0 ? (
              <div className="space-y-3">
                {recentAgents.map((agent) => (
                  <div key={agent.agent_id} className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50">
                    <div className={`w-3 h-3 rounded-full ${
                      agent.active ? 'bg-green-400' : 'bg-gray-400'
                    }`}></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{agent.agent_name}</p>
                      <p className="text-xs text-gray-500">
                        {agent.a2a_descriptor.capabilities.slice(0, 2).join(', ')}
                        {agent.a2a_descriptor.capabilities.length > 2 && '...'}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      {agent.status === 'active' && <CheckCircleIcon className="h-4 w-4 text-green-500" />}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No agents registered yet.</p>
            )}
          </div>
        </div>

        {/* Recent Sessions */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Recent Sessions
            </h3>
            {recentSessions.length > 0 ? (
              <div className="space-y-3">
                {recentSessions.map((session) => (
                  <div key={session.session_id} className="p-3 rounded-lg hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {session.initiating_agent} → {session.target_agent}
                        </p>
                        <p className="text-xs text-gray-500 truncate">{session.task}</p>
                      </div>
                      <div className="ml-2 flex-shrink-0">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          session.status === 'active' ? 'bg-green-100 text-green-800' :
                          session.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                          session.status === 'failed' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {session.status}
                        </span>
                      </div>
                    </div>
                    <div className="mt-2 flex items-center text-xs text-gray-500">
                      <ClockIcon className="h-3 w-3 mr-1" />
                      {new Date(session.created_at).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No sessions initiated yet.</p>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Quick Actions
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <button className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
              <UserGroupIcon className="h-5 w-5 mr-2 text-gray-400" />
              Register New Agent
            </button>
            <button className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
              <ChartBarIcon className="h-5 w-5 mr-2 text-gray-400" />
              Start A2A Session
            </button>
            <button className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
              <ClockIcon className="h-5 w-5 mr-2 text-gray-400" />
              View All Sessions
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 