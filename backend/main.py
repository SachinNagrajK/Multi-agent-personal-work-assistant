from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Dict, Any
import json
import uuid

from config import settings
from models import (
    WorkflowRequest,
    WorkflowResponse,
    ApprovalRequest,
    DashboardData,
    AgentAction
)
# from orchestrator import orchestrator  # Old orchestrator - commented out
# from orchestrator_modern import WorkspaceOrchestrator  # BROKEN - doesn't work properly
from orchestrator_react import WorkspaceAssistant  # NEW PROPER REACT AGENT
# from orchestrator_simple import SimpleOrchestrator  # Basic version
from demo_data import demo_data
from guardrails import guardrails
from context_manager import context_manager

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()

# Global orchestrator instance (initialized on first use)
modern_orchestrator = None

def get_orchestrator():
    """Lazy initialization of orchestrator."""
    global modern_orchestrator
    if modern_orchestrator is None:
        try:
            print("Initializing ReAct agent...")
            modern_orchestrator = WorkspaceAssistant()
            print("Agent ready!")
        except Exception as e:
            import traceback
            print(f"\n❌ ERROR initializing orchestrator:")
            print(traceback.format_exc())
            raise
    return modern_orchestrator


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("==> Workspace Assistant API starting...")
    print(f"LangSmith Tracing: {settings.LANGCHAIN_TRACING_V2}")
    print(f"Environment: {settings.ENVIRONMENT}")
    # Don't initialize orchestrator here - do it on first request
    print("✓ Ready to handle requests")
    yield
    # Shutdown
    print("==> Workspace Assistant API shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Workspace Assistant API",
    description="Multi-agent AI system for knowledge worker productivity",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
@app.get("/")
async def root():
    """Health check endpoint"""
    print("==> Root endpoint called")
    return {
        "status": "healthy",
        "service": "Workspace Assistant API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


@app.post("/api/test")
async def test_endpoint(request: Request):
    """Simple test endpoint to verify connection"""
    print("\n" + "="*50)
    print("==> TEST ENDPOINT CALLED!")
    body = await request.json()
    print(f"==> Received body: {body}")
    print("="*50 + "\n")
    return {"status": "success", "received": body, "message": "Backend is working!"}


@app.get("/api/demo-data")
async def get_demo_data():
    """Get demo data for testing"""
    return demo_data.get_demo_data()


@app.get("/api/dashboard")
async def get_dashboard() -> DashboardData:
    """Get dashboard data with real-time AI analysis"""
    data = demo_data.get_demo_data()
    
    # Filter for urgent/high priority items
    urgent_emails = [e for e in data["emails"] if e.get("priority") in ["urgent", "high"]][:5]
    today_meetings = data["calendar_events"][:3]
    high_priority_tasks = [t for t in data["tasks"] if t.get("priority") in ["urgent", "high"]][:5]
    
    return DashboardData(
        urgent_emails=urgent_emails,
        today_meetings=today_meetings,
        high_priority_tasks=high_priority_tasks,
        recent_activity=[],
        pending_approvals=[],
        current_context=None
    )


@app.post("/api/workflow/execute")
async def execute_workflow(request: WorkflowRequest) -> WorkflowResponse:
    """Execute a workflow"""
    
    # Get demo data
    data = demo_data.get_demo_data()
    
    # Prepare workflow request
    workflow_data = {
        "workflow_type": request.workflow_type,
        "parameters": request.parameters,
        "user_id": "demo_user",
        "emails": data["emails"],
        "calendar_events": data["calendar_events"],
        "tasks": data["tasks"],
        "documents": data["documents"]
    }
    
    try:
        # Execute workflow using modern orchestrator
        workflow_description = f"{request.workflow_type}: {json.dumps(request.parameters)}"
        orchestrator = get_orchestrator()
        result = orchestrator.process_request(workflow_description)
        
        # Broadcast progress to websocket clients
        await manager.broadcast({
            "type": "workflow_progress",
            "workflow_id": str(uuid.uuid4()),
            "status": "completed",
            "response": result
        })
        
        return WorkflowResponse(
            workflow_id=str(uuid.uuid4()),
            status="completed",
            results={"response": result},
            agent_actions=[],
            requires_approval=False,
            approval_items=[]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/workflow/approve")
async def approve_workflow(request: ApprovalRequest):
    """Approve or reject a workflow action"""
    
    # In a real implementation, this would update the workflow state
    # and potentially trigger follow-up actions
    
    return {
        "workflow_id": request.workflow_id,
        "approval_id": request.approval_id,
        "status": "approved" if request.approved else "rejected",
        "message": "Action processed successfully"
    }


# ============================================================================
# MODERN AI ENDPOINTS - Using LangGraph orchestrator with real Google APIs
# ============================================================================

@app.post("/api/ai/chat")
async def ai_chat(request: Request):
    """
    Natural language chat with AI assistant.
    Uses modern orchestrator with real Gmail/Calendar.
    """
    print("\n" + "="*60)
    print("==> 🎯 CHAT ENDPOINT CALLED!")
    print(f"==> Request method: {request.method}")
    print(f"==> Request URL: {request.url}")
    print(f"==> Request headers: {dict(request.headers)}")
    
    body = await request.json()
    print(f"==> Request body: {body}")
    user_message = body.get("message", "")
    print(f"==> User message: '{user_message}'")
    print("="*60 + "\n")
    
    if not user_message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    try:
        # Process through modern orchestrator
        orchestrator = get_orchestrator()
        response = orchestrator.process_request(user_message)
        
        # Get session stats
        stats = orchestrator.get_session_stats()
        
        return {
            "response": response,
            "stats": stats,
            "timestamp": str(uuid.uuid4())
        }
    except Exception as e:
        import traceback
        print(f"\n❌ ERROR in chat endpoint:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai/triage")
async def ai_triage():
    """
    AI-powered email triage using real Gmail.
    Returns prioritized email analysis.
    """
    try:
        orchestrator = get_orchestrator()
        orchestrator.clear_conversation()  # Start fresh
        response = orchestrator.process_request(
            "Triage my recent emails and tell me what needs immediate attention"
        )
        
        return {
            "response": response,
            "timestamp": str(uuid.uuid4())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai/daily-brief")
async def daily_brief():
    """
    Generate AI-powered daily briefing.
    Combines emails, calendar, and tasks into intelligent summary.
    """
    try:
        orchestrator = get_orchestrator()
        orchestrator.clear_conversation()  # Start fresh
        response = orchestrator.process_request(
            "Give me a comprehensive daily briefing: check my emails for urgent items, "
            "show my calendar for today, and suggest priorities"
        )
        
        return {
            "response": response,
            "generated_at": str(uuid.uuid4())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai/context-summary")
async def context_summary():
    """Get current context summary and statistics."""
    try:
        return {
            "total_messages": len(context_manager.full_history),
            "context_length": context_manager.calculate_context_length(context_manager.full_history),
            "is_summarized": len(context_manager.summarized_context) > 0,
            "summary_length": len(context_manager.summarized_context) if context_manager.summarized_context else 0
        }
    except Exception as e:
        print(f"Context summary error: {e}")
        return {
            "total_messages": 0,
            "context_length": 0,
            "is_summarized": False,
            "summary_length": 0
        }


@app.get("/api/ai/guardrails-status")
async def guardrails_status():
    """Get current guardrails status and safety metrics."""
    try:
        status = guardrails.get_status_report()
        return {
            "status": status,
            "total_checks": len(guardrails.action_history),
            "triggered": len(guardrails.triggered_guardrails)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/search-context")
async def search_context(request: Request):
    """Search through conversation history."""
    body = await request.json()
    query = body.get("query", "")
    
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    try:
        from context_manager import search_context_history
        result = search_context_history.invoke({"query": query})
        return {"results": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/emails")
async def get_emails():
    """Get all emails"""
    return demo_data.generate_emails()


@app.get("/api/calendar")
async def get_calendar():
    """Get calendar events from Google Calendar"""
    try:
        from tools.calendar_tools import get_calendar_service
        from datetime import datetime, timedelta
        
        service = get_calendar_service()
        if not service:
            print("Failed to connect to Google Calendar, using demo data")
            return demo_data.generate_calendar_events()
        
        # Get current time and next 30 days
        now = datetime.utcnow().isoformat() + 'Z'
        end_time = (datetime.utcnow() + timedelta(days=30)).isoformat() + 'Z'
        
        # Call the Calendar API
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=end_time,
            maxResults=20,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return []
        
        # Format events for frontend
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            formatted_event = {
                'title': event.get('summary', 'No Title'),
                'summary': event.get('summary', 'No Title'),
                'description': event.get('description', ''),
                'start': start,
                'end': end,
                'date': start.split('T')[0] if 'T' in start else start,
                'location': event.get('location', ''),
                'attendees': event.get('attendees', []),
                'id': event['id'],
                'htmlLink': event.get('htmlLink', '')
            }
            formatted_events.append(formatted_event)
        
        return formatted_events
        
    except Exception as e:
        print(f"Calendar error: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to demo data if there's an error
        return demo_data.generate_calendar_events()


@app.get("/api/tasks")
async def get_tasks():
    """Get tasks"""
    return demo_data.generate_tasks()


@app.get("/api/documents")
async def get_documents():
    """Get documents"""
    return demo_data.generate_documents()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "message": "WebSocket connection established"
        })
        
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Echo back for now (can be extended for bidirectional communication)
            await websocket.send_json({
                "type": "echo",
                "data": message
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
