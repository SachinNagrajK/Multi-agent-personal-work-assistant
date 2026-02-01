# Quick Start Guide - AI Workspace Assistant

## 🚀 Fast Setup (5 Minutes)

### Step 1: Configure Environment

```bash
cd backend
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
OPENAI_API_KEY=sk-your-key-here
PINECONE_API_KEY=your-pinecone-key
PINECONE_HOST=https://workspace-memory-xxxxx.svc.environment.pinecone.io
LANGCHAIN_API_KEY=your-langsmith-key
SECRET_KEY=your-secret-key-minimum-32-chars
```

**Note:** Get Pinecone host from: https://app.pinecone.io → Your Index → Host URL

### Step 2: Install Backend Dependencies

```bash
# In backend directory
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Step 3: Install Frontend Dependencies

```bash
# In frontend directory
cd frontend
npm install
```

### Step 4: Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 5: Open in Browser

Navigate to: http://localhost:5173

## 🎬 Demo Scenarios

### 1. Morning Startup Workflow
- Click "Morning Startup" in Quick Actions
- Watch agents:
  - Triage your emails by priority
  - Prepare for today's meetings  
  - Prioritize your tasks
  - Generate daily briefing

### 2. Email Triage
- Click "Email Triage"
- Agents will:
  - Analyze all emails
  - Draft responses for urgent ones
  - Extract action items
  - Flag items needing approval

### 3. Context Switch
- Click "Context Switch"
- Enter project name: "Project Phoenix"
- Agent pulls:
  - Related emails
  - Meeting notes
  - Tasks and documents
  - Summary of where you left off

### 4. Meeting Prep
- Click "Meeting Prep"
- Agent prepares:
  - Meeting context
  - Suggested agenda
  - Action items from last time
  - Relevant documents

## 📊 Viewing Results

1. **Dashboard** (center): Shows prioritized emails, meetings, and tasks
2. **Agent Activity** (right): Real-time agent actions and status
3. **Quick Actions** (left): Launch workflows

## 🔍 Observability with LangSmith

1. Go to https://smith.langchain.com
2. Select your project: "workspace-assistant"
3. View:
   - Agent execution traces
   - Token usage per agent
   - Latency metrics
   - Decision reasoning

## 🛡️ Guardrails in Action

The system automatically:
- ✅ Detects PII in emails
- ✅ Validates calendar changes
- ✅ Checks for sensitive content
- ✅ Requires approval for critical actions

## 💡 Key Features to Showcase

1. **Multi-Agent Coordination**: 6 specialized agents working together
2. **Human-in-Loop**: Approval workflows for sensitive actions
3. **Memory Management**: Pinecone stores and retrieves context
4. **Real-time Updates**: WebSocket shows live agent activity
5. **Guardrails**: Safety checks at every step
6. **LangSmith Monitoring**: Complete observability

## 🎯 For the HP IQ Demo

**Opening Statement:**
> "This is a production-ready multi-agent system that demonstrates agent orchestration, tool use, memory management, and human-in-loop workflows. It's built specifically for workplace productivity - exactly the kind of AI-powered solutions HP IQ is building."

**Key Points to Highlight:**
1. **Edge-Cloud Architecture**: Local preprocessing, cloud AI processing
2. **Agent Orchestration**: LangGraph coordinates 6 specialized agents
3. **Tool Use**: Each agent has specific tools (APIs, databases, search)
4. **Memory**: Pinecone vector store for context and learning
5. **Guardrails**: Safety and privacy checks built-in
6. **Monitoring**: LangSmith tracks everything for production debugging

**Demo Flow (30 seconds):**
1. Click "Morning Startup"
2. Show real-time agent activity feed
3. Point out specific agents (Email, Calendar, Task)
4. Show results in dashboard
5. Open LangSmith to show traces

## 🐛 Troubleshooting

**Backend won't start:**
- Check `.env` file has all required keys
- Ensure Python 3.11+ is installed
- Try: `pip install -r requirements.txt --upgrade`

**Frontend won't start:**
- Delete `node_modules` and run `npm install` again
- Check Node.js version (18+)

**No agent activity showing:**
- Check browser console for WebSocket errors
- Ensure backend is running on port 8000
- Check CORS settings in backend config

**Pinecone errors:**
- Verify Pinecone API key is correct
- Check Pinecone dashboard for index status
- Index creation may take a few minutes on first run

## 📦 Docker Deployment (Optional)

```bash
# Build and run everything
docker-compose up --build

# Access at http://localhost:5173
```

## 🎓 Understanding the Code

**Backend Structure:**
```
backend/
├── agents/          # Individual agent implementations
├── config.py        # Settings and configuration
├── models.py        # Pydantic models
├── orchestrator.py  # LangGraph workflow
├── memory.py        # Pinecone integration
├── guardrails.py    # Safety checks
└── main.py          # FastAPI application
```

**Key Files to Review:**
- `orchestrator.py`: Multi-agent workflow logic
- `agents/email_agent.py`: Example agent implementation
- `guardrails.py`: Safety and validation
- `memory.py`: Vector memory management

## 🚀 Next Steps

1. **Add Real Integrations**: Connect Gmail API, Google Calendar
2. **Enhance Agents**: Add more sophisticated reasoning
3. **Custom Workflows**: Create domain-specific workflows
4. **Deploy**: Use Docker + Kubernetes for production
5. **Scale**: Add message queue for async processing

## 💬 Questions During Demo?

**"How do you handle errors?"**
- Each agent has try-catch with fallbacks
- Failed actions logged to LangSmith
- Guardrails prevent invalid operations

**"How does memory work?"**
- Pinecone stores embeddings of all work items
- Semantic search retrieves relevant context
- Learns patterns over time

**"Can this scale?"**
- Yes! Async FastAPI + message queues
- Agents can run in parallel
- Pinecone handles millions of vectors

**"What about privacy?"**
- Guardrails detect and redact PII
- Sensitive data can stay on-device
- Configurable data retention policies

Good luck with your demo! 🎉
