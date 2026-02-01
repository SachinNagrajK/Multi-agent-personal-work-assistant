from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any, List
from datetime import datetime
from memory import memory_manager
from config import settings
from tools.web_tools import TavilySearchTool
from tools.analysis_tools import SentimentAnalysisTool, KeywordExtractionTool
from tools.communication_tools import SlackMessageTool, TeamsMessageTool, NotificationTool
from schemas import MeetingPreparation, MeetingAgenda, MeetingDecisions
import json


class MeetingAgent:
    """Handles meeting transcription, summarization, and action item extraction"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.3,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Create structured output LLMs
        self.prep_llm = self.llm.with_structured_output(MeetingPreparation)
        self.agenda_llm = self.llm.with_structured_output(MeetingAgenda)
        self.decisions_llm = self.llm.with_structured_output(MeetingDecisions)
        
        # Initialize tools
        self.search_tool = TavilySearchTool()
        self.sentiment_analyzer = SentimentAnalysisTool()
        self.keyword_extractor = KeywordExtractionTool()
        self.slack_tool = SlackMessageTool()
        self.teams_tool = TeamsMessageTool()
        self.notification_tool = NotificationTool()
    
    async def process_meeting_transcript(
        self,
        meeting_id: str,
        transcript: str,
        meeting_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process meeting transcript and extract insights"""
        
        process_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a meeting analysis assistant. Analyze this meeting transcript and provide:
1. A concise summary
2. Key decisions made
3. Action items (who, what, when)
4. Important topics discussed
5. Open questions or unresolved issues
6. Sentiment/tone of the meeting
7. Follow-up items needed

Return JSON format:
{
    "summary": "meeting summary",
    "key_decisions": ["decision1", "decision2"],
    "action_items": [
        {"owner": "person", "action": "what to do", "due_date": "when"}
    ],
    "topics_discussed": ["topic1", "topic2"],
    "open_questions": ["question1"],
    "sentiment": "positive|neutral|negative|mixed",
    "follow_ups": ["follow_up1"]
}"""),
            ("user", """Meeting: {title}
Attendees: {attendees}
Duration: {duration}

Transcript:
{transcript}""")
        ])
        
        try:
            response = await self.llm.ainvoke(
                process_prompt.format_messages(
                    title=meeting_metadata.get("title", ""),
                    attendees=", ".join(meeting_metadata.get("attendees", [])),
                    duration=meeting_metadata.get("duration", "unknown"),
                    transcript=transcript[:8000]  # Truncate very long transcripts
                )
            )
            
            result = extract_json_from_response(response.content)
            
            # Store meeting insights in memory
            await memory_manager.store_meeting_context(
                meeting_id=meeting_id,
                meeting_data={
                    **meeting_metadata,
                    "summary": result["summary"],
                    "key_decisions": result["key_decisions"],
                    "action_items": result["action_items"]
                }
            )
            
            return {
                "meeting_id": meeting_id,
                "meeting_title": meeting_metadata.get("title"),
                "analysis": result,
                "status": "processed"
            }
            
        except Exception as e:
            print(f"Error processing meeting transcript: {e}")
            return {
                "meeting_id": meeting_id,
                "meeting_title": meeting_metadata.get("title"),
                "analysis": {
                    "summary": "Unable to process transcript",
                    "key_decisions": [],
                    "action_items": [],
                    "topics_discussed": []
                },
                "status": "error",
                "error": str(e)
            }
    
    async def generate_meeting_summary(
        self,
        meeting_data: Dict[str, Any]
    ) -> str:
        """Generate a shareable meeting summary"""
        
        summary_prompt = ChatPromptTemplate.from_messages([
            ("system", """Create a professional meeting summary email that can be sent to attendees.
Include:
- Meeting overview
- Key points discussed
- Decisions made
- Action items with owners
- Next steps

Format it as a professional email."""),
            ("user", """Meeting Details:
{meeting_data}""")
        ])
        
        try:
            response = await self.llm.ainvoke(
                summary_prompt.format_messages(
                    meeting_data=json.dumps(meeting_data, indent=2)
                )
            )
            
            return response.content
            
        except Exception as e:
            print(f"Error generating meeting summary: {e}")
            return f"Error generating summary: {str(e)}"
    
    async def suggest_meeting_agenda(
        self,
        meeting_title: str,
        context: Dict[str, Any]
    ) -> List[str]:
        """Suggest agenda items for an upcoming meeting"""
        
        agenda_prompt = ChatPromptTemplate.from_messages([
            ("system", """Suggest agenda items for this meeting based on the context.
Return JSON array of agenda items: ["Agenda item 1", "Agenda item 2", ...]
Each item should be specific and actionable."""),
            ("user", """Meeting: {title}

Context:
{context}""")
        ])
        
        try:
            response = await self.llm.ainvoke(
                agenda_prompt.format_messages(
                    title=meeting_title,
                    context=json.dumps(context)
                )
            )
            
            agenda = extract_json_from_response(response.content)
            return agenda if isinstance(agenda, list) else []
            
        except Exception as e:
            print(f"Error suggesting agenda: {e}")
            return []
    
    async def extract_decisions(
        self,
        transcript: str
    ) -> List[Dict[str, Any]]:
        """Extract key decisions from meeting transcript"""
        
        decisions_prompt = ChatPromptTemplate.from_messages([
            ("system", """Extract all decisions made in this meeting.
Return JSON array:
[
    {
        "decision": "what was decided",
        "rationale": "why",
        "impact": "who/what is affected",
        "confidence": "high|medium|low"
    }
]"""),
            ("user", "Transcript:\n{transcript}")
        ])
        
        try:
            response = await self.llm.ainvoke(
                decisions_prompt.format_messages(transcript=transcript[:8000])
            )
            
            decisions = extract_json_from_response(response.content)
            return decisions if isinstance(decisions, list) else []
            
        except Exception as e:
            print(f"Error extracting decisions: {e}")
            return []
    
    async def track_meeting_action_items(
        self,
        action_items: List[Dict[str, Any]],
        meeting_id: str
    ) -> List[Dict[str, Any]]:
        """Convert meeting action items into trackable tasks"""
        
        tasks = []
        
        for item in action_items:
            task = {
                "id": f"task_{meeting_id}_{len(tasks)}",
                "title": item.get("action", ""),
                "description": f"From meeting: {meeting_id}",
                "owner": item.get("owner", "Unassigned"),
                "due_date": item.get("due_date"),
                "status": "todo",
                "source": "meeting",
                "source_id": meeting_id
            }
            tasks.append(task)
        
        return tasks
    
    async def compare_with_previous_meeting(
        self,
        current_meeting: Dict[str, Any],
        previous_meeting: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare current meeting with previous one to track progress"""
        
        compare_prompt = ChatPromptTemplate.from_messages([
            ("system", """Compare these two meetings and identify:
1. Progress made on previous action items
2. Recurring topics/issues
3. New developments
4. Items that weren't addressed

Return JSON format:
{
    "progress_made": ["progress1"],
    "recurring_issues": ["issue1"],
    "new_topics": ["topic1"],
    "unaddressed_items": ["item1"]
}"""),
            ("user", """Previous Meeting:
{previous}

Current Meeting:
{current}""")
        ])
        
        try:
            response = await self.llm.ainvoke(
                compare_prompt.format_messages(
                    previous=json.dumps(previous_meeting),
                    current=json.dumps(current_meeting)
                )
            )
            
            result = extract_json_from_response(response.content)
            return result
            
        except Exception as e:
            print(f"Error comparing meetings: {e}")
            return {
                "progress_made": [],
                "recurring_issues": [],
                "new_topics": [],
                "unaddressed_items": []
            }


# Singleton instance
meeting_agent = MeetingAgent()
