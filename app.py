from openai import OpenAI
import asyncio
from agents import Agent, Runner, function_tool, trace
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os.path
import pickle
from typing import List, Optional
from datetime import datetime, timezone
import calendar
import logging

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Google Calendar API setup
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Logger setup
logger = logging.getLogger(__name__)

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

def create_event(summary: str, start_iso: str, end_iso: str, attendees: list[str] | None = None) -> str:
    """Create a Google Calendar event and return the event link."""
    service = get_calendar_service()
    
    event = {
        'summary': summary,
        'start': {
            'dateTime': start_iso,
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_iso,
            'timeZone': 'UTC',
        },
    }
    
    if attendees:
        event['attendees'] = [{'email': email} for email in attendees]
    
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return created_event.get('htmlLink', 'Event created successfully')

@function_tool
def schedule_calendar_event(
    title: str,
    start_time: str,
    end_time: str,
    attendees: list[str] | None = None,
) -> dict:
    link = create_event(
        summary=title,
        start_iso=start_time,
        end_iso=end_time,
        attendees=attendees,
    )
    return {"event_link": link}

@function_tool
def list_calendar_meetings(
    period: Optional[str] = "current_month",
    start_iso: Optional[str] = None,
    end_iso: Optional[str] = None,
    max_results: int = 250,
) -> dict:
    """
    List calendar events for a period.

    - If start_iso and end_iso are provided, they are used as the time range (ISO 8601, UTC).
    - Otherwise, if period == "current_month" (default), returns events for the current month (UTC).
    - Returns a dictionary with count and list of events (summary, start, end, attendees, link, id).
    """
    try:
        # Compute current-month range if no explicit range given
        if not start_iso and not end_iso:
            if period == "current_month":
                now = datetime.now(timezone.utc)
                year = now.year
                month = now.month
                first_day = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)
                last_day_num = calendar.monthrange(year, month)[1]
                last_day = datetime(year, month, last_day_num, 23, 59, 59, tzinfo=timezone.utc)
                start_iso = first_day.isoformat()
                end_iso = last_day.isoformat()
            else:
                raise ValueError("Either provide start_iso/end_iso or use period='current_month'")

        logger.info(f"Listing events from {start_iso} to {end_iso}")

        service = get_calendar_service()

        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=start_iso,
                timeMax=end_iso,
                singleEvents=True,
                orderBy="startTime",
                maxResults=max_results,
            )
            .execute()
        )

        items = events_result.get("items", [])
        events: List[dict] = []

        for ev in items:
            start = ev.get("start", {})
            end = ev.get("end", {})

            # support both dateTime (timed events) and date (all-day)
            start_val = start.get("dateTime") or start.get("date")
            end_val = end.get("dateTime") or end.get("date")

            attendees = []
            for a in ev.get("attendees", []):
                attendees.append({
                    "email": a.get("email"),
                    "responseStatus": a.get("responseStatus")
                })

            events.append({
                "id": ev.get("id"),
                "summary": ev.get("summary"),
                "start": start_val,
                "end": end_val,
                "attendees": attendees,
                "htmlLink": ev.get("htmlLink"),
                "created": ev.get("created"),
                "updated": ev.get("updated"),
            })

        return {"count": len(events), "events": events}

    except Exception as e:
        logger.exception("Failed to list calendar meetings")
        return {"error": str(e), "count": 0, "events": []}

def create_calendar_agent():
    """Create and return the calendar agent with configured tools and instructions."""
    return Agent(
        name="Calendar Agent",
        instructions="""
You are a scheduling agent.

Behavior rules:
- Talk naturally with the user
- Ask questions if date, time, or duration are missing
- make sure date, time indicate current or future date, time (not past) 
- Never create an event until you have:
  title, start_time, end_time (in ISO 8601 format: YYYY-MM-DDTHH:MM:SS)
- Once ready, call the calendar tool
- You can also list meetings in a time range using list_calendar_meetings
- When listing meetings, default to current month if no range is specified
- Confirm the result
""",
        tools=[
            schedule_calendar_event,
            list_calendar_meetings
        ],
        model="gpt-4o-mini",
    )


def main():
    """Main function to run the calendar agent in an interactive loop."""
    calendar_agent = create_calendar_agent()
    conversation_history = []
    
    print("Google Calendar Agent")
    print("=" * 50)
    print("Type 'exit' or 'quit' to end the conversation.\n")
    
    while True:
        user_input = input("User: ")
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        # Add user message to history
        conversation_history.append({"role": "user", "content": user_input})
        
        # Create context from history
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
        
        result = Runner.run_sync(
            starting_agent=calendar_agent,
            input=context
        )

        response = result.final_output
        print("Agent:", response)
        
        # Add agent response to history
        conversation_history.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
