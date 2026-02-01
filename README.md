# 🤖 AI-Powered Multi-Agent Workspace Assistant

An intelligent personal assistant built with LangGraph and LangChain that autonomously manages emails, calendars, and tasks through natural language conversations. Features ReAct reasoning, conversation memory, and seamless Google Workspace integration.

## ✨ Key Features

### 🎯 Core Capabilities
- **Natural Language Interface**: Chat with AI to manage your entire workflow
- **Multi-Turn Conversations**: Maintains context across messages for complex task completion
- **Autonomous Task Execution**: AI analyzes requests and takes appropriate actions without constant prompting
- **Real-Time Processing**: Instant responses with live updates

### 📧 Email Management
- **Smart Triage**: AI analyzes and prioritizes incoming emails
- **Email Search**: Natural language queries to find specific messages
- **Read & Summarize**: Get quick summaries of recent emails
- **Send Emails**: Compose and send emails through conversation

### 📅 Calendar Intelligence
- **Smart Scheduling**: "Schedule a meeting with john@example.com in 1 hour for 30 minutes"
- **Free Slot Finding**: Automatically identifies available time slots
- **Event Management**: View, create, and manage calendar events
- **Multi-Turn Scheduling**: Provide details across multiple messages

### 🧠 Advanced AI Features
- **ReAct Reasoning**: Uses LangGraph's ReAct pattern for intelligent decision-making
- **Conversation Memory**: Remembers entire conversation history for context-aware responses
- **Tool Orchestration**: Autonomously selects and chains multiple tools to complete tasks
- **Guardrails**: Built-in safety checks to protect sensitive information

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│         Frontend (React + Vite)                 │
│  ┌──────────────┐  ┌───────────────────────┐  │
│  │ Chat UI      │  │ Quick Actions Panel   │  │
│  │ - Chat       │  │ - Triage Emails      │  │
│  │ - History    │  │ - Daily Brief        │  │
│  └──────────────┘  └───────────────────────┘  │
└─────────────────────────────────────────────────┘
                     ↕ REST API
┌─────────────────────────────────────────────────┐
│      Backend (FastAPI + Python)                 │
│  ┌───────────────────────────────────────────┐ │
│  │   WorkspaceAssistant (orchestrator)       │ │
│  │   - Conversation Memory                   │ │
│  │   - LangGraph ReAct Agent                 │ │
│  └───────────────────────────────────────────┘ │
│                     ↕                           │
│  ┌───────────────────────────────────────────┐ │
│  │         Tool Integration Layer            │ │
│  │  ┌─────────────┐  ┌──────────────────┐  │ │
│  │  │ Gmail Tools │  │ Calendar Tools   │  │ │
│  │  │ - Search    │  │ - List Events    │  │ │
│  │  │ - Read      │  │ - Create Event   │  │ │
│  │  │ - Send      │  │ - Find Slots     │  │ │
│  │  └─────────────┘  └──────────────────┘  │ │
│  └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
                     ↕
┌─────────────────────────────────────────────────┐
│      External Services                          │
│  ┌──────────────┐  ┌──────────────────────┐   │
│  │ OpenAI GPT-4 │  │ Google Workspace APIs│   │
│  │ (LangChain)  │  │ - Gmail API          │   │
│  └──────────────┘  │ - Calendar API       │   │
│                     └──────────────────────┘   │
└─────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**: Backend runtime
- **Node.js 18+**: Frontend development
- **OpenAI API Key**: For GPT-4 LLM
- **Google Cloud Project**: With Gmail & Calendar APIs enabled
- **LangSmith Account** (Optional): For monitoring and tracing

### 1. Clone Repository

```bash
git clone git@github.com:SachinNagrajK/Multi-agent-personal-work-assistant.git
cd Multi-agent-personal-work-assistant
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

**Configure .env:**
```env
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_API_KEY=your_langsmith_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=workspace-assistant
```

**Setup Google Cloud Credentials:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API and Google Calendar API
4. Create OAuth 2.0 credentials (Desktop App)
5. Download credentials and save as `backend/credentials.json`

**Run Backend:**
```bash
python -m uvicorn main:app --reload --port 8000
```

Backend will start on: `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will start on: `http://localhost:5173`

### 4. First Run - Google Authentication

1. Open browser and go to `http://localhost:5173`
2. On first API call, you'll be prompted to authenticate with Google
3. Follow OAuth flow to grant permissions
4. Credentials will be cached in `backend/token.pickle`

## 📖 Usage Examples

### Email Triage
```
User: "Triage my recent emails"
AI: [Analyzes emails and provides prioritized summary]
```

### Meeting Scheduling (Multi-Turn)
```
User: "Schedule a meeting with john@example.com"
AI: "What time would you like to schedule the meeting?"
User: "Tomorrow at 2pm for 1 hour"
AI: ✅ Event created successfully!
    Title: Meeting with john@example.com
    When: 2026-02-02T14:00:00 to 2026-02-02T15:00:00
```

### Complex Scheduling with Relative Time
```
User: "Schedule a meeting after 30 minutes with sachin@gmail.com"
AI: "How long should the meeting be?"
User: "30 minutes"
AI: [Calculates current time + 30 minutes, schedules meeting]
```

### Daily Briefing
```
Click "Daily Brief" button → AI provides comprehensive summary of:
- Urgent emails requiring attention
- Today's calendar events
- Suggested priorities
```

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | Async REST API framework |
| **LangGraph** | Multi-agent orchestration with ReAct pattern |
| **LangChain** | LLM integration and tool binding |
| **OpenAI GPT-4** | Language model for reasoning |
| **Google APIs** | Gmail and Calendar integration |
| **Uvicorn** | ASGI server |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | UI framework |
| **Vite** | Build tool and dev server |
| **TailwindCSS** | Styling |
| **Fetch API** | Backend communication |

### AI Components
- **ReAct Agent**: LangGraph's ToolNode and tools_condition for agent loop
- **Conversation Memory**: Full history maintained in WorkspaceAssistant class
- **Tool Binding**: Direct LLM-to-tool integration via bind_tools()
- **Guardrails**: Sensitive data detection and filtering

## 📁 Project Structure

```
multi-agent-langgraph/
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── orchestrator_react.py      # LangGraph ReAct agent (MAIN)
│   ├── config.py                  # Configuration settings
│   ├── guardrails.py              # Safety and validation
│   ├── models.py                  # Pydantic models
│   ├── demo_data.py               # Demo data generators
│   ├── tools/
│   │   ├── gmail_tools.py         # Gmail API integration
│   │   └── calendar_tools.py      # Calendar API integration
│   ├── requirements.txt           # Python dependencies
│   └── credentials.json           # Google OAuth (DO NOT COMMIT)
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterfaceNew.jsx    # Main chat UI
│   │   │   ├── QuickActions.jsx        # Action buttons
│   │   │   └── CalendarPanel.jsx       # Calendar display
│   │   ├── App.jsx                     # Root component
│   │   └── main.jsx                    # Entry point
│   ├── package.json               # Node dependencies
│   └── vite.config.js             # Vite configuration
│
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## 🔒 Security & Best Practices

### Sensitive Data Protection
- **Never commit** `credentials.json`, `token.pickle`, or `.env` files
- All sensitive files are in `.gitignore`
- Guardrails system blocks credit cards, SSNs, passwords in user input
- Email addresses are allowed for legitimate scheduling operations

### API Key Management
- Store all API keys in `.env` file
- Use environment variables for configuration
- Rotate keys regularly

### Google OAuth
- OAuth tokens automatically refresh when expired
- Tokens stored securely in `token.pickle`
- Minimal scope permissions requested

## 🎯 Features Breakdown

### 8 Integrated Tools

1. **get_current_time**: Returns current datetime for time calculations
2. **gmail_read_recent**: Reads recent emails with optional filters
3. **gmail_send_email**: Sends emails with cc/bcc support
4. **gmail_search**: Searches emails by query
5. **calendar_get_today_schedule**: Gets today's events
6. **calendar_list_events**: Lists upcoming events
7. **calendar_create_event**: Creates calendar events with attendees
8. **calendar_find_free_slots**: Finds available time slots

### Conversation Memory System
- **Full History Retention**: Every message stored in conversation_messages list
- **Context Passing**: Complete history passed to LLM on every request
- **Multi-Turn Support**: Agent remembers details from previous messages
- **Session Isolation**: Quick action buttons clear history for fresh context

### ReAct Agent Behavior
```python
System Prompt Includes:
- "Review ALL previous messages in the conversation"
- "DO NOT ask for clarification if you have enough information"
- "When scheduling, FIRST call get_current_time"
- "Calculate EXACT start and end times in ISO format"
```

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check for port conflicts
netstat -ano | findstr :8000
```

### Google API Authentication Issues
1. Ensure `credentials.json` is in `backend/` directory
2. Delete `token.pickle` and re-authenticate
3. Check API is enabled in Google Cloud Console
4. Verify OAuth consent screen is configured

### Frontend Connection Issues
- Verify backend is running on port 8000
- Check browser console for CORS errors
- Ensure fetch URLs point to `http://localhost:8000`

### Agent Not Working Properly
- Check `OPENAI_API_KEY` is valid in `.env`
- Verify LangSmith tracing is working (check logs)
- Review agent logs in terminal for errors

## 📊 Monitoring & Debugging

### LangSmith Integration
All agent interactions are traced via LangSmith:
- View decision-making process
- Track tool calls and responses
- Monitor token usage
- Debug failures

Access at: https://smith.langchain.com/

### Backend Logging
Extensive logging in terminal:
```
==> 🎯 CHAT ENDPOINT CALLED!
==> User message: 'schedule a meeting...'
Initializing ReAct agent...
✓ Agent ready!
```

## 🚧 Known Limitations

- Calendar events use America/New_York timezone (can be configured)
- Email sending requires OAuth approval for production use
- First authentication requires manual browser interaction
- Large email/calendar operations may take time

## 🔮 Future Enhancements

- [ ] Add task management agent
- [ ] Implement document processing
- [ ] Multi-calendar support
- [ ] Email template suggestions
- [ ] Smart meeting summaries
- [ ] Integration with Slack/Teams
- [ ] Voice interface
- [ ] Mobile app

## 📄 License

MIT License - feel free to use this project for learning or commercial purposes.

## 👨‍💻 Author

**Sachin Nagraj Kulkarni**

## 🙏 Acknowledgments

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph) - Multi-agent orchestration
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [OpenAI](https://openai.com/) - GPT-4 language model
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python API framework
- [React](https://react.dev/) - Frontend library

---

**⭐ Star this repo if you find it useful!**
