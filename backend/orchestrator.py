from langgraph.graph import StateGraph, END
from graph_state import GraphState
from agents import (
    email_agent,
    calendar_agent,
    document_agent,
    task_agent,
    context_agent,
    meeting_agent
)
from models import AgentAction, AgentType
from typing import Dict, Any
from datetime import datetime


class WorkspaceOrchestrator:
    """Orchestrates multiple agents using LangGraph"""
    
    def __init__(self):
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create graph
        workflow = StateGraph(GraphState)
        
        # Add nodes for each workflow type
        workflow.add_node("route_workflow", self._route_workflow)
        workflow.add_node("morning_startup", self._morning_startup_workflow)
        workflow.add_node("email_triage", self._email_triage_workflow)
        workflow.add_node("context_switch", self._context_switch_workflow)
        workflow.add_node("meeting_prep", self._meeting_prep_workflow)
        workflow.add_node("finalize", self._finalize)
        
        # Define edges
        workflow.set_entry_point("route_workflow")
        
        workflow.add_conditional_edges(
            "route_workflow",
            self._route_decision,
            {
                "morning_startup": "morning_startup",
                "email_triage": "email_triage",
                "context_switch": "context_switch",
                "meeting_prep": "meeting_prep"
            }
        )
        
        workflow.add_edge("morning_startup", "finalize")
        workflow.add_edge("email_triage", "finalize")
        workflow.add_edge("context_switch", "finalize")
        workflow.add_edge("meeting_prep", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def _route_decision(self, state: GraphState) -> str:
        """Decide which workflow to execute"""
        return state["workflow_type"]
    
    async def _route_workflow(self, state: GraphState) -> GraphState:
        """Initial routing node"""
        state["status"] = "routing"
        state["agent_actions"] = []
        return state
    
    async def _morning_startup_workflow(self, state: GraphState) -> GraphState:
        """Morning startup workflow: triage emails, check calendar, suggest priorities"""
        
        results = {}
        
        try:
            # Log agent action
            state["agent_actions"].append(AgentAction(
                agent_type=AgentType.EMAIL,
                action="triage_emails",
                status="started",
                timestamp=datetime.now(),
                details={}
            ))
            
            # 1. Triage emails
            if state.get("emails"):
                triaged = await email_agent.triage_emails(state["emails"])
                state["triaged_emails"] = triaged
                results["email_triage"] = await email_agent.suggest_email_actions(triaged)
                
                state["agent_actions"][-1].status = "completed"
                state["agent_actions"][-1].result = f"Triaged {len(triaged)} emails"
            
            # 2. Check today's calendar
            state["agent_actions"].append(AgentAction(
                agent_type=AgentType.CALENDAR,
                action="check_todays_meetings",
                status="started",
                timestamp=datetime.now(),
                details={}
            ))
            
            if state.get("calendar_events"):
                # Prepare for upcoming meetings
                meeting_preps = []
                for event in state["calendar_events"][:3]:  # Top 3 meetings
                    prep = await calendar_agent.prepare_for_meeting(
                        event,
                        {"emails": results.get("email_triage", {}).get("urgent_emails", [])}
                    )
                    meeting_preps.append(prep)
                
                state["meeting_preps"] = meeting_preps
                results["meeting_prep"] = meeting_preps
                
                state["agent_actions"][-1].status = "completed"
                state["agent_actions"][-1].result = f"Prepared {len(meeting_preps)} meetings"
            
            # 3. Prioritize tasks
            state["agent_actions"].append(AgentAction(
                agent_type=AgentType.TASK,
                action="prioritize_tasks",
                status="started",
                timestamp=datetime.now(),
                details={}
            ))
            
            if state.get("tasks"):
                prioritized = await task_agent.prioritize_tasks(state["tasks"])
                state["prioritized_tasks"] = prioritized
                
                # Suggest next task
                next_task = await task_agent.suggest_next_task(
                    state["tasks"],
                    {"time": "morning", "context": "startup"}
                )
                results["task_suggestion"] = next_task
                
                state["agent_actions"][-1].status = "completed"
                state["agent_actions"][-1].result = f"Prioritized {len(prioritized)} tasks"
            
            # 4. Get daily context
            state["agent_actions"].append(AgentAction(
                agent_type=AgentType.CONTEXT,
                action="daily_briefing",
                status="started",
                timestamp=datetime.now(),
                details={}
            ))
            
            daily_context = await context_agent.get_daily_context(state.get("user_id", "user"))
            results["daily_context"] = daily_context
            
            state["agent_actions"][-1].status = "completed"
            state["agent_actions"][-1].result = "Daily briefing ready"
            
            state["results"] = results
            state["status"] = "completed"
            
        except Exception as e:
            state["status"] = "error"
            state["error"] = str(e)
            if state["agent_actions"]:
                state["agent_actions"][-1].status = "failed"
                state["agent_actions"][-1].error = str(e)
        
        return state
    
    async def _email_triage_workflow(self, state: GraphState) -> GraphState:
        """Email triage workflow"""
        
        results = {}
        
        try:
            state["agent_actions"].append(AgentAction(
                agent_type=AgentType.EMAIL,
                action="triage_and_draft",
                status="started",
                timestamp=datetime.now(),
                details={}
            ))
            
            # Triage emails
            if state.get("emails"):
                triaged = await email_agent.triage_emails(state["emails"])
                state["triaged_emails"] = triaged
                
                # Draft responses for urgent emails that need replies
                drafts = []
                for email in triaged:
                    triage = email["triage_result"]
                    if triage["priority"] == "urgent" and triage["requires_response"]:
                        draft = await email_agent.draft_response(
                            email["original_email"],
                            context=triage["summary"]
                        )
                        drafts.append({
                            "email_id": email["email_id"],
                            "draft": draft
                        })
                
                state["draft_emails"] = drafts
                results["triaged_count"] = len(triaged)
                results["drafts_created"] = len(drafts)
                results["drafts"] = drafts
                
                # Check if any drafts need approval
                needs_approval = any(d["draft"].get("requires_approval") for d in drafts)
                if needs_approval:
                    state["requires_approval"] = True
                    state["approval_items"] = [
                        {
                            "type": "email_draft",
                            "email_id": d["email_id"],
                            "draft": d["draft"]["draft"]
                        }
                        for d in drafts if d["draft"].get("requires_approval")
                    ]
                
                state["agent_actions"][-1].status = "completed"
                state["agent_actions"][-1].result = f"Triaged {len(triaged)} emails, created {len(drafts)} drafts"
            
            state["results"] = results
            state["status"] = "completed"
            
        except Exception as e:
            state["status"] = "error"
            state["error"] = str(e)
            if state["agent_actions"]:
                state["agent_actions"][-1].status = "failed"
                state["agent_actions"][-1].error = str(e)
        
        return state
    
    async def _context_switch_workflow(self, state: GraphState) -> GraphState:
        """Context switching workflow"""
        
        results = {}
        
        try:
            state["agent_actions"].append(AgentAction(
                agent_type=AgentType.CONTEXT,
                action="switch_context",
                status="started",
                timestamp=datetime.now(),
                details={}
            ))
            
            project_name = state.get("parameters", {}).get("project_name", "")
            
            if project_name:
                # Switch context
                context = await context_agent.switch_context(
                    project_name,
                    state.get("user_id", "user")
                )
                
                state["current_context"] = context
                results["context"] = context
                
                state["agent_actions"][-1].status = "completed"
                state["agent_actions"][-1].result = f"Switched to {project_name}"
            
            state["results"] = results
            state["status"] = "completed"
            
        except Exception as e:
            state["status"] = "error"
            state["error"] = str(e)
            if state["agent_actions"]:
                state["agent_actions"][-1].status = "failed"
                state["agent_actions"][-1].error = str(e)
        
        return state
    
    async def _meeting_prep_workflow(self, state: GraphState) -> GraphState:
        """Meeting preparation workflow"""
        
        results = {}
        
        try:
            state["agent_actions"].append(AgentAction(
                agent_type=AgentType.MEETING,
                action="prepare_meeting",
                status="started",
                timestamp=datetime.now(),
                details={}
            ))
            
            meeting_id = state.get("parameters", {}).get("meeting_id")
            meeting = next(
                (m for m in state.get("calendar_events", []) if m.get("id") == meeting_id),
                None
            )
            
            if meeting:
                # Get context
                from memory import memory_manager
                context = await memory_manager.get_project_context(meeting.get("title", ""))
                
                # Prepare meeting
                prep = await calendar_agent.prepare_for_meeting(meeting, context)
                results["preparation"] = prep
                
                state["agent_actions"][-1].status = "completed"
                state["agent_actions"][-1].result = f"Prepared meeting: {meeting.get('title')}"
            
            state["results"] = results
            state["status"] = "completed"
            
        except Exception as e:
            state["status"] = "error"
            state["error"] = str(e)
            if state["agent_actions"]:
                state["agent_actions"][-1].status = "failed"
                state["agent_actions"][-1].error = str(e)
        
        return state
    
    async def _finalize(self, state: GraphState) -> GraphState:
        """Finalize the workflow"""
        if state["status"] != "error":
            state["status"] = "completed"
        return state
    
    async def execute_workflow(self, workflow_request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow"""
        
        # Initialize state
        initial_state = {
            "workflow_type": workflow_request.get("workflow_type"),
            "parameters": workflow_request.get("parameters", {}),
            "user_id": workflow_request.get("user_id", "user"),
            "emails": workflow_request.get("emails", []),
            "calendar_events": workflow_request.get("calendar_events", []),
            "tasks": workflow_request.get("tasks", []),
            "documents": workflow_request.get("documents", []),
            "triaged_emails": [],
            "draft_emails": [],
            "meeting_preps": [],
            "prioritized_tasks": [],
            "current_context": None,
            "context_summary": None,
            "agent_actions": [],
            "current_agent": None,
            "requires_approval": False,
            "approval_items": [],
            "guardrail_violations": [],
            "results": {},
            "status": "pending",
            "error": None,
            "memory_context": {}
        }
        
        # Execute graph
        final_state = await self.graph.ainvoke(initial_state)
        
        return final_state


# Singleton instance
orchestrator = WorkspaceOrchestrator()
