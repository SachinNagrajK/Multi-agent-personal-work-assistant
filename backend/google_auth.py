"""
Google API OAuth authentication utility.
Handles OAuth flow, token storage, and service initialization.
"""
import os
import pickle
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# OAuth scopes - defines what access we're requesting
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive.file',
]

# Token storage path
TOKEN_PATH = Path(__file__).parent / 'token.pickle'
CREDENTIALS_PATH = Path(__file__).parent / 'credentials.json'


def get_credentials() -> Optional[Credentials]:
    """
    Get valid user credentials from storage or run OAuth flow.
    
    Returns:
        Valid credentials or None if credentials.json is missing
    """
    creds = None
    
    # Load existing token
    if TOKEN_PATH.exists():
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh expired token
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            # Run OAuth flow
            if not CREDENTIALS_PATH.exists():
                print("\n❌ ERROR: credentials.json not found!")
                print("Please follow the setup instructions in GOOGLE_SETUP_GUIDE.md")
                return None
            
            print("\n🔐 Starting OAuth flow (Manual Method)...")
            print("=" * 70)
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_PATH), 
                SCOPES,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob'  # Out-of-band flow
            )
            
            # Get authorization URL
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            print("\n📋 STEPS:")
            print("1. Copy the URL below")
            print("2. Open it in your browser")
            print("3. Sign in and authorize the app")
            print("4. Google will show you a CODE")
            print("5. Copy that code and paste it below")
            print("\n" + "=" * 70)
            print(f"\nURL:\n{auth_url}\n")
            print("=" * 70)
            
            code = input("\nPaste the authorization code here: ").strip()
            
            if not code:
                print("❌ No code provided. Aborting.")
                return None
            
            try:
                flow.fetch_token(code=code)
                creds = flow.credentials
            except Exception as e:
                print(f"❌ Failed to get token: {e}")
                return None
        
        # Save credentials for next run
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
        print("✅ Credentials saved successfully!")
    
    return creds


def get_gmail_service():
    """Get authenticated Gmail API service."""
    creds = get_credentials()
    if not creds:
        return None
    
    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except HttpError as error:
        print(f"❌ Error creating Gmail service: {error}")
        return None


def get_calendar_service():
    """Get authenticated Google Calendar API service."""
    creds = get_credentials()
    if not creds:
        return None
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except HttpError as error:
        print(f"❌ Error creating Calendar service: {error}")
        return None


def get_drive_service():
    """Get authenticated Google Drive API service."""
    creds = get_credentials()
    if not creds:
        return None
    
    try:
        service = build('drive', 'v3', credentials=creds)
        return service
    except HttpError as error:
        print(f"❌ Error creating Drive service: {error}")
        return None


def test_gmail_connection():
    """Test Gmail API connection by fetching profile."""
    service = get_gmail_service()
    if not service:
        return False
    
    try:
        profile = service.users().getProfile(userId='me').execute()
        print(f"\n✅ Gmail connected!")
        print(f"   Email: {profile['emailAddress']}")
        print(f"   Total messages: {profile['messagesTotal']}")
        return True
    except HttpError as error:
        print(f"❌ Gmail connection failed: {error}")
        return False


def test_calendar_connection():
    """Test Calendar API connection by listing calendars."""
    service = get_calendar_service()
    if not service:
        return False
    
    try:
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        print(f"\n✅ Calendar connected!")
        print(f"   Found {len(calendars)} calendar(s)")
        for cal in calendars[:3]:  # Show first 3
            print(f"   - {cal['summary']}")
        return True
    except HttpError as error:
        print(f"❌ Calendar connection failed: {error}")
        return False


def test_all_connections():
    """Test all Google API connections."""
    print("=" * 60)
    print("Testing Google API Connections")
    print("=" * 60)
    
    gmail_ok = test_gmail_connection()
    calendar_ok = test_calendar_connection()
    
    print("\n" + "=" * 60)
    if gmail_ok and calendar_ok:
        print("✅ All connections successful!")
        print("=" * 60)
        return True
    else:
        print("❌ Some connections failed. Check the errors above.")
        print("=" * 60)
        return False


if __name__ == "__main__":
    # Run connection tests
    test_all_connections()
