from typing import TypedDict, List, Optional, Dict, Any, Annotated
import operator
from models import AgentAction, Priority, WorkContext


class GraphState(TypedDict):
    """State that flows through the LangGraph"""
    
    # Input
    workflow_type: str
    parameters: Dict[str, Any]
    user_id: str
    
    # Email state
    emails: List[Dict[str, Any]]
    triaged_emails: List[Dict[str, Any]]
    draft_emails: List[Dict[str, Any]]
    
    # Calendar state
    calendar_events: List[Dict[str, Any]]
    meeting_preps: List[Dict[str, Any]]
    
    # Document state
    documents: List[Dict[str, Any]]
    document_summaries: List[Dict[str, Any]]
    
    # Task state
    tasks: List[Dict[str, Any]]
    prioritized_tasks: List[Dict[str, Any]]
    
    # Context state
    current_context: Optional[Dict[str, Any]]
    context_summary: Optional[str]
    
    # Agent tracking
    agent_actions: Annotated[List[AgentAction], operator.add]
    current_agent: Optional[str]
    
    # Approval & guardrails
    requires_approval: bool
    approval_items: List[Dict[str, Any]]
    guardrail_violations: List[Dict[str, Any]]
    
    # Results
    results: Dict[str, Any]
    status: str
    error: Optional[str]
    
    # Memory
    memory_context: Dict[str, Any]
