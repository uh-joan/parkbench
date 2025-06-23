import React, { useState, useEffect } from 'react';
import { 
  UsersIcon, 
  ServerIcon, 
  ChartBarIcon, 
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline';
import api from '../services/api';
import { Agent, A2ASession } from '../types';

interface DashboardStats {
  totalAgents: number;
  activeAgents: number;
  verifiedAgents: number;
  activeSessions: number;
  totalSessions: number;
  apiHealth: boolean;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalAgents: 0,
    activeAgents: 0,
    verifiedAgents: 0,
    activeSessions: 0,
    totalSessions: 0,
    apiHealth: false,
  });
  const [recentAgents, setRecentAgents] = useState<Agent[]>([]);
  const [recentSessions, setRecentSessions] = useState<A2ASession[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);

        // Check API health
        const health = await api.healthCheck();
        
        // Fetch agents
        const agents = await api.searchAgents();
        const sessions = await api.getAllSessions();

        // Calculate stats
        const dashboardStats: DashboardStats = {
          totalAgents: agents.length,
          activeAgents: agents.filter(agent => agent.active).length,
          verifiedAgents: agents.filter(agent => agent.verified).length,
          activeSessions: sessions.filter(session => session.status === 'active').length,
          totalSessions: sessions.length,
          apiHealth: health.status === 'healthy',
        };

        setStats(dashboardStats);
        setRecentAgents(agents.slice(0, 5));
        setRecentSessions(sessions.slice(0, 5));
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const StatCard: React.FC<{
    title: string;
    value: number | string;
    icon: React.ComponentType<any>;
    color: string;
    subtitle?: string;
  }> = ({ title, value, icon: Icon, color, subtitle }) => (
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
              {subtitle && <dd className="text-sm text-gray-500">{subtitle}</dd>}
            </dl>
          </div>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            Dashboard
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Welcome to ParkBench - Your AI Agent Orchestration Platform
          </p>
        </div>
        <div className="mt-4 flex md:mt-0 md:ml-4">
          <div className="flex items-center">
            {stats.apiHealth ? (
              <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
            ) : (
              <ExclamationTriangleIcon className="h-5 w-5 text-red-500 mr-2" />
            )}
            <span className={`text-sm ${stats.apiHealth ? 'text-green-600' : 'text-red-600'}`}>
              API {stats.apiHealth ? 'Healthy' : 'Unavailable'}
            </span>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Agents"
          value={stats.totalAgents}
          icon={UsersIcon}
          color="text-blue-500"
          subtitle="Registered agents"
        />
        <StatCard
          title="Active Agents"
          value={stats.activeAgents}
          icon={ServerIcon}
          color="text-green-500"
          subtitle="Currently online"
        />
        <StatCard
          title="Verified Agents"
          value={stats.verifiedAgents}
          icon={CheckCircleIcon}
          color="text-purple-500"
          subtitle="Certificate validated"
        />
        <StatCard
          title="Active Sessions"
          value={stats.activeSessions}
          icon={ChartBarIcon}
          color="text-yellow-500"
          subtitle={`${stats.totalSessions} total`}
        />
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Agents */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Recent Agents
            </h3>
            <div className="space-y-3">
              {recentAgents.length > 0 ? (
                recentAgents.map((agent) => (
                  <div key={agent.agent_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center">
                      <div className={`w-3 h-3 rounded-full mr-3 ${
                        agent.active ? 'bg-green-400' : 'bg-gray-400'
                      }`}></div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{agent.agentName}</p>
                        <p className="text-xs text-gray-500">
                          {agent.agent_metadata.skills.slice(0, 2).join(', ')}
                          {agent.agent_metadata.skills.length > 2 && '...'}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {agent.verified && <CheckCircleIcon className="h-4 w-4 text-green-500" />}
                      {agent.agent_metadata.a2a_compliant && (
                        <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">A2A</span>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-gray-500">No agents registered yet</p>
              )}
            </div>
          </div>
        </div>

        {/* Recent Sessions */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Recent Sessions
            </h3>
            <div className="space-y-3">
              {recentSessions.length > 0 ? (
                recentSessions.map((session) => (
                  <div key={session.session_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center">
                      <ClockIcon className="h-4 w-4 text-gray-400 mr-3" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">{session.task}</p>
                        <p className="text-xs text-gray-500">
                          {session.initiating_agent} → {session.target_agent}
                        </p>
                      </div>
                    </div>
                    <div>
                      <span className={`px-2 py-1 text-xs rounded ${
                        session.status === 'active' ? 'bg-green-100 text-green-800' :
                        session.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                        session.status === 'failed' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {session.status}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-gray-500">No sessions yet</p>
              )}
            </div>
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
            <button className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition duration-200">
              Register New Agent
            </button>
            <button className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg transition duration-200">
              Search Agents
            </button>
            <button className="bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded-lg transition duration-200">
              View API Docs
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 