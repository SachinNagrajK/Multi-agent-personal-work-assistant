# Modern Multi-Agent System - Implementation Plan

## Research Findings

### Modern LangGraph Patterns (2024-2026)
Based on official LangChain/LangGraph documentation and examples:

1. **State Management**:
   - Use `TypedDict` with `Annotated` fields
   - Custom reducers (e.g., `add_messages`) for list operations
   - State channels for communication between nodes

2. **Graph Structure**:
   - `StateGraph` with nodes and edges
   - Conditional edges for routing decisions
   - `Send` API for orchestrator-worker patterns
   - START and END virtual nodes

3. **Tools**:
   - Use `@tool` decorator for custom tools
   - `bind_tools()` to attach tools to LLM
   - `ToolNode` for prebuilt tool execution
   - Tool messages in conversation flow

4. **Modern Features**:
   - `with_structured_output()` for Pydantic schemas (already added ✅)
   - `RunnableCallable` for async functions
   - `post_model_hook` for validation/guardrails
   - Context schema with `Runtime[Context]`
   - Checkpointing for persistence
   - Streaming support

5. **No "@before_agent" or Middleware in LangGraph Core**:
   - NOT a feature in LangGraph itself
   - Middleware exists at HTTP/deployment level (not agent level)
   - Use `post_model_hook` instead for post-processing
   - Use conditional edges for pre-processing

## Current Project Status

### What Works ✅:
- Latest LangChain 0.3.25 installed in venv
- Email agent using structured outputs
- Backend structure with FastAPI
- Frontend React app
- 18 tool stubs created
- Pinecone configured

### What Needs Fixing ❌:
1. **All tools are mocks** - Need real API integrations
2. **No proper LangGraph patterns** - Using old approach
3. **Agents don't use bind_tools()** - Tools not properly integrated
4. **No state management** - Not using StateGraph properly
5. **Missing Google API integrations** - No Gmail, Calendar, Drive

## Implementation Roadmap

### Phase 1: Google API Setup (Day 1 - Today)
**Goal**: Get real Google services working

1. Set up Google Cloud Project
   - Enable Gmail API
   - Enable Google Calendar API
   - Enable Google Drive API
   - Create OAuth 2.0 credentials
   - Download credentials.json

2. Install Google Client Libraries
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2
   pip install google-api-python-client
   ```

3. Create OAuth Flow
   - Token storage
   - Refresh token handling
   - User consent screen

4. Test Basic Operations
   - Read emails from Gmail
   - Create calendar event
   - List files from Drive

### Phase 2: Real Tool Implementation (Day 2)
**Goal**: Replace mock tools with real Google API calls

1. **Gmail Tools**:
   - `GmailReadTool` - Fetch emails with filters
   - `GmailSendTool` - Send emails with attachments
   - `GmailSearchTool` - Search email content
   - `GmailLabelTool` - Apply labels/organize

2. **Calendar Tools**:
   - `CalendarListTool` - Get events
   - `CalendarCreateTool` - Create events
   - `CalendarUpdateTool` - Modify/cancel events
   - `CalendarFindSlotsTo` - Find free time slots

3. **Drive Tools**:
   - `DriveListTool` - List files/folders
   - `DriveReadTool` - Read document content
   - `DriveSearchTool` - Search across files
   - `DriveShareTool` - Manage permissions

4. Keep Web Tools:
   - Tavily search (already has API key)
   - Web scraper (works without API)

### Phase 3: Modern Agent Architecture (Day 3)
**Goal**: Rebuild agents using proper LangGraph patterns

1. **Create Proper State Schema**:
```python
from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class WorkspaceState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    emails: list[dict]
    calendar_events: list[dict]
    tasks: list[dict]
    context: dict
    current_agent: str
```

2. **Rebuild Email Agent**:
   - Use `bind_tools()` with Gmail tools
   - Proper tool calling loop
   - Structured outputs for decisions
   - Post-model hooks for validation

3. **Rebuild Calendar Agent**:
   - Use `bind_tools()` with Calendar tools
   - Conflict detection
   - Smart scheduling

4. **Rebuild Task Agent**:
   - Use `bind_tools()` with task tools
   - Priority scoring
   - Dependency tracking

5. **Rebuild Context Agent**:
   - Use `bind_tools()` with Drive/file tools
   - Context switching
   - Project summarization

### Phase 4: Modern Orchestrator (Day 4)
**Goal**: Use proper LangGraph patterns

1. **StateGraph Setup**:
```python
from langgraph.graph import StateGraph, END, START

workflow = StateGraph(WorkspaceState)
```

2. **Add Nodes**:
```python
workflow.add_node("email_agent", email_agent_node)
workflow.add_node("calendar_agent", calendar_agent_node)
workflow.add_node("task_agent", task_agent_node)
workflow.add_node("context_agent", context_agent_node)
```

3. **Conditional Routing**:
```python
def route_to_agent(state):
    # Intelligent routing based on state
    if state["emails"]:
        return "email_agent"
    elif state["calendar_events"]:
        return "calendar_agent"
    # ...
    return END

workflow.add_conditional_edges(START, route_to_agent)
```

4. **Parallel Execution**:
```python
# Use Send API for parallel workflows
from langgraph.types import Send

def fanout(state):
    return [
        Send("email_agent", {...}),
        Send("calendar_agent", {...}),
        Send("task_agent", {...})
    ]
```

5. **Checkpointing**:
```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
graph = workflow.compile(checkpointer=checkpointer)
```

### Phase 5: Testing & Refinement (Day 5)
**Goal**: Make it production-ready

1. **Test Real Workflows**:
   - Connect real Gmail account
   - Connect real Calendar
   - Test morning startup workflow
   - Test email triage with real emails
   - Test meeting prep with real calendar

2. **Add Error Handling**:
   - API rate limits
   - Token expiration
   - Network errors
   - Graceful degradation

3. **Add Guardrails**:
   - Email sending confirmation
   - Calendar event validation
   - Sensitive data protection

4. **Performance Optimization**:
   - Parallel tool calls where possible
   - Caching frequently accessed data
   - Efficient state updates

5. **Documentation**:
   - API setup guide
   - Configuration options
   - Troubleshooting

## Key Architectural Decisions

### 1. Use Real Google APIs
- No more mocks
- OAuth 2.0 for security
- Proper scopes and permissions

### 2. Modern LangGraph Patterns
- StateGraph with proper state management
- bind_tools() for all agents
- Conditional edges for routing
- Send API for parallel execution
- Checkpointing for persistence

### 3. Structured Outputs
- Already using with_structured_output() ✅
- Pydantic schemas for all LLM responses
- Type-safe throughout

### 4. Proper Tool Calling
- Tools as LangChain tools (@tool decorator)
- ToolNode for execution
- Tool messages in conversation

### 5. Post-Model Hooks
- NOT middleware (@before_agent doesn't exist)
- Use post_model_hook parameter
- Validation and guardrails

## What We're NOT Doing

❌ "@before_agent" decorator - doesn't exist in LangGraph
❌ Custom middleware at agent level - not a LangGraph pattern
❌ Mock data in production - using real APIs
❌ Old JSON parsing approach - using structured outputs
❌ Global state - using proper StateGraph

## What We ARE Doing

✅ Real Google API integrations
✅ Modern LangGraph StateGraph
✅ Proper tool calling with bind_tools()
✅ Structured outputs with Pydantic
✅ Post-model hooks for validation
✅ Checkpointing for persistence
✅ Conditional routing
✅ Parallel execution with Send API

## Next Immediate Steps

1. Stop the current broken server
2. Set up Google Cloud Project
3. Get OAuth credentials
4. Install Google client libraries
5. Test basic Gmail/Calendar access
6. Then rebuild agents properly

## Timeline

- **Day 1** (Today): Google API setup + OAuth
- **Day 2**: Real tool implementation
- **Day 3**: Modern agent architecture
- **Day 4**: Proper orchestrator with LangGraph
- **Day 5**: Testing + refinement

Your demo is tomorrow (Jan 31), so we focus on:
1. Getting real Google APIs working TODAY
2. At minimum, show real Gmail and Calendar integration
3. Even if not all features work, show REAL data

## Priority for Tomorrow's Demo

**MUST HAVE**:
1. Real Gmail integration - read actual emails
2. Real Calendar integration - show actual events  
3. At least ONE workflow working end-to-end
4. Modern LangGraph state management visible

**NICE TO HAVE**:
5. All 4 workflows working
6. Parallel execution demo
7. Checkpointing demo
8. LangSmith tracing

Let's start with Google API setup NOW!
