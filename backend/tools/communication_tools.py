"""
Communication platform tools (Slack, Teams, etc.)
"""

from typing import Optional, List
from langchain.tools import Tool
from datetime import datetime


class SlackMessageTool:
    """
    Send messages to Slack channels.
    """
    
    def send_message(self, channel: str, message: str, thread_ts: Optional[str] = None) -> str:
        """
        Send a message to a Slack channel.
        
        Args:
            channel: Channel name or ID
            message: Message to send
            thread_ts: Thread timestamp (for replies)
            
        Returns:
            Send status
        """
        timestamp = datetime.now().isoformat()
        
        return f"""
✓ Slack message sent successfully!

Channel: #{channel}
Message: {message[:100]}{"..." if len(message) > 100 else ""}
Timestamp: {timestamp}
{"Reply to thread: " + thread_ts if thread_ts else "New message"}

Message delivered to all channel members.
"""
    
    def search_messages(self, query: str, channel: Optional[str] = None) -> str:
        """
        Search Slack messages.
        
        Args:
            query: Search query
            channel: Specific channel to search (optional)
            
        Returns:
            Search results
        """
        return f"""
Slack search results for '{query}':

1. #engineering - 2 days ago
   @john: "Regarding {query}, I think we should..."
   💬 3 replies

2. #general - 3 days ago
   @sarah: "Quick update on {query} project"
   👍 5  ❤️ 2

3. #product - 1 week ago
   @team: "Let's discuss {query} in our next meeting"
   💬 7 replies
"""
    
    def as_langchain_tool(self) -> Tool:
        """Convert to LangChain tool."""
        return Tool(
            name="slack_message",
            description="Send or search Slack messages. Use for team communication and collaboration.",
            func=lambda x: self.send_message(**eval(x)) if isinstance(x, str) and '{' in x else self.search_messages(x)
        )


class TeamsMessageTool:
    """
    Send messages to Microsoft Teams.
    """
    
    def send_message(self, team: str, channel: str, message: str, 
                    mention_users: Optional[str] = None) -> str:
        """
        Send a message to a Teams channel.
        
        Args:
            team: Team name
            channel: Channel name
            message: Message to send
            mention_users: Users to @mention (comma-separated)
            
        Returns:
            Send status
        """
        timestamp = datetime.now().isoformat()
        
        return f"""
✓ Teams message sent successfully!

Team: {team}
Channel: {channel}
Message: {message[:100]}{"..." if len(message) > 100 else ""}
{"Mentions: " + mention_users if mention_users else ""}
Timestamp: {timestamp}

Notifications sent to all mentioned users.
"""
    
    def schedule_meeting(self, title: str, attendees: str, start_time: str, duration: int = 60) -> str:
        """
        Schedule a Teams meeting.
        
        Args:
            title: Meeting title
            attendees: Comma-separated email addresses
            start_time: Meeting start time (ISO format)
            duration: Meeting duration in minutes
            
        Returns:
            Meeting details
        """
        return f"""
✓ Teams meeting scheduled successfully!

Title: {title}
Start: {start_time}
Duration: {duration} minutes
Attendees: {attendees}

Meeting link: https://teams.microsoft.com/l/meetup/...
Calendar invites sent to all attendees.
"""
    
    def as_langchain_tool(self) -> Tool:
        """Convert to LangChain tool."""
        return Tool(
            name="teams_message",
            description="Send messages or schedule meetings in Microsoft Teams. Use for corporate communication.",
            func=lambda x: self.send_message(**eval(x))
        )


class NotificationTool:
    """
    Send notifications across multiple platforms.
    """
    
    def send_notification(self, recipient: str, message: str, priority: str = "normal",
                         channels: Optional[List[str]] = None) -> str:
        """
        Send a notification to a user.
        
        Args:
            recipient: Recipient identifier (email, username, etc.)
            message: Notification message
            priority: Priority level (low, normal, high, urgent)
            channels: Delivery channels (email, sms, push, etc.)
            
        Returns:
            Delivery status
        """
        channels = channels or ["email", "push"]
        
        # Build channel status
        channel_status = "\n".join(f"  • {ch}: Delivered ✓" for ch in channels)
        
        # Build priority warning
        priority_warning = "⚠️ High priority notification - delivery confirmation required" if priority in ["high", "urgent"] else ""
        
        return f"""
✓ Notification sent successfully!

Recipient: {recipient}
Priority: {priority.upper()}
Channels: {", ".join(channels)}
Message: {message}

Status by channel:
{channel_status}

{priority_warning}
"""    
    def as_langchain_tool(self) -> Tool:
        """Convert to LangChain tool."""
        return Tool(
            name="send_notification",
            description="Send notifications to users via multiple channels (email, SMS, push). Supports priority levels.",
            func=lambda x: self.send_notification(**eval(x))
        )
