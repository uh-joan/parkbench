import React from 'react';

// Hot reload trigger - Updated at 7:01 PM
const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          ParkBench Portal
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          AI Agent Identity, Discovery, Negotiation & Orchestration Platform
        </p>
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            System Status
          </h2>
          <div className="flex items-center justify-center space-x-4">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
              <span className="text-green-700">Frontend Running</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
              <span className="text-green-700">Backend API</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App; 