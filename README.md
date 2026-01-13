<!-- example Interaction -->
User: Set a meeting with John tomorrow
Agent: What time should the meeting start and how long should it be?

User: 3pm for one hour
Agent: What should I call the meeting?

User: Architecture review
Agent: ✅ Event created. Here’s the link:
https://calendar.google.com/...


# Google Calendar Agent

An AI-powered calendar scheduling agent that uses OpenAI's GPT models to interact naturally with users and manage Google Calendar events through a modern web interface.

## Features

- 🤖 Natural language conversation for scheduling
- 📅 Google Calendar integration
- 🌐 Web-based chat interface (Flask)
- ✨ Context-aware multi-turn conversations
- 🔒 Secure OAuth 2.0 authentication
- 💬 Real-time chat interface
- ⚡ Easy setup and configuration

## Prerequisites

- Python 3.10 or higher (for local development)
- Docker and Docker Compose (for containerized deployment)
- Google Cloud Platform account
- OpenAI API key

## Installation

### Option 1: Docker Deployment (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/qheider/google-Calendar-Agent.git
   cd google-Calendar-Agent
   ```

2. **Set up environment variables**
   Create a `.env` file:
   ```bash
   OPENAI_API_KEY=your-openai-api-key-here
   ```

3. **Add Google credentials**
   - Place your `credentials.json` file in the project root
   - Initial authentication will create `token.pickle`

4. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

5. **Access the application**
   - Open browser: http://localhost:5000
   - Or from network: http://[your-ip]:5000

6. **View logs** (optional)
   ```bash
   docker-compose logs -f
   ```

7. **Stop the container**
   ```bash
   docker-compose down
   ```

### Option 2: Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/qheider/google-Calendar-Agent.git
   cd google-Calendar-Agent
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Google Calendar API Setup

1. **Create a Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Google Calendar API**
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

3. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Desktop app" as application type
   - Download the credentials JSON file
   - Rename it to `credentials.json` and place it in the project root

## Configuration

1. **Create `.env` file**
   ```bash
   cp .env.example .env
   ```
   Or create a new `.env` file with:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   ```

2. **Add your OpenAI API key**
   - Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
   - Replace `your-openai-api-key-here` in `.env` with your actual key

## Usage

### Test Google Calendar Connection

First, verify your Google Calendar API setup:
```bash
python calendarTest.py
```

This will:
- Test authentication
- List your calendars
- Show upcoming events

### Run the Flask Web Application

Start the Flask web server:
```bash
python flask_app.py
```

Then open your browser and navigate to:
```
http://localhost:5000
```

You'll see a modern chat interface where you can interact with the calendar agent.

### Alternative: Command Line Interface

If you prefer the CLI version, you can still use:
```bash
python app.py
```

### Example Conversation

```
User: Schedule a meeting with John tomorrow at 3pm for 1 hour
Agent: What would you like to title this meeting?
User: Architecture Review
Agent: Great! I'll schedule "Architecture Review" with John for tomorrow at 3:00 PM to 4:00 PM.
[Event created successfully]
```

### Date/Time Format

The agent accepts natural language, but internally uses ISO 8601 format:
- Format: `YYYY-MM-DDTHH:MM:SS`
- Example: `2025-12-30T15:00:00` (December 30, 2025 at 3:00 PM)

## Project Structure

```
google-Calendar-Agent/
├── flask_app.py           # Flask web application (main)
├── app.py                 # CLI version
├── calendarTest.py        # API connection test
├── templates/             # HTML templates
│   └── index.html        # Chat interface
├── static/               # Static assets
│   └── style.css        # Styles for web interface
├── Dockerfile            # Docker container definition
├── docker-compose.yml    # Docker Compose configuration
├── requirements.txt      # Python dependencies
├── .dockerignore         # Docker ignore rules
├── .env                  # Environment variables (not in git)
├── .gitignore           # Git ignore rules
├── credentials.json      # Google OAuth credentials (not in git)
├── token.pickle         # Cached authentication token (not in git)
└── README.md            # This file
```

## Docker Commands

### Build the Docker image manually
```bash
docker build -t calendar-agent .
```

### Run the container manually
```bash
docker run -d -p 5000:5000 \
  -v $(pwd)/credentials.json:/app/credentials.json:ro \
  -v $(pwd)/token.pickle:/app/token.pickle \
  -v $(pwd)/.env:/app/.env:ro \
  --name calendar-agent \
  calendar-agent
```

### View container logs
```bash
docker logs -f calendar-agent
```

### Stop and remove container
```bash
docker stop calendar-agent
docker rm calendar-agent
```

## Security Notes

⚠️ **Important**: Never commit sensitive files to version control
- `.env` - Contains your OpenAI API key
- `credentials.json` - Google OAuth client secrets
- `client_secret_*.json` - Alternative credential format
- `token.pickle` - Cached authentication tokens

These files are already in `.gitignore` to prevent accidental commits.

## Troubleshooting

### Authentication Issues
- Delete `token.pickle` and re-run to re-authenticate
- Verify `credentials.json` is in the project root
- Check that Google Calendar API is enabled in your Google Cloud project

### Agent Not Remembering Context
- Ensure you're running the latest version of the code
- The conversation history is maintained within a single session
- Restarting the app clears conversation history

### OpenAI API Errors
- Verify your API key in `.env` is correct
- Check your OpenAI account has available credits
- Ensure the model `gpt-4o-mini` is accessible to your account

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
