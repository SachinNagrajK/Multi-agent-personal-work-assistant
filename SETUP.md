# Setup Instructions

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- OpenAI API key
- Pinecone API key
- LangSmith API key (for monitoring)

## Backend Setup

### 1. Create Virtual Environment

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Environment

Copy the example environment file:
```powershell
copy .env.example .env
```

Edit `.env` and add your API keys:
```env
OPENAI_API_KEY=sk-your-openai-key-here
PINECONE_API_KEY=your-pinecone-key-here
PINECONE_HOST=https://workspace-memory-xxxxx.svc.environment.pinecone.io
LANGCHAIN_API_KEY=your-langsmith-key-here
PINECONE_INDEX_NAME=workspace-memory
SECRET_KEY=generate-a-secure-random-string-min-32-chars
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=workspace-assistant
```

**Important:** Pinecone requires BOTH API key AND host URL!
- Get host from: https://app.pinecone.io → Your Index → Copy host URL

**To generate SECRET_KEY:**
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Run Backend

```powershell
python main.py
```

The API will be available at: http://localhost:8000

**API Documentation:** http://localhost:8000/docs

## Frontend Setup

### 1. Install Dependencies

```powershell
cd frontend
npm install
```

### 2. Run Development Server

```powershell
npm run dev
```

The frontend will be available at: http://localhost:5173

## Verification

### Check Backend
1. Visit http://localhost:8000
2. Should see: `{"status": "healthy", ...}`

### Check Frontend
1. Visit http://localhost:5173
2. Should see the Workspace Assistant dashboard

### Check WebSocket
Open browser console and look for:
```
WebSocket connected
```

## Using the Application

### 1. Run Morning Startup Workflow
- Click "Morning Startup" button
- Watch the Agent Activity panel (right side)
- See results appear in Dashboard (center)

### 2. Monitor with LangSmith
1. Go to https://smith.langchain.com
2. Find project "workspace-assistant"
3. View agent execution traces

## Troubleshooting

### Backend Issues

**ModuleNotFoundError:**
```powershell
pip install -r requirements.txt --upgrade
```

**Pinecone Connection Error:**
- Verify API key in `.env`
- Check Pinecone dashboard: https://app.pinecone.io
- Ensure index name matches configuration

**OpenAI API Error:**
- Verify API key starts with `sk-`
- Check API quota: https://platform.openai.com/usage

### Frontend Issues

**npm install fails:**
```powershell
rm -rf node_modules
rm package-lock.json
npm install
```

**Vite errors:**
```powershell
npm install vite@latest --save-dev
```

**WebSocket connection fails:**
- Ensure backend is running on port 8000
- Check browser console for errors
- Verify CORS settings in backend

### Common Issues

**"Agent activity not showing":**
- Check browser console for WebSocket errors
- Ensure both backend and frontend are running
- Clear browser cache and reload

**"Workflow execution fails":**
- Check backend logs for errors
- Verify all API keys are correct
- Check LangSmith dashboard for detailed errors

**"Import errors in Python":**
```powershell
# Make sure virtual environment is activated
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Production Deployment

### Using Docker

```powershell
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Environment Variables for Production

Update `.env`:
```env
ENVIRONMENT=production
DEBUG=false
ALLOWED_ORIGINS=https://your-domain.com
```

## Next Steps

1. ✅ Verify all workflows execute successfully
2. ✅ Check LangSmith for agent traces
3. ✅ Test human-in-loop approvals
4. ✅ Review guardrails in action
5. ✅ Prepare demo scenarios

## Getting Help

- **Backend Errors**: Check `backend/*.log` files
- **Frontend Errors**: Open browser DevTools console
- **LangSmith**: View traces at https://smith.langchain.com

## Demo Preparation Checklist

- [ ] Backend running without errors
- [ ] Frontend loads correctly
- [ ] All workflows execute successfully
- [ ] WebSocket shows real-time updates
- [ ] LangSmith captures traces
- [ ] Demo data displays properly
- [ ] Prepared talking points
- [ ] Tested on presentation laptop/screen

Ready to impress at HP IQ! 🚀
