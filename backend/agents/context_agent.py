from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any, List
from memory import memory_manager
from config import settings
from tools.web_tools import TavilySearchTool
from tools.file_tools import FileSearchTool
from tools.analysis_tools import DataAnalysisTool, KeywordExtractionTool
from schemas import DailyContext, ContextSwitch, ProjectSummary
import json


class ContextAgent:
    """Manages work context and provides context-aware assistance"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.3,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Create structured output LLMs
        self.daily_context_llm = self.llm.with_structured_output(DailyContext)
        self.switch_llm = self.llm.with_structured_output(ContextSwitch)
        self.project_llm = self.llm.with_structured_output(ProjectSummary)
        
        # Initialize tools
        self.search_tool = TavilySearchTool()
        self.file_search = FileSearchTool()
        self.data_analyzer = DataAnalysisTool()
        self.keyword_extractor = KeywordExtractionTool()
    
    async def switch_context(
        self,
        project_name: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Help user switch to a different project context"""
        
        # Get all related context from memory
        project_context = await memory_manager.get_project_context(project_name)
        
        # Generate context summary
        context_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a context switching assistant. Help the user quickly get up to speed on this project.
Provide:
1. A brief summary of what this project is about
2. Recent activity (what's been happening)
3. Pending items that need attention
4. Suggested next actions
5. Key people or resources involved

Return JSON format:
{
    "summary": "project overview",
    "recent_activity": ["activity1", "activity2"],
    "pending_items": ["pending1", "pending2"],
    "suggested_next_actions": ["action1", "action2"],
    "key_people": ["person1"],
    "last_worked_on": "what you were doing last"
}"""),
            ("user", """Project: {project_name}

Related Emails: {emails}
Related Meetings: {meetings}
Related Tasks: {tasks}
Related Documents: {documents}""")
        ])
        
        try:
            response = await self.llm.ainvoke(
                context_prompt.format_messages(
                    project_name=project_name,
                    emails=json.dumps([e.get("metadata", {}) for e in project_context.get("emails", [])[:5]]),
                    meetings=json.dumps([m.get("metadata", {}) for m in project_context.get("meetings", [])[:5]]),
                    tasks=json.dumps([t.get("metadata", {}) for t in project_context.get("tasks", [])[:5]]),
                    documents=json.dumps([d.get("metadata", {}) for d in project_context.get("documents", [])[:3]])
                )
            )
            
            result = extract_json_from_response(response.content)
            
            return {
                "project_name": project_name,
                "context_summary": result,
                "related_items": {
                    "emails": project_context.get("emails", [])[:5],
                    "meetings": project_context.get("meetings", [])[:5],
                    "tasks": project_context.get("tasks", [])[:5],
                    "documents": project_context.get("documents", [])[:3]
                },
                "status": "ready"
            }
            
        except Exception as e:
            print(f"Error switching context: {e}")
            return {
                "project_name": project_name,
                "context_summary": {
                    "summary": "Unable to load context",
                    "recent_activity": [],
                    "pending_items": [],
                    "suggested_next_actions": []
                },
                "related_items": project_context,
                "status": "error",
                "error": str(e)
            }
    
    async def identify_context_from_activity(
        self,
        recent_items: Dict[str, List[Dict[str, Any]]]
    ) -> List[str]:
        """Identify what projects/contexts the user is working on"""
        
        identify_prompt = ChatPromptTemplate.from_messages([
            ("system", """Analyze recent activity and identify distinct projects or contexts the user is working on.
Look for patterns in emails, meetings, tasks, and documents.

Return JSON array of project names: ["Project Alpha", "Q1 Planning", "Client X"]"""),
            ("user", """Recent Activity:
Emails: {emails}
Meetings: {meetings}
Tasks: {tasks}
Documents: {documents}""")
        ])
        
        try:
            response = await self.llm.ainvoke(
                identify_prompt.format_messages(
                    emails=json.dumps([e.get("subject", "") for e in recent_items.get("emails", [])[:10]]),
                    meetings=json.dumps([m.get("title", "") for m in recent_items.get("meetings", [])[:10]]),
                    tasks=json.dumps([t.get("title", "") for t in recent_items.get("tasks", [])[:10]]),
                    documents=json.dumps([d.get("title", "") for d in recent_items.get("documents", [])[:10]])
                )
            )
            
            projects = extract_json_from_response(response.content)
            return projects if isinstance(projects, list) else []
            
        except Exception as e:
            print(f"Error identifying contexts: {e}")
            return []
    
    async def suggest_context_organization(
        self,
        all_items: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Suggest how to organize work into contexts"""
        
        org_prompt = ChatPromptTemplate.from_messages([
            ("system", """Analyze all work items and suggest how to organize them into logical contexts/projects.

Return JSON format:
{
    "suggested_projects": [
        {
            "name": "Project Name",
            "description": "what it's about",
            "items": {
                "email_ids": ["id1"],
                "task_ids": ["id2"],
                "document_ids": ["id3"],
                "meeting_ids": ["id4"]
            }
        }
    ],
    "uncategorized": {
        "email_ids": [],
        "task_ids": []
    }
}"""),
            ("user", """All Items:
Emails: {emails}
Tasks: {tasks}
Meetings: {meetings}
Documents: {documents}""")
        ])
        
        try:
            response = await self.llm.ainvoke(
                org_prompt.format_messages(
                    emails=json.dumps([{"id": e.get("id"), "subject": e.get("subject")} 
                                      for e in all_items.get("emails", [])[:20]]),
                    tasks=json.dumps([{"id": t.get("id"), "title": t.get("title")} 
                                     for t in all_items.get("tasks", [])[:20]]),
                    meetings=json.dumps([{"id": m.get("id"), "title": m.get("title")} 
                                        for m in all_items.get("meetings", [])[:20]]),
                    documents=json.dumps([{"id": d.get("id"), "title": d.get("title")} 
                                         for d in all_items.get("documents", [])[:20]])
                )
            )
            
            result = extract_json_from_response(response.content)
            return result
            
        except Exception as e:
            print(f"Error suggesting organization: {e}")
            return {
                "suggested_projects": [],
                "uncategorized": {},
                "error": str(e)
            }
    
    async def get_daily_context(self, user_id: str) -> Dict[str, Any]:
        """Get context for starting the day"""
        
        # This would typically pull from actual data sources
        # For now, return structure
        
        daily_prompt = ChatPromptTemplate.from_messages([
            ("system", """Create a daily briefing for the user. Include:
1. What's on the schedule today
2. What needs immediate attention
3. What was left incomplete yesterday
4. Suggested priorities for today

Return JSON format:
{
    "greeting": "Good morning! Here's your day:",
    "todays_focus": ["focus1", "focus2"],
    "urgent_items": ["urgent1"],
    "meetings_today": 3,
    "recommended_schedule": "schedule suggestion"
}"""),
            ("user", "User ID: {user_id}\nCurrent Date: {date}")
        ])
        
        try:
            from datetime import datetime
            response = await self.llm.ainvoke(
                daily_prompt.format_messages(
                    user_id=user_id,
                    date=datetime.now().strftime("%Y-%m-%d %A")
                )
            )
            
            result = extract_json_from_response(response.content)
            return result
            
        except Exception as e:
            print(f"Error getting daily context: {e}")
            return {
                "greeting": "Good morning!",
                "todays_focus": [],
                "urgent_items": [],
                "error": str(e)
            }


# Singleton instance
context_agent = ContextAgent()
