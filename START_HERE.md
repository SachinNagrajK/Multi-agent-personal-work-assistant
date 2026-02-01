# 🚀 Quick Start Commands

## Starting the Application

### Option 1: Start Both Servers (Recommended)

**Terminal 1 - Backend:**
```powershell
cd S:\Studies\Projects\multi-agent-langgraph
.\venv\Scripts\Activate.ps1
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```powershell
cd S:\Studies\Projects\multi-agent-langgraph\frontend
npm run dev
```

### Option 2: One-Line Commands

**Backend (with venv):**
```powershell
$env:Path = "S:\Studies\Projects\multi-agent-langgraph\venv\Scripts;" + $env:Path; cd S:\Studies\Projects\multi-agent-langgraph\backend; python main.py
```

**Frontend:**
```powershell
cd S:\Studies\Projects\multi-agent-langgraph\frontend; npm run dev
```

---

## Access Points

- **Frontend UI**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger UI)

---

## Stopping the Servers

Press `Ctrl+C` in each terminal window.

---

## Testing Individual Components

### Test Backend Only:
```powershell
cd S:\Studies\Projects\multi-agent-langgraph
.\venv\Scripts\Activate.ps1
cd backend

# Test orchestrator
python test_orchestrator.py

# Test real Google APIs
python test_real_tools.py

# Test email agent
python test_modern_agent.py
```

### Test API Endpoints:
```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8000/"

# Chat endpoint
Invoke-RestMethod -Uri "http://localhost:8000/api/ai/chat" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"message": "What unread emails do I have?"}'

# Email triage
Invoke-RestMethod -Uri "http://localhost:8000/api/ai/triage"

# Daily brief
Invoke-RestMethod -Uri "http://localhost:8000/api/ai/daily-brief"

# Context summary
Invoke-RestMethod -Uri "http://localhost:8000/api/ai/context-summary"

# Guardrails status
Invoke-RestMethod -Uri "http://localhost:8000/api/ai/guardrails-status"
```

---

## Environment Variables

Make sure these are set in `backend/.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_key_here
LANGCHAIN_PROJECT=multi-agent-workspace
```

---

## Common Issues

### "Module not found" errors:
```powershell
# Activate venv first
cd S:\Studies\Projects\multi-agent-langgraph
.\venv\Scripts\Activate.ps1

# Reinstall if needed
pip install -r requirements.txt
```

### Port already in use:
```powershell
# Find process using port 8000
Get-NetTCPConnection -LocalPort 8000 | Select-Object -Property OwningProcess

# Kill it (replace PID)
Stop-Process -Id <PID> -Force
```

### Frontend won't start:
```powershell
cd S:\Studies\Projects\multi-agent-langgraph\frontend
npm install
npm run dev
```

### Google OAuth errors:
```powershell
# Delete token and re-authenticate
cd S:\Studies\Projects\multi-agent-langgraph\backend
rm token.pickle
python test_real_tools.py
# Follow OAuth flow in browser
```

---

## Quick Demo Flow

1. **Start servers** (both terminals)
2. **Open browser** to http://localhost:5173
3. **Try these in order:**
   - "What unread emails do I have?" (Shows real Gmail integration)
   - "Triage my emails by priority" (Shows AI analysis)
   - "Give me my daily brief" (Shows multi-agent coordination)
   - Click "🎯 Triage Emails" button (Shows quick actions)
4. **Show stats sidebar** (Shows context manager, guardrails)
5. **Switch to Email tab** (Shows data display)
6. **Switch to Calendar tab** (Shows calendar integration)

---

## Development Workflow

### Making Backend Changes:
1. Edit files in `backend/`
2. Server auto-reloads (uvicorn watch mode)
3. Test via browser or API calls

### Making Frontend Changes:
1. Edit files in `frontend/src/`
2. Vite hot-reloads automatically
3. Check browser for updates

### Adding New Features:
See `CREATIVE_FEATURES.md` for ideas!

---

## 📋 Checklist Before Demo

- [ ] Both servers running
- [ ] No errors in terminals
- [ ] Browser shows UI correctly
- [ ] Chat responds to messages
- [ ] Gmail connection works (check stats sidebar)
- [ ] Calendar connection works (check stats sidebar)
- [ ] Quick actions work
- [ ] Stats sidebar updates
- [ ] No CORS errors in browser console

---

## 🎯 Ready to Go!

Your interactive AI workspace assistant is ready to showcase all the modern LangGraph features! 🚀
