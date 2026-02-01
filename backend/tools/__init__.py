"""
Tools package for AI agents.
Provides various tools for web search, email, calendar, file operations, etc.
"""

from .web_tools import (
    TavilySearchTool,
    WebScraperTool,
    URLExtractorTool
)
from .email_tools import (
    EmailSenderTool,
    EmailSearchTool,
    EmailAttachmentTool
)
# Real Google API tools
from .gmail_tools import gmail_tools
from .calendar_tools import calendar_tools

from .file_tools import (
    FileReadTool,
    FileWriteTool,
    FileSearchTool
)
from .analysis_tools import (
    DataAnalysisTool,
    SentimentAnalysisTool,
    KeywordExtractionTool
)
from .communication_tools import (
    SlackMessageTool,
    TeamsMessageTool,
    NotificationTool
)

__all__ = [
    # Web tools
    "TavilySearchTool",
    "WebScraperTool",
    "URLExtractorTool",
    # Email tools (legacy)
    "EmailSenderTool",
    "EmailSearchTool",
    "EmailAttachmentTool",
    # Real Google API tools
    "gmail_tools",
    "calendar_tools",
    # File tools
    "FileReadTool",
    "FileWriteTool",
    "FileSearchTool",
    # Analysis tools
    "DataAnalysisTool",
    "SentimentAnalysisTool",
    "KeywordExtractionTool",
    # Communication tools
    "SlackMessageTool",
    "TeamsMessageTool",
    "NotificationTool",
]
