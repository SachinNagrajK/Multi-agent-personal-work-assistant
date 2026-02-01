"""
Pydantic schemas for structured LLM outputs - Modern LangChain approach
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class PriorityLevel(str, Enum):
    """Priority levels"""
    urgent = "urgent"
    high = "high"
    medium = "medium"
    low = "low"


class EmailTriageResult(BaseModel):
    """Structured output for email triage"""
    priority: PriorityLevel = Field(description="Priority level of the email")
    category: str = Field(description="Category of the email (e.g., 'work', 'personal', 'meeting')")
    requires_response: bool = Field(description="Whether the email requires a response")
    action_items: List[str] = Field(description="List of action items extracted from the email")
    summary: str = Field(description="Brief summary of the email content")
    reasoning: str = Field(description="Reasoning behind the priority assignment")


class TaskPrioritization(BaseModel):
    """Structured output for task prioritization"""
    priority: PriorityLevel = Field(description="Priority level of the task")
    urgency_score: int = Field(description="Urgency score from 1-10", ge=1, le=10)
    complexity: str = Field(description="Complexity assessment (simple/moderate/complex)")
    estimated_time: str = Field(description="Estimated time to complete")
    dependencies: List[str] = Field(description="List of dependencies or blockers")
    should_do_today: bool = Field(description="Whether this task should be done today")
    reasoning: str = Field(description="Reasoning behind the prioritization")


class MeetingPreparation(BaseModel):
    """Structured output for meeting preparation"""
    summary: str = Field(description="Summary of the meeting context")
    key_topics: List[str] = Field(description="Key topics to discuss")
    attendees: List[str] = Field(description="List of attendees")
    suggested_agenda: List[str] = Field(description="Suggested agenda items")
    materials_needed: List[str] = Field(description="Materials or documents needed")
    action_items: List[str] = Field(description="Pre-meeting action items")


class DailyContext(BaseModel):
    """Structured output for daily context"""
    greeting: str = Field(description="Personalized greeting")
    priority_focus: str = Field(description="Main priority focus for the day")
    upcoming_deadlines: List[str] = Field(description="Upcoming deadlines")
    context_summary: str = Field(description="Summary of current work context")
    recommended_actions: List[str] = Field(description="Recommended actions for the day")


class EmailSuggestion(BaseModel):
    """Structured output for email action suggestions"""
    action: str = Field(description="Suggested action (reply/forward/archive/flag)")
    reasoning: str = Field(description="Reasoning for the suggestion")
    priority: PriorityLevel = Field(description="Priority of this action")
    suggested_time: str = Field(description="Suggested time to handle this")


class TaskSuggestion(BaseModel):
    """Structured output for next task suggestion"""
    suggested_task_id: str = Field(description="ID of the suggested task")
    reasoning: str = Field(description="Reasoning for suggesting this task")
    context: str = Field(description="Context for why this task is important now")
    estimated_duration: str = Field(description="Estimated duration for the task")


class CalendarConflict(BaseModel):
    """Structured output for calendar conflict analysis"""
    has_conflicts: bool = Field(description="Whether there are scheduling conflicts")
    conflicts: List[str] = Field(description="List of identified conflicts")
    suggestions: List[str] = Field(description="Suggestions to resolve conflicts")
    priority_meetings: List[str] = Field(description="Meetings that should be prioritized")


class DocumentAnalysis(BaseModel):
    """Structured output for document analysis"""
    summary: str = Field(description="Summary of the document")
    key_points: List[str] = Field(description="Key points from the document")
    topics: List[str] = Field(description="Main topics covered")
    sentiment: str = Field(description="Overall sentiment (positive/neutral/negative)")
    action_items: List[str] = Field(description="Action items extracted from the document")
    relevance_score: int = Field(description="Relevance score from 1-10", ge=1, le=10)


class MeetingAgenda(BaseModel):
    """Structured output for meeting agenda"""
    title: str = Field(description="Meeting title")
    duration: str = Field(description="Expected duration")
    items: List[str] = Field(description="Agenda items")
    time_allocations: List[str] = Field(description="Time allocation for each item")
    objectives: List[str] = Field(description="Meeting objectives")


class MeetingDecisions(BaseModel):
    """Structured output for meeting decisions"""
    decisions: List[str] = Field(description="Decisions made in the meeting")
    action_items: List[str] = Field(description="Action items assigned")
    next_steps: List[str] = Field(description="Next steps to take")
    follow_up_needed: bool = Field(description="Whether follow-up is needed")


class ContextSwitch(BaseModel):
    """Structured output for context switching"""
    previous_context: str = Field(description="Summary of previous context")
    new_context: str = Field(description="Summary of new context")
    relevant_information: List[str] = Field(description="Relevant information for the switch")
    suggested_actions: List[str] = Field(description="Suggested actions in the new context")
    time_estimate: str = Field(description="Estimated time to switch contexts")


class ProjectSummary(BaseModel):
    """Structured output for project summary"""
    project_name: str = Field(description="Name of the project")
    status: str = Field(description="Current status of the project")
    recent_activities: List[str] = Field(description="Recent activities on the project")
    pending_tasks: List[str] = Field(description="Pending tasks for the project")
    blockers: List[str] = Field(description="Current blockers or issues")
    next_milestones: List[str] = Field(description="Upcoming milestones")


class SubtaskBreakdown(BaseModel):
    """Structured output for subtask breakdown"""
    subtasks: List[str] = Field(description="List of subtasks")
    estimated_times: List[str] = Field(description="Estimated time for each subtask")
    dependencies: List[str] = Field(description="Dependencies between subtasks")
    suggested_order: List[int] = Field(description="Suggested order to complete subtasks")
