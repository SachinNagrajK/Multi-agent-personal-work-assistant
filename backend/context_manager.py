"""
Context management and summarization for long conversations.
Automatically summarizes context when it gets too long.
"""
from typing import List, Dict, Any
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain.tools import tool

from config import config


class ContextManager:
    """Manages conversation context and triggers summarization."""
    
    # Thresholds
    MAX_CONTEXT_LENGTH = 10000  # characters
    MAX_MESSAGES = 20
    SUMMARY_TARGET_LENGTH = 2000  # target length after summarization
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=config.openai_model,
            temperature=0.3,  # Lower temp for consistent summaries
            api_key=config.openai_api_key
        )
        self.full_history = []  # Store everything
        self.summarized_context = ""
    
    def calculate_context_length(self, messages: List[BaseMessage]) -> int:
        """Calculate total character count of messages."""
        return sum(len(str(m.content)) for m in messages)
    
    def needs_summarization(self, messages: List[BaseMessage]) -> bool:
        """Check if context needs summarization."""
        # Check message count
        if len(messages) > self.MAX_MESSAGES:
            return True
        
        # Check character length
        if self.calculate_context_length(messages) > self.MAX_CONTEXT_LENGTH:
            return True
        
        return False
    
    def summarize_context(self, messages: List[BaseMessage]) -> str:
        """
        Summarize conversation history to reduce context size.
        Preserves key information and decisions.
        """
        # Extract text from messages
        conversation_text = "\n\n".join([
            f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
            for m in messages
        ])
        
        prompt = f"""Summarize the following conversation, preserving:
1. Key decisions made
2. Important facts and context
3. Action items or pending tasks
4. User preferences mentioned

Be concise but comprehensive. Target length: ~500 words.

Conversation:
{conversation_text}

Summary:"""
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        summary = response.content
        
        # Store full history
        self.full_history.extend(messages)
        self.summarized_context = summary
        
        return summary
    
    def get_context_for_agent(self, recent_messages: List[BaseMessage]) -> List[BaseMessage]:
        """
        Get optimized context for agent.
        Returns: [summary as system message] + [recent messages]
        """
        if not self.summarized_context:
            return recent_messages
        
        # Create system message with summary
        summary_message = SystemMessage(
            content=f"Previous conversation summary:\n{self.summarized_context}\n\n"
                   f"Continue from here with recent context."
        )
        
        # Return summary + last few recent messages
        return [summary_message] + recent_messages[-5:]
    
    def track_tool_usage(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Track which tools are being used for analytics."""
        return {
            "tool": tool_name,
            "timestamp": str(config),
            "args": args
        }


# Singleton instance
context_manager = ContextManager()


@tool
def summarize_conversation(messages: List[str]) -> str:
    """
    Summarize a list of conversation messages.
    Useful when context is getting too long.
    
    Args:
        messages: List of message strings to summarize
    
    Returns:
        Concise summary preserving key information
    """
    # Convert strings to messages
    msg_objects = [HumanMessage(content=m) for m in messages]
    return context_manager.summarize_context(msg_objects)


@tool
def search_context_history(query: str) -> str:
    """
    Search through full conversation history for specific information.
    Useful when you need to recall earlier context.
    
    Args:
        query: What to search for in conversation history
    
    Returns:
        Relevant excerpts from history
    """
    if not context_manager.full_history:
        return "No conversation history available."
    
    # Simple keyword search (can be enhanced with embeddings)
    query_lower = query.lower()
    relevant_messages = []
    
    for msg in context_manager.full_history:
        if query_lower in str(msg.content).lower():
            relevant_messages.append(msg.content[:200])  # First 200 chars
    
    if not relevant_messages:
        return f"No matches found for '{query}' in conversation history."
    
    return f"Found {len(relevant_messages)} relevant messages:\n\n" + "\n---\n".join(relevant_messages[:5])


@tool
def get_context_stats() -> str:
    """
    Get statistics about current context usage.
    
    Returns:
        Context statistics (length, message count, etc.)
    """
    total_chars = sum(len(str(m.content)) for m in context_manager.full_history)
    
    return f"""Context Statistics:
- Total messages in history: {len(context_manager.full_history)}
- Total characters: {total_chars}
- Summarized: {'Yes' if context_manager.summarized_context else 'No'}
- Summary length: {len(context_manager.summarized_context)} chars
- Threshold: {ContextManager.MAX_CONTEXT_LENGTH} chars
- Status: {'⚠️ Near limit' if total_chars > ContextManager.MAX_CONTEXT_LENGTH * 0.8 else '✅ OK'}
"""


# Export
context_tools = [
    summarize_conversation,
    search_context_history,
    get_context_stats
]

__all__ = ["ContextManager", "context_manager", "context_tools"]
