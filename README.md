# Simple AI-Powered Webex Bot

A minimal Webex bot that uses LangChain and Google's Gemini AI to automatically respond to user messages in Webex Teams rooms.

## Architecture

- **LangChain FastAPI Server** (`langchain_api.py`): Serves AI responses via HTTP API
- **Simple AI Bot** (`simple_ai_bot.py`): Listens to Webex messages and forwards them to the AI API
- **Startup Script** (`simple_start.py`): Convenience script to start both services

## Features

- ✅ **Pure AI Mode**: No manual controls, just intelligent responses
- ✅ **Automatic Message Detection**: Responds only to user messages (not bot's own)
- ✅ **Error Handling**: Graceful handling of API timeouts and connection issues
- ✅ **Simple Setup**: One command to start everything

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure the Bot

Edit `simple_ai_bot.py` and update these values:
- `ACCESS_TOKEN`: Your Webex bot token
- `BOT_EMAIL`: Your bot's email address

Edit `langchain_api.py` and update:
- `google_api_key`: Your Google AI API key

### 3. Create a Webex Room

1. Go to Webex Teams
2. Create a new room or use an existing one
3. Add your bot to the room (using the bot's email)

### 4. Start the Bot

#### Option A: Use the startup script (recommended)
```bash
python simple_start.py
```

#### Option B: Start manually
1. Start the API server:
   ```bash
   python langchain_api.py
   ```
2. In another terminal, start the bot:
   ```bash
   python simple_ai_bot.py
   ```

## How It Works

1. **Message Detection**: Bot continuously monitors the Webex room for new messages
2. **User Filter**: Only responds to messages from users (not from itself)
3. **AI Processing**: Sends user messages to the LangChain API via HTTP POST
4. **Response**: Sends AI-generated response back to the Webex room

## API Endpoints

The LangChain API server provides:

- `POST /chat`: Generate AI responses
  ```json
  {
    "message": "User's message",
    "user_id": "webex_user",
    "room_id": "room_id"
  }
  ```

- `GET /health`: Health check endpoint

## Configuration

### Bot Personality
The AI personality is configured in `langchain_api.py`. The bot (Jarvis) is set to be:
- Professional but friendly
- Concise (under 200 words)
- Workplace-appropriate
- Helpful with various tasks

### Message Polling
The bot checks for new messages every 2 seconds. This can be adjusted in `simple_ai_bot.py`.

## Prerequisites

- Python 3.6 or higher
- A Webex Teams account
- A Webex Teams access token
- A bot to chat with (email address)
- Google AI API key for Gemini

## Troubleshooting

### "LangChain API is not running"
- Make sure `langchain_api.py` is running on port 8000
- Check if another service is using port 8000

### "No rooms found with bot"
- Ensure the bot is added to at least one Webex room
- Verify the bot email is correct

### API timeouts
- The bot waits 30 seconds for AI responses
- If Gemini API is slow, responses may timeout

## File Structure

```
webex/
├── simple_ai_bot.py      # Main bot logic
├── langchain_api.py      # LangChain FastAPI server  
├── simple_start.py       # Startup script
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## Dependencies

- `webexteamssdk`: Webex Teams integration
- `requests`: HTTP client for API calls
- `fastapi`: Web framework for the AI API
- `uvicorn`: ASGI server
- `langchain`: LLM framework
- `langchain-google-genai`: Google Gemini integration

## Security Notes

- Keep your Webex bot token secure
- Keep your Google AI API key secure
- The API runs on localhost by default (not exposed externally)

## Customization

### Change AI Model
Edit `langchain_api.py` to use a different model:
```python
model = ChatGoogleGenerativeAI(model="gemini-pro")  # or other models
```

### Modify Bot Personality
Update the system prompt in `langchain_api.py`:
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "Your custom bot personality..."),
    ("human", "{message}")
])
```

### Adjust Polling Frequency
Change the sleep interval in `simple_ai_bot.py`:
```python
time.sleep(1)  # Check every 1 second instead of 2
```

# You see live conversation:
[14:30:15] You: Hello
[14:30:17] 👤 User: Hi there! Can you help me?
[14:30:20] You: Of course! What do you need help with?
```

## API Endpoints

The LangChain API provides these endpoints:

- `GET /` - Service information
- `POST /chat` - Send message to AI bot
- `GET /chat?q=message` - Quick chat via URL
- `GET /history/{room_id}` - Get conversation history
- `POST /clear/{room_id}` - Clear room history
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

## Getting Started

1. **Get your credentials:**
   - Webex Access Token: [Webex for Developers](https://developer.webex.com/docs/getting-started)
   - Google AI API Key: [Google AI Studio](https://makersuite.google.com/app/apikey)

2. **Install and run:**
   ```bash
   pip install -r requirements.txt
   python simple_start.py
   ```

3. **Add your bot to a Webex room and start chatting!**

The bot will automatically respond to all user messages with AI-generated responses.

## License

This project is open source and available under the MIT License.
