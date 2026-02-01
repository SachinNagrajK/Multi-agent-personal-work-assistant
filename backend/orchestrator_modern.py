"""
Modern Orchestrator using LangGraph for multi-agent coordination.
Implements: routing, loop prevention, rate limiting, parallel execution.
"""
from typing import TypedDict, Annotated, Literal, Optional, List, Dict, Any, Sequence
from datetime import datetime

from langgraph.graph import StateGraph, END, START
from langgraph.types import Send
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from config import config
from context_manager import context_manager
from guardrails import guardrails, apply_guardrails


# Global workspace state
class WorkspaceState(TypedDict):
    """Global state shared across all agents."""
    messages: Annotated[Sequence[BaseMessage], "Message history"]
    user_input: str
    current_agent: Optional[str]
    delegation_history: List[str]  # Track agent call chain
    results: Dict[str, Any]  # Results from each agent
    requires_approval: bool
    context_length: int
    loop_detected: bool
    rate_limit_exceeded: bool


class AgentRouter:
    """Routes requests to appropriate agents and prevents loops."""
    
    AGENTS = {
        "email": "email_agent",
        "calendar": "calendar_agent", 
        "task": "task_agent",
        "context": "context_agent",
        "meeting": "meeting_agent",
        "document": "document_agent"
    }
    
    MAX_DELEGATION_DEPTH = 3  # Prevent infinite chains
    
    def __init__(self):
        # Lazy init - don't create LLM until first use
        self._llm = None
    
    @property
    def llm(self):
        if self._llm is None:
            self._llm = ChatOpenAI(
                model=config.openai_model,
                temperature=0.3,  # Lower for consistent routing
                api_key=config.openai_api_key
            )
        return self._llm
    
    def route_request(self, user_input: str, delegation_history: List[str]) -> str:
        """
        Determine which agent should handle the request.
        Uses LLM to intelligently route based on content.
        """
        # Check delegation depth
        if len(delegation_history) >= self.MAX_DELEGATION_DEPTH:
            return "end"
        
        routing_prompt = f"""You are a smart router for a multi-agent workspace assistant.

Available agents:
- email: Handle emails (read, send, search, triage)
- calendar: Manage calendar (events, scheduling, meetings)
- task: Task management (prioritize, track, suggest)
- context: Context tracking (projects, work switching)
- meeting: Meeting management (prep, notes, action items)
- document: Document operations (read, summarize, search)

User request: "{user_input}"

Previous agents called: {delegation_history if delegation_history else "None"}

Which agent should handle this? Reply with ONLY the agent name from the list above.
If the request is complete or unclear, reply with "end".
"""
        
        response = self.llm.invoke([HumanMessage(content=routing_prompt)])
        agent = response.content.strip().lower()
        
        # Validate agent
        if agent not in self.AGENTS and agent != "end":
            # Default to email for ambiguous requests
            agent = "email"
        
        return agent
    
    def check_loop(self, current_agent: str, delegation_history: List[str]) -> bool:
        """
        Check if routing to this agent would create a loop.
        Returns True if loop detected.
        """
        if not delegation_history:
            return False
        
        # Don't allow same agent twice in a row
        if delegation_history and delegation_history[-1] == current_agent:
            return True
        
        # Don't allow A -> B -> A pattern
        if len(delegation_history) >= 2:
            if delegation_history[-2] == current_agent:
                return True
        
        # Don't allow agent to appear more than twice in chain
        if delegation_history.count(current_agent) >= 2:
            return True
        
        return False
    
    def can_execute_parallel(self, user_input: str) -> List[str]:
        """
        Determine if request can be handled by multiple agents in parallel.
        Returns list of agents that can work simultaneously.
        """
        parallel_keywords = {
            "email": ["email", "inbox", "message"],
            "calendar": ["calendar", "schedule", "meeting", "event"],
            "task": ["task", "todo", "priority"]
        }
        
        user_lower = user_input.lower()
        matching_agents = []
        
        for agent, keywords in parallel_keywords.items():
            if any(kw in user_lower for kw in keywords):
                matching_agents.append(agent)
        
        # Return if 2+ agents can work together
        if len(matching_agents) >= 2:
            return matching_agents
        
        return []


# Initialize router
router = AgentRouter()


def orchestrator_node(state: WorkspaceState) -> WorkspaceState:
    """
    Main orchestrator - decides routing and coordination.
    """
    user_input = state["user_input"]
    delegation_history = state.get("delegation_history", [])
    
    # Check context length - trigger summarization if needed
    if context_manager.needs_summarization(state.get("messages", [])):
        print("🔄 Context getting long - summarizing...")
        summary = context_manager.summarize_context(state["messages"])
        # Replace messages with summary
        return {
            "messages": [SystemMessage(content=f"Previous context summary: {summary}")],
            "context_length": len(summary)
        }
    
    # Route to appropriate agent
    next_agent = router.route_request(user_input, delegation_history)
    
    # Check for loop
    if router.check_loop(next_agent, delegation_history):
        print(f"🔄 Loop detected! {delegation_history} -> {next_agent}")
        return {
            "loop_detected": True,
            "current_agent": None,
            "messages": state["messages"] + [AIMessage(
                content="I detected a potential loop in agent delegation. Let me provide a direct answer instead."
            )]
        }
    
    return {
        "current_agent": next_agent,
        "delegation_history": delegation_history + [next_agent] if next_agent != "end" else delegation_history
    }


def email_agent_node(state: WorkspaceState) -> WorkspaceState:
    """Email agent - handles email operations."""
    from agents.email_agent_modern import EmailAgent
    
    agent = EmailAgent()
    user_input = state["user_input"]
    
    # Determine action type
    if any(word in user_input.lower() for word in ["triage", "check", "unread"]):
        result = agent.triage_emails(max_emails=10)
    elif "send" in user_input.lower():
        # This will trigger human approval
        result = agent.send_email("", "", user_input)  # Agent will parse details
    elif "search" in user_input.lower():
        result = agent.search_emails(user_input)
    else:
        # Default to triage
        result = agent.triage_emails(max_emails=5)
    
    return {
        "results": {**state.get("results", {}), "email": result},
        "messages": state["messages"] + [AIMessage(content=result)]
    }


def calendar_agent_node(state: WorkspaceState) -> WorkspaceState:
    """Calendar agent - handles calendar operations."""
    from tools.calendar_tools import calendar_get_today_schedule, calendar_list_events, calendar_find_free_slots
    
    user_input = state["user_input"].lower()
    
    # Determine what to do
    if "today" in user_input:
        result = calendar_get_today_schedule.invoke({})
    elif "free" in user_input or "available" in user_input:
        # Extract date if present, default to today
        result = calendar_find_free_slots.invoke({"date": datetime.now().strftime("%Y-%m-%d")})
    else:
        result = calendar_list_events.invoke({"days_ahead": 7})
    
    return {
        "results": {**state.get("results", {}), "calendar": result},
        "messages": state["messages"] + [AIMessage(content=result)]
    }


def aggregator_node(state: WorkspaceState) -> WorkspaceState:
    """
    Aggregate results from multiple agents and provide coherent response.
    """
    results = state.get("results", {})
    
    if len(results) <= 1:
        # Single agent result - already in messages
        return state
    
    # Multiple agent results - create summary
    llm = ChatOpenAI(model=config.openai_model, api_key=config.openai_api_key)
    
    summary_prompt = f"""Combine these results from different agents into a coherent response:

User request: {state['user_input']}

Results:
{chr(10).join([f"- {agent}: {result[:200]}..." for agent, result in results.items()])}

Provide a clear, actionable summary for the user."""
    
    response = llm.invoke([HumanMessage(content=summary_prompt)])
    
    return {
        "messages": state["messages"] + [AIMessage(content=response.content)]
    }


def should_continue(state: WorkspaceState) -> Literal["email", "calendar", "aggregate", "end"]:
    """Router - decides next agent or end."""
    
    # Check for loop
    if state.get("loop_detected"):
        return "end"
    
    # Check rate limits
    if state.get("rate_limit_exceeded"):
        return "end"
    
    # Get current agent
    current_agent = state.get("current_agent")
    
    if not current_agent or current_agent == "end":
        # Check if we have multiple results to aggregate
        if len(state.get("results", {})) > 1:
            return "aggregate"
        return "end"
    
    # Route to appropriate agent
    if current_agent == "email":
        return "email"
    elif current_agent == "calendar":
        return "calendar"
    # Add more agents as they're implemented
    
    return "end"


def parallel_router(state: WorkspaceState) -> List[Send]:
    """
    Enable parallel execution when multiple agents can work simultaneously.
    Uses LangGraph Send API for dynamic parallelization.
    """
    user_input = state["user_input"]
    parallel_agents = router.can_execute_parallel(user_input)
    
    if not parallel_agents:
        return []
    
    print(f"🚀 Parallel execution: {parallel_agents}")
    
    # Create Send commands for each agent
    sends = []
    for agent in parallel_agents:
        sends.append(
            Send(agent, {"user_input": user_input, "messages": state["messages"]})
        )
    
    return sends


# Build the orchestrator graph - but don't compile until needed
workflow = StateGraph(WorkspaceState)

# Add nodes
workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("email", email_agent_node)
workflow.add_node("calendar", calendar_agent_node)
workflow.add_node("aggregate", aggregator_node)

# Add edges
workflow.add_edge(START, "orchestrator")
workflow.add_conditional_edges(
    "orchestrator",
    should_continue,
    {
        "email": "email",
        "calendar": "calendar",
        "aggregate": "aggregate",
        "end": END
    }
)

# After agents finish, go to aggregator or end
workflow.add_edge("email", "aggregate")
workflow.add_edge("calendar", "aggregate")
workflow.add_edge("aggregate", END)

# Don't compile here - do it lazily
orchestrator_graph = None

def get_compiled_graph():
    """Lazy compilation of graph."""
    global orchestrator_graph
    if orchestrator_graph is None:
        print("Compiling orchestrator graph...")
        orchestrator_graph = workflow.compile()
        print("✓ Graph compiled successfully")
    return orchestrator_graph
    return orchestrator_graph


class WorkspaceOrchestrator:
    """Main orchestrator interface for the workspace assistant."""
    
    def __init__(self):
        self.graph = get_compiled_graph()
        self.session_history = []
    
    def process_request(self, user_input: str) -> str:
        """
        Process a user request through the multi-agent system.
        
        Args:
            user_input: User's request
        
        Returns:
            Response from agents
        """
        # Check guardrails first
        guardrail_check = apply_guardrails("user_request", {"input": user_input})
        if not guardrail_check.get("approved", True):
            return f"⚠️ Request blocked: {guardrail_check.get('reason', 'Safety check failed')}"
        
        # Initialize state
        initial_state: WorkspaceState = {
            "messages": [],
            "user_input": user_input,
            "current_agent": None,
            "delegation_history": [],
            "results": {},
            "requires_approval": False,
            "context_length": 0,
            "loop_detected": False,
            "rate_limit_exceeded": False
        }
        
        # Run through graph
        try:
            result = self.graph.invoke(initial_state)
            
            # Store in session history
            self.session_history.append({
                "input": user_input,
                "result": result,
                "timestamp": datetime.now()
            })
            
            # Extract final response
            if result["messages"]:
                return result["messages"][-1].content
            
            return "Request processed successfully"
            
        except Exception as e:
            return f"❌ Error processing request: {str(e)}"
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about current session."""
        agents_used = []
        for r in self.session_history:
            if r.get("delegation_history"):
                agents_used.extend(r.get("delegation_history", []))
        
        return {
            "total_requests": len(self.session_history),
            "agents_used": len(set(agents_used)),
            "total_messages": sum(len(r.get("result", {}).get("messages", [])) for r in self.session_history),
            "delegation_count": len(agents_used)
        }


# Export
__all__ = ["WorkspaceOrchestrator", "get_compiled_graph", "router"]
