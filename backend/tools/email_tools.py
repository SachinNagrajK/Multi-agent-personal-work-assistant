"""
Email operation tools for agents.
"""

from typing import Dict, List, Any, Optional
from langchain.tools import Tool
from datetime import datetime
import re


class EmailSenderTool:
    """
    Send emails via Gmail API (simulated for demo).
    """
    
    def send_email(self, to: str, subject: str, body: str, cc: Optional[str] = None) -> str:
        """
        Send an email.
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            cc: CC recipients (comma-separated)
            
        Returns:
            Status message
        """
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, to):
            return f"Error: Invalid email address '{to}'"
        
        # In production, this would use Gmail API
        # For demo, we simulate the send
        result = {
            "status": "sent",
            "to": to,
            "subject": subject,
            "cc": cc,
            "timestamp": datetime.now().isoformat(),
            "message_id": f"msg_{datetime.now().timestamp()}"
        }
        
        return f"✓ Email sent successfully!\nTo: {to}\nSubject: {subject}\nMessage ID: {result['message_id']}"
    
    def as_langchain_tool(self) -> Tool:
        """Convert to LangChain tool."""
        return Tool(
            name="send_email",
            description="Send an email to a recipient. Requires: to (email address), subject, body. Optional: cc.",
            func=lambda x: self.send_email(**eval(x))
        )


class EmailSearchTool:
    """
    Search emails by criteria.
    """
    
    def search_emails(self, query: str, max_results: int = 10) -> str:
        """
        Search emails by query.
        
        Args:
            query: Search query (subject, from, keywords)
            max_results: Maximum results to return
            
        Returns:
            Matching emails
        """
        # In production, this would search Gmail API
        # For demo, return simulated results
        return f"""
Found 3 emails matching '{query}':

1. From: john@company.com
   Subject: Re: {query}
   Date: 2026-01-30 14:30
   Snippet: Following up on our discussion about {query}...

2. From: sarah@company.com
   Subject: {query} - Update
   Date: 2026-01-29 09:15
   Snippet: Quick update regarding the {query} project...

3. From: team@company.com
   Subject: Weekly {query} Report
   Date: 2026-01-28 16:00
   Snippet: This week's {query} metrics show...
"""
    
    def as_langchain_tool(self) -> Tool:
        """Convert to LangChain tool."""
        return Tool(
            name="search_emails",
            description="Search for emails by keyword, sender, or subject. Returns matching emails with snippets.",
            func=self.search_emails
        )


class EmailAttachmentTool:
    """
    Handle email attachments.
    """
    
    def list_attachments(self, email_id: str) -> str:
        """
        List attachments in an email.
        
        Args:
            email_id: Email message ID
            
        Returns:
            List of attachments
        """
        # Simulated attachment list
        return f"""
Attachments in email {email_id}:

1. quarterly_report.pdf (2.3 MB)
   - Type: application/pdf
   - Preview: Available

2. budget_analysis.xlsx (890 KB)
   - Type: application/vnd.ms-excel
   - Preview: Available

3. team_photo.jpg (1.5 MB)
   - Type: image/jpeg
   - Preview: Available
"""
    
    def download_attachment(self, email_id: str, attachment_name: str) -> str:
        """
        Download an email attachment.
        
        Args:
            email_id: Email message ID
            attachment_name: Name of attachment to download
            
        Returns:
            Download status
        """
        return f"✓ Downloaded '{attachment_name}' from email {email_id}\nSaved to: ./downloads/{attachment_name}"
    
    def as_langchain_tool(self) -> Tool:
        """Convert to LangChain tool."""
        return Tool(
            name="email_attachments",
            description="List or download email attachments. Use email_id to specify which email.",
            func=self.list_attachments
        )
