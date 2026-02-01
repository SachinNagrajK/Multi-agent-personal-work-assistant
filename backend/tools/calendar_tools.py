"""
Real Google Calendar tools using Google Calendar API.
Replaces mock calendar tools with actual Calendar integration.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from langchain.tools import tool
from googleapiclient.errors import HttpError

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from google_auth import get_calendar_service


@tool
def calendar_list_events(days_ahead: int = 7, max_results: int = 20) -> str:
    """
    List upcoming calendar events.
    
    Args:
        days_ahead: Number of days to look ahead (default 7)
        max_results: Maximum number of events to return (default 20)
    
    Returns:
        Formatted list of calendar events
    """
    service = get_calendar_service()
    if not service:
        return "❌ Failed to connect to Google Calendar."
    
    try:
        # Get current time and end time
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        end_time = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'
        
        # Call the Calendar API
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=end_time,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return f"No upcoming events found in the next {days_ahead} days."
        
        output = f"Found {len(events)} upcoming events:\n\n"
        for i, event in enumerate(events, 1):
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            summary = event.get('summary', 'No Title')
            location = event.get('location', 'No location')
            description = event.get('description', 'No description')
            
            output += f"{i}. {summary}\n"
            output += f"   When: {start}\n"
            output += f"   Duration: {start} to {end}\n"
            output += f"   Where: {location}\n"
            if description != 'No description':
                output += f"   Notes: {description[:100]}...\n"
            output += f"   ID: {event['id']}\n\n"
        
        return output
        
    except HttpError as error:
        return f"❌ Calendar API error: {error}"


@tool
def calendar_create_event(
    summary: str,
    start_time: str,
    end_time: str,
    description: str = "",
    location: str = "",
    attendees: str = ""
) -> str:
    """
    Create a new calendar event.
    
    Args:
        summary: Event title/summary
        start_time: Start time in ISO format (e.g., '2024-01-31T10:00:00')
        end_time: End time in ISO format (e.g., '2024-01-31T11:00:00')
        description: Event description (optional)
        location: Event location (optional)
        attendees: Comma-separated email addresses (optional)
    
    Returns:
        Success message with event details
    """
    service = get_calendar_service()
    if not service:
        return "❌ Failed to connect to Google Calendar."
    
    try:
        # Build event body
        event = {
            'summary': summary,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'America/New_York',  # Adjust to your timezone
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'America/New_York',
            },
        }
        
        # Add attendees if provided
        if attendees:
            email_list = [email.strip() for email in attendees.split(',')]
            event['attendees'] = [{'email': email} for email in email_list]
        
        # Create event
        created_event = service.events().insert(
            calendarId='primary',
            body=event
        ).execute()
        
        return f"✅ Event created successfully!\n" \
               f"   Title: {summary}\n" \
               f"   When: {start_time} to {end_time}\n" \
               f"   Event ID: {created_event['id']}\n" \
               f"   Link: {created_event.get('htmlLink', 'N/A')}"
        
    except HttpError as error:
        return f"❌ Failed to create event: {error}"


@tool
def calendar_find_free_slots(date: str, duration_minutes: int = 60) -> str:
    """
    Find free time slots on a specific date.
    
    Args:
        date: Date to check in YYYY-MM-DD format (e.g., '2024-01-31')
        duration_minutes: Required duration in minutes (default 60)
    
    Returns:
        List of available time slots
    """
    service = get_calendar_service()
    if not service:
        return "❌ Failed to connect to Google Calendar."
    
    try:
        # Parse date and create time range
        start_date = datetime.strptime(date, '%Y-%m-%d')
        start_time = start_date.replace(hour=9, minute=0)  # Start at 9 AM
        end_time = start_date.replace(hour=17, minute=0)   # End at 5 PM
        
        # Get events for that day
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_time.isoformat() + 'Z',
            timeMax=end_time.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Find free slots
        free_slots = []
        current_time = start_time
        
        for event in events:
            event_start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')).replace('Z', '+00:00'))
            
            # If there's a gap before this event
            if (event_start - current_time).total_seconds() / 60 >= duration_minutes:
                free_slots.append({
                    'start': current_time.strftime('%H:%M'),
                    'end': event_start.strftime('%H:%M')
                })
            
            # Move current time to end of this event
            event_end = datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')).replace('Z', '+00:00'))
            current_time = max(current_time, event_end)
        
        # Check for free time at end of day
        if (end_time - current_time).total_seconds() / 60 >= duration_minutes:
            free_slots.append({
                'start': current_time.strftime('%H:%M'),
                'end': end_time.strftime('%H:%M')
            })
        
        if not free_slots:
            return f"No free slots of {duration_minutes} minutes found on {date}."
        
        output = f"Found {len(free_slots)} free slots on {date}:\n\n"
        for i, slot in enumerate(free_slots, 1):
            output += f"{i}. {slot['start']} - {slot['end']}\n"
        
        return output
        
    except HttpError as error:
        return f"❌ Error: {error}"
    except ValueError as e:
        return f"❌ Invalid date format. Use YYYY-MM-DD (e.g., '2024-01-31')"


@tool
def calendar_update_event(event_id: str, summary: str = None, start_time: str = None, end_time: str = None) -> str:
    """
    Update an existing calendar event.
    
    Args:
        event_id: Calendar event ID
        summary: New event title (optional)
        start_time: New start time in ISO format (optional)
        end_time: New end time in ISO format (optional)
    
    Returns:
        Success or error message
    """
    service = get_calendar_service()
    if not service:
        return "❌ Failed to connect to Google Calendar."
    
    try:
        # Get existing event
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        
        # Update fields
        if summary:
            event['summary'] = summary
        if start_time:
            event['start']['dateTime'] = start_time
        if end_time:
            event['end']['dateTime'] = end_time
        
        # Update event
        updated_event = service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=event
        ).execute()
        
        return f"✅ Event updated successfully!\n" \
               f"   Title: {updated_event['summary']}\n" \
               f"   When: {updated_event['start']['dateTime']} to {updated_event['end']['dateTime']}"
        
    except HttpError as error:
        return f"❌ Failed to update event: {error}"


@tool
def calendar_delete_event(event_id: str) -> str:
    """
    Delete a calendar event.
    
    Args:
        event_id: Calendar event ID
    
    Returns:
        Success or error message
    """
    service = get_calendar_service()
    if not service:
        return "❌ Failed to connect to Google Calendar."
    
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return f"✅ Event {event_id} deleted successfully."
        
    except HttpError as error:
        return f"❌ Failed to delete event: {error}"


@tool
def calendar_get_today_schedule() -> str:
    """
    Get today's calendar schedule.
    
    Returns:
        Formatted list of today's events
    """
    service = get_calendar_service()
    if not service:
        return "❌ Failed to connect to Google Calendar."
    
    try:
        # Get today's date range
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=today_start.isoformat() + 'Z',
            timeMax=today_end.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return "📅 No events scheduled for today. Your day is free!"
        
        output = f"📅 Today's Schedule ({len(events)} events):\n\n"
        for i, event in enumerate(events, 1):
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No Title')
            location = event.get('location', '')
            
            # Parse time for better formatting
            try:
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                time_str = start_dt.strftime('%I:%M %p')
            except:
                time_str = start
            
            output += f"{i}. {time_str} - {summary}"
            if location:
                output += f" ({location})"
            output += "\n"
        
        return output
        
    except HttpError as error:
        return f"❌ Error: {error}"


# Export all tools
calendar_tools = [
    calendar_list_events,
    calendar_create_event,
    calendar_find_free_slots,
    calendar_update_event,
    calendar_delete_event,
    calendar_get_today_schedule,
]
