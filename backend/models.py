from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum


class AgentType(str, Enum):
    EMAIL = "email"
    CALENDAR = "calendar"
    DOCUMENT = "document"
    TASK = "task"
    CONTEXT = "context"
    MEETING = "meeting"


class Priority(str, Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EmailStatus(str, Enum):
    UNREAD = "unread"
    TRIAGED = "triaged"
    DRAFT_READY = "draft_ready"
    APPROVED = "approved"
    SENT = "sent"


# Email Models
class Email(BaseModel):
    id: str
    subject: str
    sender: str
    recipient: str
    body: str
    timestamp: datetime
    priority: Priority
    status: EmailStatus = EmailStatus.UNREAD
    action_items: List[str] = []
    draft_response: Optional[str] = None
    metadata: Dict[str, Any] = {}


class EmailTriageResult(BaseModel):
    email_id: str
    priority: Priority
    category: str
    requires_response: bool
    action_items: List[str]
    summary: str
    reasoning: str


class EmailDraftRequest(BaseModel):
    email_id: str
    context: str = ""


class EmailDraftResult(BaseModel):
    email_id: str
    draft: str
    tone: str
    key_points: List[str]


# Calendar Models
class CalendarEvent(BaseModel):
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    attendees: List[str]
    description: str = ""
    location: str = ""
    metadata: Dict[str, Any] = {}


class MeetingPrep(BaseModel):
    event_id: str
    summary: str
    key_topics: List[str]
    action_items_from_last_meeting: List[str]
    suggested_agenda: List[str]
    relevant_documents: List[str]
    relevant_emails: List[str]


# Document Models
class Document(BaseModel):
    id: str
    title: str
    content: str
    file_type: str
    created_at: datetime
    updated_at: datetime
    tags: List[str] = []
    metadata: Dict[str, Any] = {}


class DocumentSummary(BaseModel):
    document_id: str
    summary: str
    key_points: List[str]
    topics: List[str]
    sentiment: str


class DocumentQuery(BaseModel):
    query: str
    document_ids: Optional[List[str]] = None


# Task Models
class Task(BaseModel):
    id: str
    title: str
    description: str
    priority: Priority
    status: Literal["todo", "in_progress", "blocked", "completed"]
    due_date: Optional[datetime] = None
    dependencies: List[str] = []
    created_at: datetime
    updated_at: datetime
    related_emails: List[str] = []
    related_documents: List[str] = []
    metadata: Dict[str, Any] = {}


class TaskPrioritization(BaseModel):
    task_id: str
    priority: Priority
    urgency_score: float
    importance_score: float
    reasoning: str
    suggested_next_action: str


# Context Models
class WorkContext(BaseModel):
    project_name: str
    description: str
    related_emails: List[str] = []
    related_documents: List[str] = []
    related_tasks: List[str] = []
    related_meetings: List[str] = []
    last_accessed: datetime
    key_information: str = ""


class ContextSwitchRequest(BaseModel):
    project_name: str


class ContextSwitchResult(BaseModel):
    project_name: str
    summary: str
    recent_activity: List[str]
    pending_items: List[str]
    suggested_next_actions: List[str]
    relevant_context: Dict[str, Any]


# Agent Activity Models
class AgentAction(BaseModel):
    agent_type: AgentType
    action: str
    status: Literal["started", "in_progress", "completed", "failed"]
    timestamp: datetime
    details: Dict[str, Any] = {}
    result: Optional[Any] = None
    error: Optional[str] = None


class AgentState(BaseModel):
    current_agent: Optional[AgentType] = None
    agent_actions: List[AgentAction] = []
    pending_approvals: List[Dict[str, Any]] = []
    context: Dict[str, Any] = {}


# API Request/Response Models
class WorkflowRequest(BaseModel):
    workflow_type: Literal["morning_startup", "context_switch", "email_triage", "meeting_prep"]
    parameters: Dict[str, Any] = {}


class WorkflowResponse(BaseModel):
    workflow_id: str
    status: str
    results: Dict[str, Any]
    agent_actions: List[AgentAction]
    requires_approval: bool = False
    approval_items: List[Dict[str, Any]] = []


class ApprovalRequest(BaseModel):
    workflow_id: str
    approval_id: str
    approved: bool
    modifications: Optional[Dict[str, Any]] = None


# Dashboard Models
class DashboardData(BaseModel):
    urgent_emails: List[Email]
    today_meetings: List[CalendarEvent]
    high_priority_tasks: List[Task]
    recent_activity: List[AgentAction]
    pending_approvals: List[Dict[str, Any]]
    current_context: Optional[WorkContext] = None
