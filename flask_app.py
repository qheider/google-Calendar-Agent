from flask import Flask, render_template, request, jsonify, session
from openai import OpenAI
from agents import Agent, Runner, function_tool
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os.path
import pickle
import secrets
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# OpenAI client
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
    """Schedule a calendar event with the given details."""
    link = create_event(
        summary=title,
        start_iso=start_time,
        end_iso=end_time,
        attendees=attendees,
    )
    return {"event_link": link}


def create_calendar_agent():
    """Create and return the calendar agent with configured tools and instructions."""
    # Get current date and time for context
    current_datetime = datetime.now()
    current_date_str = current_datetime.strftime("%A, %B %d, %Y")
    current_time_str = current_datetime.strftime("%I:%M %p")
    
    return Agent(
        name="Calendar Agent",
        instructions=f"""
You are a scheduling agent.

IMPORTANT CONTEXT:
- Today is: {current_date_str}
- Current time is: {current_time_str}
- Use this information to understand relative dates like "tomorrow", "next week", "today", etc.

Behavior rules:
- Talk naturally with the user
- Understand relative dates (tomorrow, today, next Monday, etc.) based on the current date above
- Ask questions if date, time, or duration are missing
- Make sure date and time indicate current or future date and time (not past)
- Never create an event until you have:
  title, start_time, end_time (in ISO 8601 format: YYYY-MM-DDTHH:MM:SS)
- Once ready, call the calendar tool
- Confirm the result with the user
""",
        tools=[
            schedule_calendar_event
        ],
        model="gpt-4o-mini",
    )


@app.route('/')
def index():
    """Render the main chat interface."""
    # Initialize session conversation history
    if 'conversation_history' not in session:
        session['conversation_history'] = []
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages from the user."""
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Get or initialize conversation history
    if 'conversation_history' not in session:
        session['conversation_history'] = []
    
    conversation_history = session['conversation_history']
    
    # Add user message to history
    conversation_history.append({"role": "user", "content": user_message})
    
    # Create context from history
    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
    
    try:
        # Create agent and run
        calendar_agent = create_calendar_agent()
        result = Runner.run_sync(
            starting_agent=calendar_agent,
            input=context
        )
        
        response = result.final_output
        
        # Add agent response to history
        conversation_history.append({"role": "assistant", "content": response})
        
        # Save updated history to session
        session['conversation_history'] = conversation_history
        session.modified = True
        
        return jsonify({
            'response': response,
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@app.route('/clear', methods=['POST'])
def clear_conversation():
    """Clear the conversation history."""
    session['conversation_history'] = []
    session.modified = True
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
