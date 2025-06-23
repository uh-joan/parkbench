# 🎨 ParkBench Frontend Portal - Complete Usage Guide

The ParkBench platform includes a modern React frontend with TypeScript and Tailwind CSS for managing your AI agent ecosystem.

## 🚀 Quick Start

1. **Setup Frontend:**
   ```bash
   cd frontend/parkbench-portal
   npm install
   npm start
   ```

2. **Access Portal:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:9000 (must be running)

## 📋 Main Features & Usage Examples

### 1. 📊 Dashboard (Homepage)
**URL:** http://localhost:3000/
**Purpose:** Overview of your ParkBench platform

**What you'll see:**
- System health status (API connection indicator)
- Agent statistics (total, active, verified)
- A2A session statistics (active sessions)
- Recent agent registrations
- Recent A2A session activity
- Real-time status indicators

**Example Use Case:**
Monitor your AI agent network at a glance, check system health, and see recent activity across all agents and sessions.

### 2. 🔍 Agent Discovery
**URL:** http://localhost:3000/discovery
**Purpose:** Search and explore registered AI agents

**Features:**
- Search agents by name, description, or skills
- Filter by verification status (verified/unverified)
- Filter by A2A compliance
- Filter by active status
- View detailed agent profiles
- See agent capabilities and skills

**Step-by-Step Example:**
1. Go to Discovery page
2. Use search bar: 'text generation' to find text AI agents
3. Apply filters: Select 'Verified Only' + 'A2A Compliant'
4. Click on an agent card to see full profile
5. View agent's API endpoint, skills, protocols, and A2A capabilities

**Use Cases:**
- Find agents with specific skills for your project
- Discover A2A-compliant agents for automation
- Check agent availability and verification status

### 3. 📝 Agent Registration
**URL:** http://localhost:3000/register
**Purpose:** Register new AI agents in the ParkBench network

**Registration Form Sections:**

**Basic Information:**
- Agent Name (DNS format): 'my-agent.example.com'
- Version: '1.0.0'
- Description: 'What this agent does'
- Maintainer Contact: 'admin@example.com'
- API Endpoint: 'https://api.example.com/agent'

**Capabilities:**
- Skills: 'text-generation, summarization, analysis'
- Protocols: REST, GraphQL, A2A, WebSocket, gRPC
- Input/Output Formats: JSON, XML, Plain Text
- Pricing Model: free, pay-per-use, subscription

**A2A Configuration (if A2A compliant):**
- Supported Tasks: 'summarization, translation'
- Negotiation Support: Yes/No
- Context Requirements: 'input_text, language'
- Token Budget: 10000

**Security:**
- Certificate (PEM format): Paste X.509 certificate
- Public Key: Agent's public key

**Example Registration Process:**
1. Fill Basic Information form
2. Add comma-separated skills: 'nlp, text-analysis, sentiment'
3. Select protocols: Check REST and A2A
4. If A2A compliant: Configure A2A settings
5. Paste valid X.509 certificate
6. Submit for registration
7. Receive agent ID and status

### 4. 📊 Session Monitor
**URL:** http://localhost:3000/sessions
**Purpose:** Monitor and manage A2A (Agent-to-Agent) sessions

**Features:**
- View all active A2A sessions
- Filter sessions by initiating agent
- Filter sessions by target agent
- Filter by session status (active, completed, failed)
- View session details and progress
- Real-time session status updates

**Example Workflow:**
1. Go to Sessions page to see all A2A interactions
2. Use filters to find specific agent interactions
3. Click on session to see details:
   - Initiating agent and target agent
   - Task being performed
   - Session context and parameters
   - Current status and progress
   - Start time and duration
4. Monitor session completion or errors

**Use Cases:**
- Debug A2A session issues
- Monitor agent collaboration performance
- Track task completion rates
- Analyze agent-to-agent communication patterns

### 5. ⚙️ Admin Panel
**URL:** http://localhost:3000/admin
**Purpose:** Administrative controls for platform management

**Admin Features:**

**API Key Management:**
- Generate new API keys for agents
- Set permissions (read, write, negotiate, admin)
- Set expiration times
- Revoke existing API keys
- View API key usage statistics

**Agent Management:**
- Approve/reject agent registrations
- Update agent verification status
- Deactivate problematic agents
- View detailed agent information

**System Configuration:**
- Configure platform settings
- Set rate limiting parameters
- Manage authentication policies
- View system logs and metrics

**Example Admin Tasks:**

1. **Generate API Key:**
   - Select agent: 'my-agent.example.com'
   - Set permissions: ['read', 'write', 'negotiate']
   - Set expiration: 7 days
   - Generate and copy API key

2. **Manage Agent Verification:**
   - Review pending agent registrations
   - Verify certificates manually if needed
   - Approve or reject registrations
   - Update agent status

## 🔧 Technical Details

### Frontend Architecture:
- **Framework:** React 18 with TypeScript
- **Styling:** Tailwind CSS for responsive design
- **Icons:** Heroicons for consistent UI
- **HTTP Client:** Axios for API communication
- **Routing:** React Router DOM for navigation
- **State Management:** React hooks and local state

### API Integration:
- **Base URL:** http://localhost:9000 (configured in package.json proxy)
- **Authentication:** Supports JWT tokens and API keys
- **Error Handling:** User-friendly error messages
- **Loading States:** Spinners and loading indicators
- **Real-time Updates:** Periodic data refresh

### Key File Structure:
```
frontend/parkbench-portal/src/
├── components/
│   ├── Dashboard.tsx      # Main dashboard with stats
│   ├── AgentDiscovery.tsx # Agent search and filtering
│   ├── AgentRegistration.tsx # Agent registration form
│   ├── SessionMonitor.tsx # A2A session monitoring
│   └── AdminPanel.tsx    # Admin controls
├── services/
│   └── api.ts            # API service layer
├── types/
│   └── index.ts          # TypeScript type definitions
└── App.tsx               # Main app with routing
```

## 🚀 Getting Started (Summary)

1. **Start Backend:** `cd parkbench/deployment && docker compose up -d`
2. **Start Frontend:** `cd frontend/parkbench-portal && npm install && npm start`
3. **Access Portal:** http://localhost:3000
4. **Start Exploring:** Begin with Dashboard, then try Discovery and Registration

## 💡 Pro Tips

- **Mobile Responsive:** Works on tablets and mobile devices
- **Keyboard Navigation:** Fully accessible with keyboard shortcuts
- **Real-time Updates:** Dashboard refreshes automatically
- **Form Validation:** Client-side validation with helpful error messages
- **Search Optimization:** Search supports partial matches and skill-based filtering

## 🎯 Common Workflows

### Developer Workflow:
1. **Dashboard** → Check system health
2. **Discovery** → Find existing agents with needed skills
3. **Registration** → Register your new agent
4. **Sessions** → Monitor agent interactions

### Admin Workflow:
1. **Dashboard** → Monitor overall system metrics
2. **Admin Panel** → Generate API keys and manage agents
3. **Discovery** → Verify agent registrations
4. **Sessions** → Debug any problematic interactions

The ParkBench frontend provides an intuitive interface for managing your AI agent ecosystem with enterprise-grade features and modern UX design! 🎉 