#!/usr/bin/env python3
"""
LangChain API for Webex Bot
A FastAPI service to provide AI responses for the Webex bot
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import json
from typing import Optional
from datetime import datetime
import uvicorn

# FastAPI App
app = FastAPI(
    title="Webex Bot AI API",
    description="AI-powered responses for Webex bot using LangChain and Gemini",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini Model Setup - Optimized for speed
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.1,  # Lower temperature for faster, more consistent responses
    max_tokens=150,   # Limit response length for speed
    max_retries=1,    # Reduce retries for faster failure handling
    request_timeout=15,  # 15 second timeout instead of default 60
    google_api_key="AIzaSyDsi82MHuNMwZyUoJ5q6xN8yd9Q4yBw5gM",
    convert_system_message_to_human=True
)

# Webex Bot personality prompt template - Optimized for speed
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are Jarvis, a helpful AI assistant in Webex Teams.

    RESPONSE GUIDELINES:
    - Keep responses under 100 words (be concise and direct)
    - Professional but friendly tone
    - No markdown formatting (plain text only)
    - Answer directly without lengthy explanations
    - If you don't know something, say so briefly
    - Use minimal emojis for workplace appropriateness

    CONTEXT: {history}
    """),
    ("human", "{question}")
])

def format_history_for_prompt(history):
    """Format conversation history for the prompt - optimized for speed"""
    if not history:
        return "New conversation"
    
    # Only show last 2 exchanges to keep prompt short and fast
    recent_history = history[-2:]
    formatted = []
    for entry in recent_history:
        formatted.append(f"Q: {entry['question'][:50]}...")  # Truncate long questions
        formatted.append(f"A: {entry['answer'][:50]}...")    # Truncate long answers
    
    return " | ".join(formatted)

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "default_user"
    room_id: Optional[str] = "default_room"

class ChatResponse(BaseModel):
    status: str
    user_message: str
    bot_response: str
    mode: str = "ai"
    timestamp: str

class HistoryResponse(BaseModel):
    status: str
    total_conversations: int
    history: list

class ModeResponse(BaseModel):
    status: str
    current_mode: str
    available_modes: list

# In-memory storage for conversation history by room/user
conversation_histories = {}

@app.get("/")
async def home():
    """Health check endpoint"""
    return {
        "status": "success",
        "service": "Webex Bot AI API",
        "version": "1.0",
        "bot_name": "Jarvis",
        "endpoints": {
            "POST /chat": "Send a message to the AI bot",
            "GET /chat": "Send a message via query parameter",
            "GET /history/{room_id}": "Get conversation history for a room",
            "POST /clear/{room_id}": "Clear conversation history for a room",
            "GET /modes": "Get available bot modes",
            "GET /health": "Detailed health check"
        }
    }

def get_conversation_key(user_id: str, room_id: str) -> str:
    """Generate a unique key for conversation history"""
    return f"{room_id}_{user_id}"

@app.post("/chat", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest):
    """Send a message to the AI bot - optimized for speed"""
    try:
        message = request.message.strip()
        
        if not message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Check for quick responses first (for instant replies)
        quick_response = get_quick_response(message)
        if quick_response:
            return ChatResponse(
                status="success",
                user_message=message,
                bot_response=quick_response,
                mode="quick",
                timestamp=datetime.now().isoformat()
            )
        
        # Get conversation key
        conv_key = get_conversation_key(request.user_id, request.room_id)
        
        # Initialize conversation history if not exists
        if conv_key not in conversation_histories:
            conversation_histories[conv_key] = []
        
        # Format conversation history for the prompt (minimal for speed)
        history_text = format_history_for_prompt(conversation_histories[conv_key])
        
        # Create the prompt with the message and history
        formatted_prompt = prompt.format_messages(
            question=message,
            history=history_text
        )
        
        # Get response from AI model
        response = model.invoke(formatted_prompt)
        bot_response = response.content
        
        # Store in conversation history (keep last 5 exchanges for speed)
        conversation_entry = {
            "question": message,
            "answer": bot_response,
            "timestamp": datetime.now().isoformat()
        }
        conversation_histories[conv_key].append(conversation_entry)
        
        # Keep only last 5 conversations per room/user (reduced from 10)
        if len(conversation_histories[conv_key]) > 5:
            conversation_histories[conv_key].pop(0)
        
        return ChatResponse(
            status="success",
            user_message=message,
            bot_response=bot_response,
            mode="ai",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@app.get("/chat", response_model=ChatResponse)
async def chat_with_bot_get(
    q: str = Query(..., description="The message to send to the bot"),
    user_id: str = Query("default_user", description="User ID"),
    room_id: str = Query("default_room", description="Room ID")
):
    """Send a message to the bot via GET request"""
    request = ChatRequest(message=q, user_id=user_id, room_id=room_id)
    return await chat_with_bot(request)

@app.get("/history/{room_id}", response_model=HistoryResponse)
async def get_room_history(room_id: str, user_id: str = Query("default_user")):
    """Get conversation history for a specific room and user"""
    conv_key = get_conversation_key(user_id, room_id)
    history = conversation_histories.get(conv_key, [])
    
    return HistoryResponse(
        status="success",
        total_conversations=len(history),
        history=history
    )

@app.post("/clear/{room_id}")
async def clear_room_history(room_id: str, user_id: str = Query("default_user")):
    """Clear conversation history for a specific room and user"""
    conv_key = get_conversation_key(user_id, room_id)
    
    if conv_key in conversation_histories:
        conversation_histories[conv_key] = []
    
    return {
        "status": "success",
        "message": f"Conversation history cleared for room {room_id} and user {user_id}"
    }

@app.get("/modes", response_model=ModeResponse)
async def get_available_modes():
    """Get available bot modes"""
    return ModeResponse(
        status="success",
        current_mode="ai",
        available_modes=["manual", "ai", "hybrid"]
    )

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test AI model connectivity
        test_response = model.invoke("Hello")
        ai_status = "connected" if test_response else "disconnected"
    except Exception as e:
        ai_status = f"disconnected: {str(e)}"
    
    return {
        "status": "healthy",
        "service": "Webex Bot AI API",
        "ai_model": {
            "status": ai_status,
            "model": "gemini-2.0-flash",
            "provider": "Google Generative AI"
        },
        "conversations": {
            "active_rooms": len(conversation_histories),
            "total_conversations": sum(len(hist) for hist in conversation_histories.values()),
            "max_stored_per_room": 10
        },
        "features": [
            "AI-powered responses",
            "Conversation memory per room",
            "Webex-optimized personality",
            "Professional tone",
            "Context awareness"
        ]
    }

# Simple cache for fast responses to common questions
QUICK_RESPONSES = {
    "hi": "Hi there! How can I help you?",
    "hello": "Hello! What can I do for you?",
    "hey": "Hey! How can I assist?",
    "help": "I'm here to help! What do you need assistance with?",
    "thanks": "You're welcome!",
    "thank you": "Happy to help!",
    "bye": "Goodbye! 👋",
    "how are you": "I'm doing well, thanks! How can I help you?",
    "what can you do": "I can answer questions, help with tasks, and have conversations. What do you need?",
    "time": "I don't have real-time access, but I can help with other questions!",
    "weather": "I don't have weather data access, but what else can I help with?"
}

def get_quick_response(message):
    """Check if message matches a quick response pattern"""
    message_lower = message.lower().strip()
    
    # Exact matches first
    if message_lower in QUICK_RESPONSES:
        return QUICK_RESPONSES[message_lower]
    
    # Partial matches for common greetings
    for key, response in QUICK_RESPONSES.items():
        if key in message_lower and len(message_lower) < 20:  # Only for short messages
            return response
    
    return None

# Predefined responses for manual mode (fallback)
MANUAL_RESPONSES = {
    "hello": "Hello! I'm Jarvis, your AI assistant. How can I help you today?",
    "hi": "Hi there! I'm here to assist you. What would you like to know?",
    "help": "I can help you with various tasks like answering questions, providing information, or just having a conversation. What do you need assistance with?",
    "what can you do": "I can answer questions, help with work-related tasks, provide information on various topics, and engage in professional conversations. Just ask me anything!",
    "bye": "Goodbye! Feel free to reach out anytime you need assistance.",
    "thanks": "You're welcome! I'm always here to help.",
    "thank you": "My pleasure! Don't hesitate to ask if you need anything else."
}

@app.post("/manual-response")
async def get_manual_response(request: ChatRequest):
    """Get a predefined manual response"""
    message = request.message.lower().strip()
    
    # Find the best matching manual response
    for key, response in MANUAL_RESPONSES.items():
        if key in message:
            return ChatResponse(
                status="success",
                user_message=request.message,
                bot_response=response,
                mode="manual",
                timestamp=datetime.now().isoformat()
            )
    
    # Default response if no match found
    return ChatResponse(
        status="success",
        user_message=request.message,
        bot_response="I understand you're in manual mode. You can ask me about common topics or type 'help' to see what I can assist with.",
        mode="manual",
        timestamp=datetime.now().isoformat()
    )

if __name__ == '__main__':
    print("🤖 Starting Webex Bot AI API with FastAPI...")
    print("🧠 AI Model: Gemini 2.0 Flash")
    print("📡 Available endpoints:")
    print("   GET  /                    - Service information")
    print("   POST /chat               - Chat with AI bot")
    print("   GET  /chat?q=...         - Chat via URL parameter")
    print("   GET  /history/{room_id}  - Get room conversation history")
    print("   POST /clear/{room_id}    - Clear room history")
    print("   POST /manual-response    - Get predefined responses")
    print("   GET  /modes              - Available bot modes")
    print("   GET  /health             - Detailed health check")
    print("   GET  /docs               - Interactive API documentation")
    print("\n💡 Example usage:")
    print("   curl -X POST http://localhost:8000/chat -H 'Content-Type: application/json' -d '{\"message\": \"Hello!\", \"room_id\": \"room123\"}'")
    print("   curl 'http://localhost:8000/chat?q=How are you?&room_id=room123'")
    print("\n🌐 Server running on: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
