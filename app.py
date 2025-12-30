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

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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
- Confirm the result
""",
        tools=[
            schedule_calendar_event
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
