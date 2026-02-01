"""
Modern Email Agent using LangGraph ReAct pattern with real Gmail tools.
Implements: structured outputs, bind_tools, human-in-loop, guardrails.
"""
from typing import TypedDict, Annotated, Literal, Optional
from datetime import datetime

from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langchain.tools import tool

from config import config
from schemas import EmailTriageResult
from tools.gmail_tools import (
    gmail_read_recent,
    gmail_send_email,
    gmail_search,
    gmail_get_unread_count,
    gmail_mark_as_read,
    gmail_add_label,
    gmail_get_email_body
)
from tools.web_tools import TavilySearchTool


# State definition
class EmailAgentState(TypedDict):
    """State for email agent with message history."""
    messages: Annotated[list[BaseMessage], "add_messages"]
    user_input: str
    action: str  # 'triage', 'send', 'search', 'read'
    result: Optional[str]
    requires_approval: bool
    context_length: int
    

# Initialize LLM and tools
llm = ChatOpenAI(
    model=config.openai_model,
    temperature=config.temperature,
    api_key=config.openai_api_key
)

# Real Gmail tools
gmail_tool_list = [
    gmail_read_recent,
    gmail_send_email,
    gmail_search,
    gmail_get_unread_count,
    gmail_mark_as_read,
    gmail_add_label,
    gmail_get_email_body
]

# Bind tools to LLM
llm_with_tools = llm.bind_tools(gmail_tool_list)


# Agent nodes
def email_agent_node(state: EmailAgentState) -> EmailAgentState:
    """Main email agent - decides what to do and calls appropriate tools."""
    messages = state["messages"]
    user_input = state.get("user_input", "")
    
    # Add user message if not already in messages
    if not messages or not isinstance(messages[-1], HumanMessage):
        messages.append(HumanMessage(content=user_input))
    
    # System prompt
    system_prompt = """You are an intelligent email assistant with access to Gmail.

Your capabilities:
- Read and search emails using gmail_read_recent, gmail_search, gmail_get_email_body
- Check unread count with gmail_get_unread_count
- Send emails using gmail_send_email (ALWAYS ask for approval before sending!)
- Organize emails with gmail_mark_as_read, gmail_add_label

Guidelines:
1. For email sending, ALWAYS set requires_approval=True in your response
2. Be concise and helpful
3. Use appropriate tools for the task
4. Provide context from emails when relevant

Current task: {user_input}
"""
    
    # Call LLM with tools
    response = llm_with_tools.invoke([
        {"role": "system", "content": system_prompt.format(user_input=user_input)},
        *messages
    ])
    
    # Update state
    new_state = {
        "messages": messages + [response],
        "context_length": sum(len(str(m.content)) for m in messages) + len(str(response.content))
    }
    
    # Check if sending email (needs approval)
    if response.tool_calls:
        for tool_call in response.tool_calls:
            if tool_call["name"] == "gmail_send_email":
                new_state["requires_approval"] = True
    
    return new_state


def tool_execution_node(state: EmailAgentState) -> EmailAgentState:
    """Execute tool calls from the agent."""
    messages = state["messages"]
    last_message = messages[-1]
    
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return state
    
    # Create tool node and execute
    tool_node = ToolNode(gmail_tool_list)
    tool_results = tool_node.invoke({"messages": messages})
    
    return {
        "messages": messages + tool_results["messages"],
        "context_length": state.get("context_length", 0) + len(str(tool_results))
    }


def human_approval_node(state: EmailAgentState) -> EmailAgentState:
    """Human-in-the-loop for sensitive actions like sending emails."""
    messages = state["messages"]
    
    # Find the pending email send
    for msg in reversed(messages):
        if hasattr(msg, "tool_calls"):
            for tool_call in msg.tool_calls:
                if tool_call["name"] == "gmail_send_email":
                    args = tool_call["args"]
                    print("\n" + "="*60)
                    print("⚠️  EMAIL SEND APPROVAL REQUIRED")
                    print("="*60)
                    print(f"To: {args.get('to')}")
                    print(f"Subject: {args.get('subject')}")
                    print(f"Body:\n{args.get('body')}")
                    print("="*60)
                    
                    approval = input("Approve sending? (yes/no): ").strip().lower()
                    
                    if approval != 'yes':
                        # Cancel and notify
                        messages.append(AIMessage(
                            content="❌ Email sending cancelled by user."
                        ))
                        return {
                            "messages": messages,
                            "requires_approval": False,
                            "result": "cancelled"
                        }
    
    return {
        "requires_approval": False,
        "result": "approved"
    }


def guardrails_node(state: EmailAgentState) -> EmailAgentState:
    """Apply guardrails - check for sensitive content, rate limits, etc."""
    messages = state["messages"]
    
    # Check context length - trigger summarization if too long
    if state.get("context_length", 0) > 10000:  # 10k characters
        print("⚠️  Context length exceeded. Summarization needed.")
        # TODO: Call summarization tool
        return {
            "result": "summarization_needed"
        }
    
    # Check for sensitive patterns in email sends
    for msg in reversed(messages):
        if hasattr(msg, "tool_calls"):
            for tool_call in msg.tool_calls:
                if tool_call["name"] == "gmail_send_email":
                    body = tool_call["args"].get("body", "").lower()
                    
                    # Check for sensitive keywords
                    sensitive_keywords = ["password", "credit card", "ssn", "social security"]
                    if any(keyword in body for keyword in sensitive_keywords):
                        print("🚨 GUARDRAIL TRIGGERED: Sensitive content detected!")
                        messages.append(AIMessage(
                            content="⚠️ Email contains potentially sensitive information. Please review carefully."
                        ))
    
    return state


def should_continue(state: EmailAgentState) -> Literal["tools", "approval", "guardrails", "end"]:
    """Router - decides next step based on agent's decision."""
    messages = state["messages"]
    
    if not messages:
        return "end"
    
    last_message = messages[-1]
    
    # If approval is required, go to approval
    if state.get("requires_approval"):
        return "approval"
    
    # If agent wants to use tools, execute them
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    
    # Apply guardrails before ending
    if state.get("result") != "guardrails_checked":
        return "guardrails"
    
    # Otherwise, we're done
    return "end"


# Build the graph
workflow = StateGraph(EmailAgentState)

# Add nodes
workflow.add_node("agent", email_agent_node)
workflow.add_node("tools", tool_execution_node)
workflow.add_node("approval", human_approval_node)
workflow.add_node("guardrails", guardrails_node)

# Add edges
workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "approval": "approval",
        "guardrails": "guardrails",
        "end": END
    }
)
workflow.add_edge("tools", "agent")  # After tools, go back to agent
workflow.add_edge("approval", "agent")  # After approval, continue
workflow.add_edge("guardrails", END)

# Compile
email_agent_graph = workflow.compile()


# Main interface
class EmailAgent:
    """Modern email agent with LangGraph."""
    
    def __init__(self):
        self.graph = email_agent_graph
    
    def triage_emails(self, max_emails: int = 10) -> str:
        """Triage recent emails and suggest actions."""
        initial_state = {
            "messages": [],
            "user_input": f"Please triage my last {max_emails} emails and suggest what needs immediate attention.",
            "action": "triage",
            "result": None,
            "requires_approval": False,
            "context_length": 0
        }
        
        result = self.graph.invoke(initial_state)
        
        # Get final response
        if result["messages"]:
            return result["messages"][-1].content
        return "No response from agent"
    
    def send_email(self, to: str, subject: str, body: str) -> str:
        """Send an email with human approval."""
        initial_state = {
            "messages": [],
            "user_input": f"Send an email to {to} with subject '{subject}' and body: {body}",
            "action": "send",
            "result": None,
            "requires_approval": False,
            "context_length": 0
        }
        
        result = self.graph.invoke(initial_state)
        
        if result["messages"]:
            return result["messages"][-1].content
        return "Email operation completed"
    
    def search_emails(self, query: str) -> str:
        """Search emails by query."""
        initial_state = {
            "messages": [],
            "user_input": f"Search my emails for: {query}",
            "action": "search",
            "result": None,
            "requires_approval": False,
            "context_length": 0
        }
        
        result = self.graph.invoke(initial_state)
        
        if result["messages"]:
            return result["messages"][-1].content
        return "Search completed"


# Export
__all__ = ["EmailAgent", "email_agent_graph"]
