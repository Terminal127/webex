# Simple AI Bot Configuration
# Edit these settings to control how the bot behaves

# ==== RESPONSE BEHAVIOR ====

# Only respond when mentioned (@botname) or when trigger keywords are used
RESPOND_TO_MENTIONS_ONLY = True

# If you want the bot to respond to ALL messages in the room, set this to False
# Warning: This can be very chatty in busy rooms!
# RESPOND_TO_MENTIONS_ONLY = False

# ==== TRIGGER KEYWORDS ====

# Words that will trigger the bot even without @mention
TRIGGER_KEYWORDS = [
    "jarvis",
    "bot", 
    "ai",
    "help"
]

# ==== USER FILTERING ====

# Specific email addresses the bot should respond to
# Leave empty [] to allow all users
ALLOWED_USERS = []

# Example: Only respond to specific people
# ALLOWED_USERS = [
#     "john.doe@company.com",
#     "jane.smith@company.com"
# ]

# ==== ROOM SELECTION ====

# Preferred room name to automatically connect to
# Leave empty "" to show room selection menu each time
PREFERRED_ROOM_NAME = ""

# Example: Auto-connect to a specific room
# PREFERRED_ROOM_NAME = "My Personal Bot Room"

# ==== CREDENTIALS ====

# Your Webex bot access token
ACCESS_TOKEN = "ZjUzNWFkMDYtMzk5OS00Y2Q3LThhNDctMThjMmRmNjMyNTU0MDFiNTJjNGMtZmQw_PI91_a0b782ec-198d-45d5-956a-0c60451097d6"

# Your bot's email address
BOT_EMAIL = "jarvis127@webex.bot"

# ==== API SETTINGS ====

# LangChain API server URL
LANGCHAIN_API_URL = "http://localhost:8000"
