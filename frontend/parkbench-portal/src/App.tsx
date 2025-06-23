import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { 
  HomeIcon, 
  MagnifyingGlassIcon as SearchIcon, 
  PlusCircleIcon, 
  ChartBarIcon,
  CogIcon 
} from '@heroicons/react/24/outline';
import Dashboard from './components/Dashboard';
import AgentDiscovery from './components/AgentDiscovery';
import AgentRegistration from './components/AgentRegistration';
import SessionMonitor from './components/SessionMonitor';
import AdminPanel from './components/AdminPanel';

const Navigation: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', name: 'Dashboard', icon: HomeIcon },
    { path: '/discovery', name: 'Discovery', icon: SearchIcon },
    { path: '/register', name: 'Register', icon: PlusCircleIcon },
    { path: '/sessions', name: 'Sessions', icon: ChartBarIcon },
    { path: '/admin', name: 'Admin', icon: CogIcon },
  ];

  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between">
          <div className="flex space-x-7">
            {/* Logo */}
            <div className="flex items-center py-4">
              <Link to="/" className="flex items-center">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg mr-2"></div>
                <span className="font-semibold text-gray-500 text-lg">ParkBench</span>
              </Link>
            </div>

            {/* Primary Nav */}
            <div className="hidden md:flex items-center space-x-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`py-4 px-2 text-gray-500 font-medium hover:text-blue-500 transition duration-300 flex items-center ${
                      isActive ? 'text-blue-500 border-b-2 border-blue-500' : ''
                    }`}
                  >
                    <Icon className="w-5 h-5 mr-1" />
                    {item.name}
                  </Link>
                );
              })}
            </div>
          </div>

          {/* Secondary Nav */}
          <div className="hidden md:flex items-center space-x-3">
            <div className="flex items-center text-sm text-gray-500">
              <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
              API Connected
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button className="outline-none mobile-menu-button">
              <svg className="w-6 h-6 text-gray-500 hover:text-blue-500"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M4 6h16M4 12h16M4 18h16"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <div className="hidden mobile-menu">
        <ul className="">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className="block text-sm px-2 py-4 text-gray-500 hover:bg-blue-500 hover:text-white transition duration-300 flex items-center"
                >
                  <Icon className="w-5 h-5 mr-2" />
                  {item.name}
                </Link>
              </li>
            );
          })}
        </ul>
      </div>
    </nav>
  );
};

const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        
        <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/discovery" element={<AgentDiscovery />} />
            <Route path="/register" element={<AgentRegistration />} />
            <Route path="/sessions" element={<SessionMonitor />} />
            <Route path="/admin" element={<AdminPanel />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-12">
          <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
            <div className="text-center text-gray-500 text-sm">
              <p>ParkBench - Open AI Agent Identity & Orchestration Platform</p>
              <p className="mt-1">Built with React, TypeScript, and Tailwind CSS</p>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
};

export default App;
