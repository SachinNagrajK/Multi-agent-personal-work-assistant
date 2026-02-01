"""
Simplified orchestrator with ReAct pattern - proper agent behavior.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from config import config


class SimpleOrchestrator:
    """ReAct agent orchestrator with tool calling."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=config.openai_model,
            temperature=0.7,
            api_key=config.openai_api_key
        )
        self.session_history = []
        
        # Import all tools
        from tools.gmail_tools import (
            gmail_read_recent, gmail_send_email, gmail_search, 
            gmail_get_unread_count, gmail_mark_as_read, gmail_get_email_body
        )
        from tools.calendar_tools import (
            calendar_list_events, calendar_create_event, 
            calendar_find_free_slots, calendar_get_today_schedule
        )
        
        # Combine all tools
        self.tools = [
            gmail_read_recent,
            gmail_send_email,
            gmail_search,
            gmail_get_unread_count,
            gmail_mark_as_read,
            gmail_get_email_body,
            calendar_list_events,
            calendar_create_event,
            calendar_find_free_slots,
            calendar_get_today_schedule
        ]
        
        # Create ReAct prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI workspace assistant with access to Gmail and Google Calendar.

Your capabilities:
- Read, search, and manage emails
- Create, update, and manage calendar events
- Find free time slots
- Send emails

When given a task:
1. Break it down into steps
2. Use the available tools to complete each step
3. Reason about the results
4. Continue until the task is fully complete
5. Provide a clear summary of what you did

Be proactive and complete the full task, not just part of it."""),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create agent
        self.agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=10,
            handle_parsing_errors=True
        )
        
        print("✓ ReAct agent orchestrator initialized")
    
    def process_request(self, user_input: str) -> str:
        """Process a user request using ReAct agent."""
        try:
            print(f"\n{'='*60}")
            print(f"Processing: {user_input}")
            print(f"{'='*60}\n")
            
            # Run agent
            result = self.agent_executor.invoke({
                "input": user_input,
                "chat_history": []
            })
            
            # Store in history
            self.session_history.append({
                "input": user_input,
                "output": result["output"],
                "timestamp": datetime.now()
            })
            
            return result["output"]
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return f"Error processing request: {str(e)}"
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        return {
            "total_requests": len(self.session_history),
            "agents_used": ["email", "calendar"],
            "total_messages": len(self.session_history) * 2,
            "delegation_count": 0
        }


# Export
__all__ = ["SimpleOrchestrator"]
