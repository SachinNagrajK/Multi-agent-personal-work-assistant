from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any, List
from datetime import datetime
from models import Priority, EmailStatus
from guardrails import guardrails
from memory import memory_manager
from config import settings
from tools.web_tools import TavilySearchTool, URLExtractorTool
from tools.email_tools import EmailSenderTool, EmailSearchTool
from tools.analysis_tools import SentimentAnalysisTool, KeywordExtractionTool
from schemas import EmailTriageResult, EmailSuggestion
import json


class EmailAgent:
    """Handles email triage, drafting, and action item extraction"""
    
    def __init__(self):
        # Use structured output with modern LangChain
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.3,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Create structured output LLM
        self.structured_llm = self.llm.with_structured_output(EmailTriageResult)
        self.suggestion_llm = self.llm.with_structured_output(EmailSuggestion)
        
        # Initialize tools
        self.search_tool = TavilySearchTool()
        self.url_extractor = URLExtractorTool()
        self.email_sender = EmailSenderTool()
        self.email_search = EmailSearchTool()
        self.sentiment_analyzer = SentimentAnalysisTool()
        self.keyword_extractor = KeywordExtractionTool()
    
    async def triage_emails(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Triage incoming emails by priority and category"""
        triaged = []
        
        for email in emails:
            triage_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert email triage assistant. Analyze the email and provide structured output."""),
                ("user", "Email from: {sender}\nSubject: {subject}\nBody: {body}")
            ])
            
            try:
                # Use structured output - no JSON parsing needed!
                result = await self.structured_llm.ainvoke(
                    triage_prompt.format_messages(
                        sender=email.get("sender", ""),
                        subject=email.get("subject", ""),
                        body=email.get("body", "")[:1000]  # Truncate long emails
                    )
                )
                
                # Convert Pydantic model to dict for storage
                result_dict = result.model_dump()
                
                # Store in memory
                await memory_manager.store_email_context(
                    email_id=email["id"],
                    email_data={
                        **email,
                        "priority": result_dict["priority"],
                        "category": result_dict["category"]
                    }
                )
                
                triaged.append({
                    "email_id": email["id"],
                    "original_email": email,
                    "triage_result": result_dict
                })
                
            except Exception as e:
                print(f"Error triaging email {email['id']}: {e}")
                # Default triage
                triaged.append({
                    "email_id": email["id"],
                    "original_email": email,
                    "triage_result": {
                        "priority": "medium",
                        "category": "uncategorized",
                        "requires_response": False,
                        "action_items": [],
                        "summary": "Unable to analyze",
                        "reasoning": "Error during analysis"
                    }
                })
        
        return triaged
    
    async def draft_response(self, email_data: Dict[str, Any], context: str = "") -> Dict[str, Any]:
        """Draft a response to an email"""
        draft_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an email writing assistant. Draft a professional response to the email.
Consider the context provided and maintain appropriate tone.

Return JSON format:
{
    "draft": "email body text",
    "tone": "professional|friendly|formal|casual",
    "key_points": ["point1", "point2"],
    "suggestions": "any suggestions for the user"
}"""),
            ("user", """Original Email:
From: {sender}
Subject: {subject}
Body: {body}

Context: {context}

Draft a response that addresses the key points.""")
        ])
        
        try:
            response = await self.llm.ainvoke(
                draft_prompt.format_messages(
                    sender=email_data.get("sender", ""),
                    subject=email_data.get("subject", ""),
                    body=email_data.get("body", ""),
                    context=context
                )
            )
            
            result = extract_json_from_response(response.content)
            
            # Validate with guardrails
            validation = guardrails.validate_email_send({
                "subject": f"Re: {email_data.get('subject', '')}",
                "body": result["draft"],
                "recipient": email_data.get("sender", "")
            })
            
            result["guardrail_check"] = validation
            result["requires_approval"] = validation["requires_approval"]
            
            return result
            
        except Exception as e:
            print(f"Error drafting response: {e}")
            return {
                "draft": "",
                "tone": "unknown",
                "key_points": [],
                "suggestions": f"Error: {str(e)}",
                "guardrail_check": {"valid": False},
                "requires_approval": True
            }
    
    async def extract_action_items(self, email_body: str) -> List[str]:
        """Extract action items from email"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Extract action items from this email. Return as JSON array.
Only include clear, actionable tasks.

Example: ["Schedule meeting with John", "Review Q1 report", "Send updated proposal"]"""),
            ("user", "{email_body}")
        ])
        
        try:
            response = await self.llm.ainvoke(
                prompt.format_messages(email_body=email_body)
            )
            
            action_items = extract_json_from_response(response.content)
            return action_items if isinstance(action_items, list) else []
            
        except Exception as e:
            print(f"Error extracting action items: {e}")
            return []
    
    async def suggest_email_actions(self, triaged_emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Suggest what to do with triaged emails"""
        urgent = [e for e in triaged_emails if e["triage_result"]["priority"] == "urgent"]
        needs_response = [e for e in triaged_emails if e["triage_result"]["requires_response"]]
        
        return {
            "urgent_count": len(urgent),
            "urgent_emails": urgent[:5],  # Top 5
            "needs_response_count": len(needs_response),
            "suggested_actions": [
                {
                    "email_id": e["email_id"],
                    "action": "respond",
                    "reason": "Requires urgent response"
                }
                for e in urgent if e["triage_result"]["requires_response"]
            ]
        }


# Singleton instance
email_agent = EmailAgent()
