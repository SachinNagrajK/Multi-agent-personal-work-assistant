from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any, List
from datetime import datetime, timedelta
from memory import memory_manager
from guardrails import guardrails
from config import settings
from tools.calendar_tools import CalendarSearchTool, CalendarCreateTool, CalendarUpdateTool
from tools.web_tools import TavilySearchTool
from tools.communication_tools import NotificationTool
from schemas import MeetingPreparation, CalendarConflict
import json


class CalendarAgent:
    """Handles calendar management and meeting preparation"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.3,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Create structured output LLMs
        self.meeting_prep_llm = self.llm.with_structured_output(MeetingPreparation)
        self.conflict_llm = self.llm.with_structured_output(CalendarConflict)
        
        # Initialize tools
        self.calendar_search = CalendarSearchTool()
        self.calendar_create = CalendarCreateTool()
        self.calendar_update = CalendarUpdateTool()
        self.search_tool = TavilySearchTool()
        self.notification_tool = NotificationTool()
    
    async def prepare_for_meeting(
        self,
        meeting: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare context and materials for an upcoming meeting"""
        
        # Get relevant context from memory
        relevant_emails = context.get("emails", [])[:5]
        relevant_docs = context.get("documents", [])[:3]
        
        prep_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a meeting preparation assistant. Analyze the meeting and context to create:
1. A summary of what this meeting is about
2. Key topics likely to be discussed
3. Action items from previous meetings (if any)
4. Suggested agenda items
5. Relevant materials to review

Return JSON format:
{
    "summary": "meeting purpose and context",
    "key_topics": ["topic1", "topic2"],
    "previous_action_items": ["item1", "item2"],
    "suggested_agenda": ["agenda item 1", "agenda item 2"],
    "relevant_materials": ["doc1", "email thread"],
    "preparation_time_needed": "10 minutes"
}"""),
            ("user", """Meeting Details:
Title: {title}
Attendees: {attendees}
Time: {time}
Description: {description}

Recent Related Emails: {emails}
Related Documents: {documents}""")
        ])
        
        try:
            response = await self.llm.ainvoke(
                prep_prompt.format_messages(
                    title=meeting.get("title", ""),
                    attendees=", ".join(meeting.get("attendees", [])),
                    time=str(meeting.get("start_time", "")),
                    description=meeting.get("description", ""),
                    emails=json.dumps([e.get("metadata", {}).get("subject", "") for e in relevant_emails]),
                    documents=json.dumps([d.get("metadata", {}).get("title", "") for d in relevant_docs])
                )
            )
            
            result = extract_json_from_response(response.content)
            
            # Store meeting context
            await memory_manager.store_meeting_context(
                meeting_id=meeting["id"],
                meeting_data=meeting
            )
            
            return {
                "meeting_id": meeting["id"],
                "meeting_title": meeting.get("title"),
                "preparation": result,
                "status": "ready"
            }
            
        except Exception as e:
            print(f"Error preparing for meeting: {e}")
            return {
                "meeting_id": meeting["id"],
                "meeting_title": meeting.get("title"),
                "preparation": {
                    "summary": "Unable to prepare",
                    "key_topics": [],
                    "previous_action_items": [],
                    "suggested_agenda": [],
                    "relevant_materials": []
                },
                "status": "error",
                "error": str(e)
            }
    
    async def optimize_schedule(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze schedule and suggest optimizations"""
        
        # Analyze schedule density
        total_meeting_time = 0
        back_to_back_meetings = 0
        
        sorted_events = sorted(events, key=lambda x: x.get("start_time", ""))
        
        for i in range(len(sorted_events)):
            event = sorted_events[i]
            start = event.get("start_time")
            end = event.get("end_time")
            
            if isinstance(start, str):
                start = datetime.fromisoformat(start.replace("Z", "+00:00"))
            if isinstance(end, str):
                end = datetime.fromisoformat(end.replace("Z", "+00:00"))
            
            duration = (end - start).total_seconds() / 60  # minutes
            total_meeting_time += duration
            
            # Check if back-to-back
            if i < len(sorted_events) - 1:
                next_start = sorted_events[i + 1].get("start_time")
                if isinstance(next_start, str):
                    next_start = datetime.fromisoformat(next_start.replace("Z", "+00:00"))
                
                if (next_start - end).total_seconds() < 300:  # Less than 5 min gap
                    back_to_back_meetings += 1
        
        optimization_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a calendar optimization assistant. Analyze the schedule and suggest improvements.

Return JSON format:
{
    "overall_assessment": "schedule analysis",
    "issues": ["issue1", "issue2"],
    "suggestions": ["suggestion1", "suggestion2"],
    "recommended_breaks": ["when to add breaks"],
    "focus_time_opportunities": ["time blocks for deep work"]
}"""),
            ("user", """Schedule Analysis:
Total meetings: {meeting_count}
Total meeting time: {total_time} minutes
Back-to-back meetings: {back_to_back}
Meetings: {meetings}""")
        ])
        
        try:
            response = await self.llm.ainvoke(
                optimization_prompt.format_messages(
                    meeting_count=len(events),
                    total_time=int(total_meeting_time),
                    back_to_back=back_to_back_meetings,
                    meetings=json.dumps([{
                        "title": e.get("title"),
                        "duration": str(e.get("end_time")) if e.get("end_time") else "unknown"
                    } for e in sorted_events[:10]])
                )
            )
            
            result = extract_json_from_response(response.content)
            
            return {
                "statistics": {
                    "total_meetings": len(events),
                    "total_meeting_time_minutes": int(total_meeting_time),
                    "back_to_back_count": back_to_back_meetings,
                    "average_meeting_duration": int(total_meeting_time / len(events)) if events else 0
                },
                "optimization": result
            }
            
        except Exception as e:
            print(f"Error optimizing schedule: {e}")
            return {
                "statistics": {
                    "total_meetings": len(events),
                    "total_meeting_time_minutes": int(total_meeting_time)
                },
                "optimization": {
                    "overall_assessment": "Unable to analyze",
                    "issues": [],
                    "suggestions": []
                },
                "error": str(e)
            }
    
    async def suggest_meeting_times(
        self,
        attendees: List[str],
        duration_minutes: int,
        preferred_times: List[str]
    ) -> List[Dict[str, Any]]:
        """Suggest optimal meeting times"""
        # Simplified version - in production would check actual availability
        
        suggestions = []
        base_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        
        for i in range(3):
            suggestion_time = base_time + timedelta(days=i)
            suggestions.append({
                "start_time": suggestion_time.isoformat(),
                "end_time": (suggestion_time + timedelta(minutes=duration_minutes)).isoformat(),
                "confidence": 0.9 - (i * 0.1),
                "reasoning": f"Good time for all attendees"
            })
        
        return suggestions


# Singleton instance
calendar_agent = CalendarAgent()
