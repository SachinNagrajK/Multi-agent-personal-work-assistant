from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any, List
from datetime import datetime
from memory import memory_manager
from guardrails import guardrails
from config import settings
from tools.web_tools import TavilySearchTool
from tools.analysis_tools import DataAnalysisTool
from tools.communication_tools import NotificationTool
from schemas import TaskPrioritization, TaskSuggestion, SubtaskBreakdown
import json


class TaskAgent:
    """Handles task management, prioritization, and suggestions"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.3,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Create structured output LLMs
        self.prioritization_llm = self.llm.with_structured_output(TaskPrioritization)
        self.suggestion_llm = self.llm.with_structured_output(TaskSuggestion)
        self.breakdown_llm = self.llm.with_structured_output(SubtaskBreakdown)
        
        # Initialize tools
        self.search_tool = TavilySearchTool()
        self.data_analyzer = DataAnalysisTool()
        self.notification_tool = NotificationTool()
    
    async def prioritize_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze and prioritize tasks"""
        
        prioritized = []
        
        for task in tasks:
            priority_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a task prioritization assistant. Analyze the task and provide:
1. Urgency score (0-10): How time-sensitive is this?
2. Importance score (0-10): How critical is this to goals?
3. Recommended priority (urgent/high/medium/low)
4. Reasoning for the priority
5. Suggested next action
6. Estimated effort (low/medium/high)
7. Dependencies or blockers

Return JSON format:
{
    "urgency_score": 8,
    "importance_score": 9,
    "priority": "urgent",
    "reasoning": "explanation",
    "suggested_next_action": "specific action to take",
    "estimated_effort": "medium",
    "blockers": ["blocker1"],
    "should_do_today": true
}"""),
                ("user", """Task: {title}
Description: {description}
Current Status: {status}
Due Date: {due_date}
Dependencies: {dependencies}""")
            ])
            
            try:
                response = await self.llm.ainvoke(
                    priority_prompt.format_messages(
                        title=task.get("title", ""),
                        description=task.get("description", ""),
                        status=task.get("status", "todo"),
                        due_date=str(task.get("due_date", "No due date")),
                        dependencies=", ".join(task.get("dependencies", []))
                    )
                )
                
                result = extract_json_from_response(response.content)
                
                # Validate task creation
                validation = guardrails.validate_task_creation(task)
                
                # Store in memory
                await memory_manager.store_task_context(
                    task_id=task["id"],
                    task_data={
                        **task,
                        "priority": result["priority"],
                        "urgency_score": result["urgency_score"]
                    }
                )
                
                prioritized.append({
                    "task_id": task["id"],
                    "task": task,
                    "prioritization": result,
                    "validation": validation
                })
                
            except Exception as e:
                print(f"Error prioritizing task {task.get('id')}: {e}")
                prioritized.append({
                    "task_id": task.get("id"),
                    "task": task,
                    "prioritization": {
                        "urgency_score": 5,
                        "importance_score": 5,
                        "priority": "medium",
                        "reasoning": "Default prioritization due to error",
                        "suggested_next_action": "Review task details"
                    }
                })
        
        # Sort by priority
        priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
        prioritized.sort(
            key=lambda x: (
                priority_order.get(x["prioritization"].get("priority", "medium"), 2),
                -x["prioritization"].get("urgency_score", 5)
            )
        )
        
        return prioritized
    
    async def suggest_next_task(
        self,
        tasks: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Suggest the next best task to work on"""
        
        # Filter for incomplete tasks
        incomplete_tasks = [t for t in tasks if t.get("status") not in ["completed", "cancelled"]]
        
        if not incomplete_tasks:
            return {
                "suggestion": "No pending tasks",
                "reasoning": "All tasks are completed"
            }
        
        suggestion_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a productivity assistant. Based on the current context and available tasks, 
suggest the next best task to work on. Consider:
- Urgency and importance
- Current time of day
- User's energy level (if known)
- Dependencies
- Context switching cost

Return JSON format:
{
    "suggested_task_id": "task_id",
    "reasoning": "why this task now",
    "estimated_time": "30 minutes",
    "preparation_needed": ["prep1"],
    "alternative_tasks": ["task_id1", "task_id2"]
}"""),
            ("user", """Current Time: {current_time}
Current Context: {context}

Available Tasks:
{tasks}""")
        ])
        
        try:
            response = await self.llm.ainvoke(
                suggestion_prompt.format_messages(
                    current_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
                    context=json.dumps(context),
                    tasks=json.dumps([{
                        "id": t.get("id"),
                        "title": t.get("title"),
                        "priority": t.get("priority"),
                        "status": t.get("status"),
                        "due_date": str(t.get("due_date")) if t.get("due_date") else None
                    } for t in incomplete_tasks[:10]])
                )
            )
            
            result = extract_json_from_response(response.content)
            return result
            
        except Exception as e:
            print(f"Error suggesting next task: {e}")
            # Default to highest priority task
            if incomplete_tasks:
                return {
                    "suggested_task_id": incomplete_tasks[0].get("id"),
                    "reasoning": "Highest priority task",
                    "estimated_time": "unknown"
                }
            return {
                "suggestion": "Error suggesting task",
                "error": str(e)
            }
    
    async def break_down_task(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Break down a complex task into subtasks"""
        
        breakdown_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a task breakdown assistant. Break down this task into specific, actionable subtasks.
Each subtask should be:
- Concrete and specific
- Completable in 30-60 minutes
- Have a clear definition of done

Return JSON array:
[
    {
        "title": "subtask title",
        "description": "what to do",
        "estimated_time": "30 minutes",
        "dependencies": [],
        "order": 1
    }
]"""),
            ("user", "Task: {title}\n\nDescription: {description}")
        ])
        
        try:
            response = await self.llm.ainvoke(
                breakdown_prompt.format_messages(
                    title=task.get("title", ""),
                    description=task.get("description", "")
                )
            )
            
            subtasks = extract_json_from_response(response.content)
            return subtasks if isinstance(subtasks, list) else []
            
        except Exception as e:
            print(f"Error breaking down task: {e}")
            return []
    
    async def identify_blockers(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify tasks that are blocking other tasks"""
        
        blocker_analysis = {
            "blocking_tasks": [],
            "blocked_tasks": [],
            "critical_path": []
        }
        
        for task in tasks:
            if task.get("dependencies"):
                # Check if dependencies are completed
                incomplete_deps = [
                    dep for dep in task.get("dependencies", [])
                    if any(t.get("id") == dep and t.get("status") not in ["completed"] for t in tasks)
                ]
                
                if incomplete_deps:
                    blocker_analysis["blocked_tasks"].append({
                        "task_id": task.get("id"),
                        "task_title": task.get("title"),
                        "blocked_by": incomplete_deps
                    })
        
        # Find tasks that are dependencies for others
        all_deps = set()
        for task in tasks:
            all_deps.update(task.get("dependencies", []))
        
        for dep_id in all_deps:
            blocking_task = next((t for t in tasks if t.get("id") == dep_id), None)
            if blocking_task and blocking_task.get("status") not in ["completed"]:
                blocker_analysis["blocking_tasks"].append({
                    "task_id": blocking_task.get("id"),
                    "task_title": blocking_task.get("title"),
                    "blocking_count": sum(
                        1 for t in tasks if dep_id in t.get("dependencies", [])
                    )
                })
        
        return blocker_analysis


# Singleton instance
task_agent = TaskAgent()
