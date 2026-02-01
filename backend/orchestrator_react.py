"""
Proper ReAct Agent using LangGraph - Clean Implementation
This is how a proper multi-agent system should work.
"""
from typing import TypedDict, Annotated, Literal
from datetime import datetime, timedelta

from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState

from config import config
from tools.gmail_tools import gmail_read_recent, gmail_send_email, gmail_search
from tools.calendar_tools import (
    calendar_get_today_schedule,
    calendar_list_events,
    calendar_create_event,
    calendar_find_free_slots
)


# Helper tool for getting current time
from langchain_core.tools import tool

@tool
def get_current_time() -> str:
    """Get the current date and time. Use this to calculate relative times like '1 hour from now' or 'tomorrow at 2pm'."""
    now = datetime.now()
    return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')} ({now.strftime('%A, %B %d, %Y at %I:%M %p')})"


# Define the agent state
class AgentState(MessagesState):
    """State for the ReAct agent."""
    pass


# Create the LLM with tools bound
def create_agent():
    """Create a ReAct agent with all tools available."""
    
    # All available tools
    tools = [
        get_current_time,
        gmail_read_recent,
        gmail_send_email,
        gmail_search,
        calendar_get_today_schedule,
        calendar_list_events,
        calendar_create_event,
        calendar_find_free_slots
    ]
    
    # Create LLM
    llm = ChatOpenAI(
        model=config.openai_model,
        temperature=0.7,
        api_key=config.openai_api_key
    )
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)
    
    # System prompt
    system_message = SystemMessage(content="""You are an intelligent workspace assistant with access to Gmail and Google Calendar.

IMPORTANT: You have full access to conversation history. You can see all previous messages in this conversation.

Your capabilities:
- Get current time using get_current_time (ALWAYS use this first when calculating relative times!)
- Search and read emails using gmail_read_recent or gmail_search
- Send emails using gmail_send_email
- View calendar using calendar_get_today_schedule or calendar_list_events
- Create calendar events using calendar_create_event
- Find free time slots using calendar_find_free_slots

CRITICAL INSTRUCTIONS FOR SCHEDULING MEETINGS:

When a user asks you to schedule a meeting, you MUST:
1. Review ALL previous messages in the conversation to gather details
2. FIRST call get_current_time to know what time it is now
3. Extract details from current AND previous messages: attendee email, subject/description, duration, timing
4. Calculate the EXACT start and end times in ISO format (YYYY-MM-DDTHH:MM:SS)
5. If they say "1 hour from now" or "after 30 minutes", add that to current time
6. Call calendar_create_event with these parameters:
   - summary: The meeting subject/title
   - start_time: ISO format like "2026-01-31T21:00:00"
   - end_time: ISO format like "2026-01-31T21:30:00"
   - attendees: Email addresses comma-separated
   - description: Any additional details

DO NOT ask for clarification if you have enough information to proceed.
DO NOT just list events when asked to create one.

Example: If user says "schedule a 30-minute meeting with john@example.com about project review in 1 hour":
1. Calculate current time + 1 hour for start_time
2. Add 30 minutes to get end_time
3. Immediately call calendar_create_event with:
   - summary="Project Review"
   - start_time="2026-01-31T21:00:00" (calculated)
   - end_time="2026-01-31T21:30:00" (calculated)
   - attendees="john@example.com"
   - description="Meeting about project review"

DO NOT ask the user for information they've already provided.
DO NOT say "I need more details" when you can infer from context.

The current date and time is: January 31, 2026, 8:00 PM (but ALWAYS call get_current_time for accurate time)

Be proactive and take action immediately when you have sufficient information.""")
    
    def call_model(state: AgentState):
        """Call the LLM with tools."""
        messages = [system_message] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    # Build the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools))
    
    # Add edges
    workflow.add_edge(START, "agent")
    
    # Conditional edge: if agent wants to use tools, go to tools node
    # Otherwise, end
    workflow.add_conditional_edges(
        "agent",
        tools_condition,
    )
    
    # After tools, go back to agent
    workflow.add_edge("tools", "agent")
    
    # Compile and return
    return workflow.compile()


# Singleton graph
_compiled_graph = None

def get_agent():
    """Get or create the compiled agent graph."""
    global _compiled_graph
    if _compiled_graph is None:
        print("🤖 Compiling ReAct agent with tools...")
        _compiled_graph = create_agent()
        print("✓ Agent ready!")
    return _compiled_graph


class WorkspaceAssistant:
    """Main interface for the workspace assistant."""
    
    def __init__(self):
        self.graph = get_agent()
        self.conversation_messages = []  # Store full conversation history
        self.session_history = []
    
    def process_request(self, user_input: str) -> str:
        """
        Process a user request through the ReAct agent.
        Maintains conversation history across multiple turns.
        
        Args:
            user_input: User's request
        
        Returns:
            Response from the agent
        """
        try:
            # Add user message to conversation history
            self.conversation_messages.append(("user", user_input))
            
            # Create state with FULL conversation history
            initial_state = {
                "messages": self.conversation_messages.copy()
            }
            
            # Run the graph
            result = self.graph.invoke(initial_state)
            
            # Extract final response from result
            messages = result.get("messages", [])
            assistant_response = ""
            
            if messages:
                # Get the last AI message
                for msg in reversed(messages):
                    if hasattr(msg, 'content') and msg.content and not msg.content.startswith('['):
                        assistant_response = msg.content
                        break
            
            if not assistant_response:
                assistant_response = "I processed your request, but couldn't generate a response."
            
            # Add assistant response to conversation history
            self.conversation_messages.append(("assistant", assistant_response))
            
            # Store in session history
            self.session_history.append({
                "input": user_input,
                "output": assistant_response,
                "timestamp": datetime.now()
            })
            
            return assistant_response
            
        except Exception as e:
            import traceback
            print(f"\n❌ ERROR in agent:")
            print(traceback.format_exc())
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            self.conversation_messages.append(("assistant", error_msg))
            return error_msg
    
    def get_session_stats(self):
        """Get session statistics."""
        return {
            "total_requests": len(self.session_history),
            "agents_used": 1,  # Single ReAct agent
            "total_messages": sum(len(r.get("result", {}).get("messages", [])) for r in self.session_history),
            "tool_calls": sum(
                len([m for m in r.get("result", {}).get("messages", []) if hasattr(m, 'tool_calls') and m.tool_calls])
                for r in self.session_history
            )
        }
    
    def clear_conversation(self):
        """Clear conversation history for a fresh start."""
        self.conversation_messages = []


__all__ = ["WorkspaceAssistant", "get_agent"]
