import React from 'react';
import { Link } from 'react-router-dom';
import { 
  GlobeAltIcon, 
  ShieldCheckIcon, 
  UserGroupIcon,
  RocketLaunchIcon,
  SparklesIcon,
  DocumentCheckIcon,
  ChatBubbleLeftRightIcon,
  LinkIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

const LandingPage: React.FC = () => {
  const features = [
    {
      icon: <GlobeAltIcon className="h-8 w-8" />,
      title: "Vendor-Neutral Discovery",
      description: "The universal registry that connects agents across OpenAI, Anthropic, LangChain, and all other ecosystems - no vendor lock-in."
    },
    {
      icon: <LinkIcon className="h-8 w-8" />,
      title: "A2A Protocol Ready",
      description: "Built for agent-to-agent discovery with full A2A protocol support, enabling dynamic machine-to-machine agent connections."
    },
    {
      icon: <UserGroupIcon className="h-8 w-8" />,
      title: "Cross-Platform Orchestration",
      description: "Discover and connect agents regardless of their underlying framework - LangChain, AutoGPT, SuperAGI, or custom builds."
    },
    {
      icon: <ShieldCheckIcon className="h-8 w-8" />,
      title: "Independent Trust Layer",
      description: "Neutral verification and reputation system not controlled by any single AI vendor, ensuring fair and open agent discovery."
    }
  ];

  const differentiators = [
    {
      title: "Open Infrastructure vs Walled Gardens",
      description: "Unlike GPT Store or Anthropic Hub, ParkBench is vendor-neutral infrastructure that connects all agent ecosystems."
    },
    {
      title: "Agent-to-Agent vs Human-to-Agent",
      description: "Purpose-built for machine-to-machine agent discovery, not just human browsing of AI assistants."
    },
    {
      title: "Standards-Based Interoperability",
      description: "First mover in A2A protocol adoption, creating the foundation for cross-vendor agent collaboration."
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <RocketLaunchIcon className="h-8 w-8 text-blue-600 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">ParkBench</h1>
            </div>
            <div className="flex space-x-4">
              <Link
                to="/login"
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
              >
                Login
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              The Universal
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600 ml-3">
                Agent Discovery Network
              </span>
            </h1>
            <p className="text-xl text-gray-600 mb-6 leading-relaxed">
              <strong>Vendor-neutral infrastructure</strong> connecting AI agents across all ecosystems.
            </p>
            <p className="text-lg text-gray-500 mb-8 leading-relaxed">
              Unlike closed platforms (GPT Store, Anthropic Hub), ParkBench enables true cross-vendor agent interoperability 
              with A2A protocol support and independent trust layers.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/login"
                className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-all duration-200 transform hover:scale-105 shadow-lg"
              >
                Register Your Agent
              </Link>
              <a
                href="#features"
                className="border-2 border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white px-8 py-4 rounded-lg text-lg font-semibold transition-all duration-200"
              >
                See How It Works
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Differentiation Banner */}
      <section className="py-12 bg-gradient-to-r from-gray-900 to-blue-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-2xl font-bold mb-4">
            "The DNS for AI Agents" - Connecting What Closed Platforms Keep Separate
          </h2>
          <p className="text-lg opacity-90">
            OpenAI and Anthropic want to own your agents. <strong>ParkBench connects your agents.</strong>
          </p>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Built for the Multi-Agent Future
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Open infrastructure that enables agents to discover and collaborate across all ecosystems
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="bg-gray-50 rounded-xl p-6 hover:bg-gray-100 transition-colors duration-200 group"
              >
                <div className="text-blue-600 mb-4 group-hover:scale-110 transition-transform duration-200">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Differentiation Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Why ParkBench vs Closed Platforms?
            </h2>
            <p className="text-xl text-gray-600">
              The future of AI is multi-vendor, multi-agent, and cross-platform
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            {differentiators.map((diff, index) => (
              <div key={index} className="bg-white rounded-xl p-6 shadow-sm">
                <CheckCircleIcon className="h-8 w-8 text-green-600 mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {diff.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {diff.description}
                </p>
              </div>
            ))}
          </div>

          {/* Comparison Table */}
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <div className="px-6 py-4 bg-blue-600 text-white">
              <h3 className="text-xl font-semibold">Platform Comparison</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Feature</th>
                    <th className="px-6 py-3 text-center text-sm font-medium text-gray-500">ParkBench</th>
                    <th className="px-6 py-3 text-center text-sm font-medium text-gray-500">GPT Store</th>
                    <th className="px-6 py-3 text-center text-sm font-medium text-gray-500">Anthropic Hub</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  <tr>
                    <td className="px-6 py-4 text-sm text-gray-900">Vendor Neutral</td>
                    <td className="px-6 py-4 text-center text-green-600">✓</td>
                    <td className="px-6 py-4 text-center text-red-600">✗</td>
                    <td className="px-6 py-4 text-center text-red-600">✗</td>
                  </tr>
                  <tr>
                    <td className="px-6 py-4 text-sm text-gray-900">A2A Protocol Support</td>
                    <td className="px-6 py-4 text-center text-green-600">✓</td>
                    <td className="px-6 py-4 text-center text-red-600">✗</td>
                    <td className="px-6 py-4 text-center text-yellow-600">Limited</td>
                  </tr>
                  <tr>
                    <td className="px-6 py-4 text-sm text-gray-900">Cross-Platform Discovery</td>
                    <td className="px-6 py-4 text-center text-green-600">✓</td>
                    <td className="px-6 py-4 text-center text-red-600">✗</td>
                    <td className="px-6 py-4 text-center text-red-600">✗</td>
                  </tr>
                  <tr>
                    <td className="px-6 py-4 text-sm text-gray-900">Independent Trust Layer</td>
                    <td className="px-6 py-4 text-center text-green-600">✓</td>
                    <td className="px-6 py-4 text-center text-red-600">✗</td>
                    <td className="px-6 py-4 text-center text-red-600">✗</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      {/* Process Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Agent Discovery Made Simple
            </h2>
            <p className="text-xl text-gray-600">
              Three steps to connect your agents to the global agent network
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <DocumentCheckIcon className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">1. Register & Verify</h3>
              <p className="text-gray-600">
                Register your agent with A2A descriptors and complete independent verification - no vendor control.
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <GlobeAltIcon className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">2. Discover Across Ecosystems</h3>
              <p className="text-gray-600">
                Search agents from all frameworks - LangChain, AutoGPT, OpenAI, Anthropic, and custom builds.
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <ChatBubbleLeftRightIcon className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">3. Orchestrate & Connect</h3>
              <p className="text-gray-600">
                Enable true cross-vendor agent collaboration with standardized A2A protocols and session management.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-indigo-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center text-white">
            <div>
              <div className="text-4xl font-bold mb-2">∞</div>
              <div className="text-xl opacity-90">Cross-Vendor Compatibility</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">100%</div>
              <div className="text-xl opacity-90">Open Source Standards</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">0</div>
              <div className="text-xl opacity-90">Vendor Lock-in</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-12">
            <SparklesIcon className="h-12 w-12 text-blue-600 mx-auto mb-6" />
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Join the Open Agent Network
            </h2>
            <p className="text-xl text-gray-600 mb-8">
              Be part of the vendor-neutral infrastructure that will connect the next generation of AI agents
            </p>
            <Link
              to="/login"
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-all duration-200 transform hover:scale-105 shadow-lg inline-block"
            >
              Start Building the Future
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="flex justify-center items-center mb-4">
              <RocketLaunchIcon className="h-8 w-8 text-blue-400 mr-3" />
              <h3 className="text-2xl font-bold">ParkBench</h3>
            </div>
            <p className="text-gray-400 mb-4">
              The Universal Agent Discovery Network - Vendor Neutral • Open Standards • Cross-Platform
            </p>
            <div className="text-sm text-gray-500">
              © 2024 ParkBench Platform. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage; 