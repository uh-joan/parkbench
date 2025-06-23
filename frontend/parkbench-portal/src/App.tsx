import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import LandingPage from './components/LandingPage';
import Login from './components/Login';
import PrivateRoute from './components/PrivateRoute';
import AuthenticatedLayout from './components/AuthenticatedLayout';
import Dashboard from './components/Dashboard';
import AgentDiscovery from './components/AgentDiscovery';
import AgentRegistration from './components/AgentRegistration';
import SessionMonitor from './components/SessionMonitor';
import AdminPanel from './components/AdminPanel';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<Login />} />
            
            {/* Protected routes */}
            <Route
              path="/dashboard"
              element={
                <PrivateRoute>
                  <AuthenticatedLayout>
                    <Dashboard />
                  </AuthenticatedLayout>
                </PrivateRoute>
              }
            />
            <Route
              path="/discovery"
              element={
                <PrivateRoute>
                  <AuthenticatedLayout>
                    <AgentDiscovery />
                  </AuthenticatedLayout>
                </PrivateRoute>
              }
            />
            <Route
              path="/registration"
              element={
                <PrivateRoute>
                  <AuthenticatedLayout>
                    <AgentRegistration />
                  </AuthenticatedLayout>
                </PrivateRoute>
              }
            />
            <Route
              path="/sessions"
              element={
                <PrivateRoute>
                  <AuthenticatedLayout>
                    <SessionMonitor />
                  </AuthenticatedLayout>
                </PrivateRoute>
              }
            />
            <Route
              path="/admin"
              element={
                <PrivateRoute>
                  <AuthenticatedLayout>
                    <AdminPanel />
                  </AuthenticatedLayout>
                </PrivateRoute>
              }
            />
            
            {/* Redirect all other routes to home */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
