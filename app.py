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

calendar_agent = Agent(
    name="Calendar Agent",
    instructions="""
You are a scheduling agent.

Behavior rules:
- Talk naturally with the user
- Ask questions if date, time, or duration are missing
- Never create an event until you have:
  title, start_time, end_time
- Once ready, call the calendar tool
- Confirm the result
""",
    tools=[
        schedule_calendar_event
    ],
    model="gpt-4.1",
)

while True:
    user_input = input("User: ")
    if user_input.lower() in {"exit", "quit"}:
        break

    result = Runner.run_sync(
        starting_agent=calendar_agent,
        input=user_input
    )

    print("Agent:", result.final_output)

# async def joke_teller():
#     result = await Runner.run(
#         starting_agent=calendar_agent,
#         input="tell me a joke"
#     )
#     print("\n🎭 Joke Result:")
#     print(result.final_output)
#     return result

# async def main():
#     with trace("Calendar Agent"):
#         result = await joke_teller()
#         print("\n✅ Agent execution completed")

# if __name__ == "__main__":
#     asyncio.run(main())
