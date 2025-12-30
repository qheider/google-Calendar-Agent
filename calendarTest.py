"""
Test script to verify Google Calendar API setup and authentication.
"""
import os.path
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime

# Google Calendar API setup
SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_calendar_service():
    """Authenticate and return Google Calendar service."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('calendar', 'v3', credentials=creds)


def test_calendar_service():
    """Test the Google Calendar API connection."""
    print("=" * 60)
    print("Google Calendar API Test")
    print("=" * 60)
    
    try:
        # Test authentication
        print("\n1. Testing authentication...")
        service = get_calendar_service()
        print("   ✓ Authentication successful!")
        
        # Test API access by getting calendar list
        print("\n2. Fetching calendar list...")
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        
        if calendars:
            print(f"   ✓ Found {len(calendars)} calendar(s):")
            for calendar in calendars:
                print(f"     - {calendar['summary']} (ID: {calendar['id']})")
        else:
            print("   ⚠ No calendars found")
        
        # Test getting upcoming events
        print("\n3. Fetching upcoming events from primary calendar...")
        now = datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=5,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        
        if events:
            print(f"   ✓ Found {len(events)} upcoming event(s):")
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(f"     - {event['summary']} (Start: {start})")
        else:
            print("   ℹ No upcoming events found")
        
        print("\n" + "=" * 60)
        print("✓ All tests passed! Google Calendar API is working properly.")
        print("=" * 60)
        
        return True
        
    except FileNotFoundError as e:
        print(f"\n✗ Error: credentials.json file not found!")
        print("  Please download your OAuth 2.0 credentials from Google Cloud Console")
        print("  and save it as 'credentials.json' in this directory.")
        return False
        
    except Exception as e:
        print(f"\n✗ Error occurred: {type(e).__name__}")
        print(f"  Details: {str(e)}")
        return False


if __name__ == "__main__":
    test_calendar_service()
