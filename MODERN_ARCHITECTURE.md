# Modern Multi-Agent Architecture Plan

## Overview
Building a production-ready multi-agent system using latest LangGraph patterns with:
- ReAct style agents that can call each other
- Human-in-the-loop for sensitive actions
- Guardrails for safety
- Context tracking and auto-summarization
- Rate limiting
- Loop prevention between agents

## Architecture Components

### 1. Agent Communication Pattern (ReAct Multi-Agent)

```python
# Each agent is a LangGraph StateGraph
# Agents can delegate to other agents through the orchestrator
# No direct agent-to-agent calls (prevents loops)

Orchestrator (Router)
    ├─> Email Agent
    ├─> Calendar Agent
    ├─> Task Agent
    ├─> Context Agent
    ├─> Meeting Agent
    └─> Document Agent

Flow:
1. User request → Orchestrator
2. Orchestrator routes to appropriate agent
3. Agent processes and may request delegation
4. Orchestrator handles delegation (checks for loops)
5. Results aggregated and returned
```

### 2. State Management

```python
# Global workspace state
class WorkspaceState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    current_agent: str
    delegation_history: list[str]  # Track agent calls
    context_summary: str
    context_length: int
    requires_human_approval: bool
    guardrails_triggered: list[str]
    rate_limit_status: dict[str, int]
```

### 3. Core Features Implementation

#### A. Human-in-the-Loop
```python
# Implemented in sensitive operations:
- Email sending
- Calendar event creation/deletion
- File modifications
- Large batch operations

def human_approval_node(state):
    # Show action details
    # Get user approval
    # Continue or cancel
```

#### B. Guardrails
```python
# Multiple guardrail layers:
1. Content guardrails (sensitive data detection)
2. Action guardrails (prevent dangerous operations)
3. Rate limit guardrails (API quota management)
4. Cost guardrails (LLM token limits)

def guardrails_node(state):
    # Check all guardrail conditions
    # Trigger warnings or blocks
```

#### C. Context Tracking & Summarization
```python
# Auto-summarize when context > threshold

class ContextTracker:
    threshold = 10000  # characters
    
    def check_length(self, state):
        if state["context_length"] > self.threshold:
            return "summarize"
        return "continue"
    
    def summarize_context(self, state):
        # Use LLM to create concise summary
        # Keep only recent critical messages
        # Store full history in database
```

#### D. Loop Prevention
```python
# Track delegation path
# Prevent A → B → A cycles

def check_loop(state):
    history = state["delegation_history"]
    current = state["current_agent"]
    
    # Don't allow agent to call itself
    if history and history[-1] == current:
        return False
    
    # Don't allow A → B → A pattern
    if len(history) >= 2 and history[-2] == current:
        return False
    
    return True
```

#### E. Rate Limiting
```python
# Track API calls per agent per time window

class RateLimiter:
    limits = {
        "gmail": 100,  # per hour
        "calendar": 50,
        "openai": 1000  # tokens per minute
    }
    
    def check_limit(self, service: str) -> bool:
        # Check current usage
        # Allow or block based on limits
        # Implement exponential backoff
```

### 4. Agent Architecture

Each agent follows this pattern:

```python
# State
class AgentState(TypedDict):
    messages: list[BaseMessage]
    tools_used: list[str]
    requires_approval: bool
    delegation_request: Optional[str]

# Nodes
- agent_node: Main LLM reasoning
- tool_node: Execute tools
- approval_node: Human review
- guardrails_node: Safety checks
- delegation_node: Request other agents

# Graph
StateGraph(AgentState)
    .add_node("agent", agent_node)
    .add_node("tools", tool_node)
    .add_node("approval", approval_node)
    .add_node("guardrails", guardrails_node)
    .add_conditional_edges(...)
```

### 5. Orchestrator Pattern

```python
# Master graph that coordinates all agents

class OrchestratorState(TypedDict):
    messages: list[BaseMessage]
    current_agent: str
    delegation_stack: list[str]
    global_context: dict
    
# Router logic
def route_to_agent(state):
    # Analyze user request
    # Check delegation history (prevent loops)
    # Route to appropriate agent
    # Or aggregate if multiple agents needed

# Parallel execution when possible
def parallel_execution(state):
    # Use Send API for independent tasks
    # E.g., check email + calendar simultaneously
```

### 6. Tools Organization

```python
# Real Google API Tools
gmail_tools = [
    gmail_read_recent,
    gmail_send_email,
    gmail_search,
    gmail_get_unread_count,
    gmail_mark_as_read,
    gmail_add_label,
    gmail_get_email_body
]

calendar_tools = [
    calendar_list_events,
    calendar_create_event,
    calendar_find_free_slots,
    calendar_update_event,
    calendar_delete_event,
    calendar_get_today_schedule
]

# Context tools
context_tools = [
    summarize_context,
    search_context,
    track_project
]

# Communication tools
communication_tools = [
    delegate_to_agent,  # Request help from another agent
    notify_user,
    request_approval
]
```

## Implementation Plan

### Phase 1: Rebuild Individual Agents (Current)
- [x] Gmail tools working
- [x] Calendar tools working
- [IN PROGRESS] Email agent with modern patterns
- [ ] Calendar agent
- [ ] Task agent
- [ ] Context agent
- [ ] Meeting agent
- [ ] Document agent

### Phase 2: Implement Core Features
- [ ] Context summarization tool
- [ ] Human-in-loop nodes
- [ ] Guardrails system
- [ ] Rate limiter
- [ ] Loop detection

### Phase 3: Build Orchestrator
- [ ] Routing logic
- [ ] Delegation system
- [ ] Parallel execution with Send API
- [ ] Global state management

### Phase 4: Integration & Testing
- [ ] Connect all agents to orchestrator
- [ ] Test multi-agent workflows
- [ ] Test loop prevention
- [ ] Test rate limiting
- [ ] Test human approval flows

### Phase 5: Production Features
- [ ] Checkpointing (persistence)
- [ ] LangSmith tracing
- [ ] Error recovery
- [ ] Performance optimization

## Key Design Decisions

1. **No Direct Agent-to-Agent Calls**: All communication through orchestrator prevents loops
2. **Tool-First Approach**: Agents use `.bind_tools()` for structured tool calling
3. **Stateful Graphs**: Each agent maintains its own state, orchestrator has global state
4. **Approval Gates**: Sensitive operations always require human approval
5. **Context Management**: Auto-summarization prevents context overflow
6. **Rate Limiting**: Prevent API quota exhaustion
7. **Guardrails**: Multiple layers of safety checks

## Example Flow

```
User: "Check my emails and schedule meetings for action items"

1. Orchestrator receives request
2. Routes to Email Agent
3. Email Agent:
   - Calls gmail_read_recent
   - Analyzes emails with LLM
   - Finds action items requiring meetings
   - Requests delegation to Calendar Agent
4. Orchestrator checks loop (OK)
5. Routes to Calendar Agent with context
6. Calendar Agent:
   - Checks free slots
   - Proposes meeting times
   - Requests approval (human-in-loop)
7. User approves
8. Calendar Agent creates events
9. Results aggregated
10. Response to user with summary
```

## Next Steps

1. ✅ Complete email agent modernization
2. Create context summarization tool
3. Build guardrails system
4. Implement rate limiter
5. Rebuild calendar agent
6. Build orchestrator with routing
7. Test multi-agent workflows

---

**Philosophy**: Each agent is autonomous but coordinated. The orchestrator acts as a smart router and prevents chaos. Human stays in control for important decisions.
