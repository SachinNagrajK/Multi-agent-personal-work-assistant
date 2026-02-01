"""
Real Gmail tools using Google Gmail API.
Replaces mock email tools with actual Gmail integration.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from langchain.tools import tool
from googleapiclient.errors import HttpError

from google_auth import get_gmail_service


@tool
def gmail_read_recent(max_results: int = 10, query: str = "") -> str:
    """
    Read recent emails from Gmail.
    
    Args:
        max_results: Maximum number of emails to retrieve (default 10)
        query: Gmail search query (e.g., 'is:unread', 'from:boss@company.com', 'subject:urgent')
    
    Returns:
        String containing email details (sender, subject, snippet, date)
    """
    service = get_gmail_service()
    if not service:
        return "❌ Failed to connect to Gmail. Check authentication."
    
    try:
        # Get list of messages
        results = service.users().messages().list(
            userId='me',
            maxResults=max_results,
            q=query
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            return f"No emails found matching query: '{query}'" if query else "No emails found."
        
        email_list = []
        for msg in messages:
            # Get full message details
            message = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='full'
            ).execute()
            
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
            
            snippet = message.get('snippet', '')
            
            email_list.append({
                'id': msg['id'],
                'sender': sender,
                'subject': subject,
                'snippet': snippet,
                'date': date
            })
        
        # Format output
        output = f"Found {len(email_list)} emails:\n\n"
        for i, email in enumerate(email_list, 1):
            output += f"{i}. From: {email['sender']}\n"
            output += f"   Subject: {email['subject']}\n"
            output += f"   Date: {email['date']}\n"
            output += f"   Preview: {email['snippet'][:100]}...\n"
            output += f"   ID: {email['id']}\n\n"
        
        return output
        
    except HttpError as error:
        return f"❌ Gmail API error: {error}"


@tool
def gmail_send_email(to: str, subject: str, body: str, cc: str = "", bcc: str = "") -> str:
    """
    Send an email via Gmail.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body (plain text)
        cc: CC recipients (comma-separated, optional)
        bcc: BCC recipients (comma-separated, optional)
    
    Returns:
        Success or error message
    """
    service = get_gmail_service()
    if not service:
        return "❌ Failed to connect to Gmail. Check authentication."
    
    try:
        # Create message
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        
        if cc:
            message['cc'] = cc
        if bcc:
            message['bcc'] = bcc
        
        # Add body
        message.attach(MIMEText(body, 'plain'))
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Send message
        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return f"✅ Email sent successfully! Message ID: {sent_message['id']}"
        
    except HttpError as error:
        return f"❌ Failed to send email: {error}"


@tool
def gmail_search(query: str, max_results: int = 20) -> str:
    """
    Search Gmail with advanced queries.
    
    Args:
        query: Gmail search query 
               Examples:
               - 'from:boss@company.com'
               - 'subject:meeting AND is:unread'
               - 'has:attachment after:2024/01/01'
               - 'label:urgent OR label:important'
        max_results: Maximum results to return (default 20)
    
    Returns:
        Formatted search results
    """
    return gmail_read_recent(max_results=max_results, query=query)


@tool
def gmail_get_unread_count() -> str:
    """
    Get count of unread emails in inbox.
    
    Returns:
        Number of unread emails
    """
    service = get_gmail_service()
    if not service:
        return "❌ Failed to connect to Gmail."
    
    try:
        results = service.users().messages().list(
            userId='me',
            q='is:unread',
            maxResults=1
        ).execute()
        
        count = results.get('resultSizeEstimate', 0)
        return f"You have {count} unread email(s)."
        
    except HttpError as error:
        return f"❌ Error: {error}"


@tool
def gmail_mark_as_read(message_id: str) -> str:
    """
    Mark an email as read.
    
    Args:
        message_id: Gmail message ID
    
    Returns:
        Success or error message
    """
    service = get_gmail_service()
    if not service:
        return "❌ Failed to connect to Gmail."
    
    try:
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        
        return f"✅ Marked email {message_id} as read."
        
    except HttpError as error:
        return f"❌ Error: {error}"


@tool
def gmail_add_label(message_id: str, label_name: str) -> str:
    """
    Add a label to an email (creates label if doesn't exist).
    
    Args:
        message_id: Gmail message ID
        label_name: Label name (e.g., 'Important', 'Follow-up')
    
    Returns:
        Success or error message
    """
    service = get_gmail_service()
    if not service:
        return "❌ Failed to connect to Gmail."
    
    try:
        # Get all labels
        labels_result = service.users().labels().list(userId='me').execute()
        labels = labels_result.get('labels', [])
        
        # Find or create label
        label_id = None
        for label in labels:
            if label['name'].lower() == label_name.lower():
                label_id = label['id']
                break
        
        if not label_id:
            # Create new label
            new_label = service.users().labels().create(
                userId='me',
                body={'name': label_name, 'labelListVisibility': 'labelShow'}
            ).execute()
            label_id = new_label['id']
        
        # Add label to message
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'addLabelIds': [label_id]}
        ).execute()
        
        return f"✅ Added label '{label_name}' to email {message_id}."
        
    except HttpError as error:
        return f"❌ Error: {error}"


@tool
def gmail_get_email_body(message_id: str) -> str:
    """
    Get full email body by message ID.
    
    Args:
        message_id: Gmail message ID
    
    Returns:
        Full email body text
    """
    service = get_gmail_service()
    if not service:
        return "❌ Failed to connect to Gmail."
    
    try:
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        # Extract body
        if 'parts' in message['payload']:
            parts = message['payload']['parts']
            data = parts[0]['body'].get('data', '')
        else:
            data = message['payload']['body'].get('data', '')
        
        if data:
            body = base64.urlsafe_b64decode(data).decode('utf-8')
        else:
            body = message.get('snippet', 'No body content')
        
        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
        
        output = f"From: {sender}\n"
        output += f"Subject: {subject}\n"
        output += f"Date: {date}\n"
        output += f"\n{'-'*60}\n\n"
        output += body
        
        return output
        
    except HttpError as error:
        return f"❌ Error: {error}"


# Export all tools
gmail_tools = [
    gmail_read_recent,
    gmail_send_email,
    gmail_search,
    gmail_get_unread_count,
    gmail_mark_as_read,
    gmail_add_label,
    gmail_get_email_body,
]
