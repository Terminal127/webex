#!/usr/bin/env python3
"""
Simple AI Webex Bot
Communicates with LangChain FastAPI server for AI responses
"""

import os
import time
import requests
from webexteamssdk import WebexTeamsAPI
from datetime import datetime

# Import configuration
try:
    from bot_config import *
    print("✅ Loaded configuration from bot_config.py")
except ImportError:
    print("⚠️  bot_config.py not found, using default settings")
    # Default configuration
    RESPOND_TO_MENTIONS_ONLY = True
    TRIGGER_KEYWORDS = ["jarvis", "bot", "ai", "help"]
    ALLOWED_USERS = []
    PREFERRED_ROOM_NAME = ""  # Leave empty to show room selection menu
    ACCESS_TOKEN = "ZjUzNWFkMDYtMzk5OS00Y2Q3LThhNDctMThjMmRmNjMyNTU0MDFiNTJjNGMtZmQw_PI91_a0b782ec-198d-45d5-956a-0c60451097d6"
    BOT_EMAIL = "jarvis127@webex.bot"
    LANGCHAIN_API_URL = "http://localhost:8000"

class SimpleAIBot:
    def __init__(self, access_token, bot_email):
        """Initialize the simple AI bot"""
        self.api = WebexTeamsAPI(access_token=access_token)
        self.bot_email = bot_email
        self.room_id = None
        self.langchain_api_url = LANGCHAIN_API_URL
        
        # Bot response settings
        self.respond_to_mentions_only = RESPOND_TO_MENTIONS_ONLY
        self.respond_to_keywords = TRIGGER_KEYWORDS
        self.allowed_users = ALLOWED_USERS
        self.preferred_room_name = getattr(globals(), 'PREFERRED_ROOM_NAME', "")
        
    def find_rooms_with_bot(self):
        """Find all rooms with the bot"""
        try:
            rooms = self.api.rooms.list()
            bot_rooms = []
            
            for room in rooms:
                memberships = self.api.memberships.list(roomId=room.id)
                for membership in memberships:
                    if membership.personEmail == self.bot_email:
                        bot_rooms.append(room)
                        break
            
            return bot_rooms
        except Exception as e:
            print(f"❌ Error finding rooms: {e}")
            return []
    
    def select_room(self):
        """Let user select which room to use"""
        bot_rooms = self.find_rooms_with_bot()
        
        if not bot_rooms:
            print(f"❌ No rooms found with bot {self.bot_email}")
            return None
        
        # Check if there's a preferred room configured
        if hasattr(self, 'preferred_room_name') and self.preferred_room_name:
            for room in bot_rooms:
                if room.title and self.preferred_room_name.lower() in room.title.lower():
                    self.room_id = room.id
                    print(f"✅ Using preferred room: {room.title or 'Direct Message'}")
                    return self.room_id
            print(f"⚠️  Preferred room '{self.preferred_room_name}' not found, showing all options...")
        
        if len(bot_rooms) == 1:
            self.room_id = bot_rooms[0].id
            print(f"✅ Using only available room: {bot_rooms[0].title or 'Direct Message'}")
            return self.room_id
        
        # Multiple rooms found - let user choose
        print(f"\n📋 Found {len(bot_rooms)} rooms with bot {self.bot_email}:")
        print("-" * 60)
        
        for i, room in enumerate(bot_rooms, 1):
            # Get member info for context
            try:
                memberships = list(self.api.memberships.list(roomId=room.id))
                member_count = len(memberships)
                
                # Get member names (limit to first 3 to avoid clutter)
                member_names = []
                for membership in memberships[:3]:
                    if membership.personEmail != self.bot_email:  # Skip the bot
                        try:
                            person = self.api.people.get(membership.personId)
                            member_names.append(person.displayName or membership.personEmail.split('@')[0])
                        except:
                            member_names.append(membership.personEmail.split('@')[0])
                
                if len(memberships) > 3:
                    member_info = f"({member_count} members: {', '.join(member_names)}, ...)"
                else:
                    member_info = f"({member_count} members: {', '.join(member_names)})"
                    
            except:
                member_info = ""
            
            print(f"{i}. {room.title or 'Direct Message'} {member_info}")
            print(f"   Type: {room.type}")
            if room.lastActivity:
                print(f"   Last activity: {room.lastActivity.strftime('%Y-%m-%d %H:%M')}")
            print()
        
        while True:
            try:
                choice = input(f"👆 Select room (1-{len(bot_rooms)}) or 'q' to quit: ").strip().lower()
                
                if choice == 'q':
                    print("👋 Goodbye!")
                    return None
                
                room_index = int(choice) - 1
                
                if 0 <= room_index < len(bot_rooms):
                    selected_room = bot_rooms[room_index]
                    self.room_id = selected_room.id
                    print(f"✅ Selected: {selected_room.title or 'Direct Message'}")
                    return self.room_id
                else:
                    print("❌ Invalid choice. Please try again.")
                    
            except ValueError:
                print("❌ Please enter a valid number or 'q' to quit.")
            except KeyboardInterrupt:
                print("\n👋 Cancelled.")
                return None
    
    def send_message(self, message):
        """Send a message to the Webex room"""
        try:
            response = self.api.messages.create(roomId=self.room_id, text=message)
            print(f"✅ Sent: {message}")
            return response
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return None
    
    def get_recent_messages(self, max_messages=5):
        """Get recent messages from the room"""
        try:
            messages = self.api.messages.list(roomId=self.room_id, max=max_messages)
            return list(messages)
        except Exception as e:
            print(f"❌ Error getting messages: {e}")
            return []
    
    def get_ai_response(self, user_message):
        """Get AI response from LangChain API - optimized for speed"""
        try:
            # Use POST request to LangChain API
            payload = {
                "message": user_message,
                "user_id": "webex_user",
                "room_id": self.room_id or "default_room"
            }
            
            response = requests.post(
                f"{self.langchain_api_url}/chat",
                json=payload,
                timeout=20  # Reduced from 30 to 20 seconds
            )
            
            if response.status_code == 200:
                data = response.json()
                raw_response = data.get("bot_response", "Sorry, I couldn't generate a response.")
                # Clean markdown formatting for Webex
                cleaned_response = self.clean_markdown_for_webex(raw_response)
                return cleaned_response
            else:
                return f"I'm having trouble processing that request right now. Please try again."
                
        except requests.exceptions.ConnectionError:
            return "🚫 AI service is not running. Please start the LangChain API server first."
        except requests.exceptions.Timeout:
            return "⏱️ I'm taking too long to respond. Could you try asking in a simpler way?"
        except Exception as e:
            return f"I encountered an issue: {str(e)}. Please try again."
    
    def should_respond_to_message(self, message):
        """Determine if the bot should respond to this message"""
        
        # Don't respond to our own messages
        if message.personEmail == self.bot_email:
            return False
        
        # Check if user is in allowed list (if specified)
        if self.allowed_users and message.personEmail not in self.allowed_users:
            print(f"⏭️  Ignoring message from {message.personEmail} (not in allowed users)")
            return False
        
        # If mentions only mode is enabled
        if self.respond_to_mentions_only:
            # Check if bot is mentioned in the message
            if hasattr(message, 'mentionedPeople') and message.mentionedPeople:
                # Get bot person ID
                try:
                    bot_person = self.api.people.me()
                    if bot_person.id in message.mentionedPeople:
                        print(f"✅ Bot was mentioned by {message.personEmail}")
                        return True
                except Exception as e:
                    print(f"Error checking mentions: {e}")
            
            # Check for keyword triggers
            message_lower = message.text.lower()
            for keyword in self.respond_to_keywords:
                if keyword in message_lower:
                    print(f"✅ Keyword '{keyword}' found in message from {message.personEmail}")
                    return True
            
            print(f"⏭️  Ignoring message from {message.personEmail} (no mention or keywords)")
            return False
        
        # If not mentions-only mode, respond to all allowed users
        print(f"✅ Responding to message from {message.personEmail}")
        return True
    
    def clean_markdown_for_webex(self, text):
        """Clean markdown formatting for better Webex display"""
        import re
        
        # Convert **bold** to just BOLD or remove formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove bold formatting
        
        # Convert *italic* to just text
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        
        # Convert `code` to just text
        text = re.sub(r'`(.*?)`', r'\1', text)
        
        # Convert markdown links [text](url) to "text (url)"
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 (\2)', text)
        
        # Convert ### headers to just text
        text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
        
        # Clean up multiple spaces and newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Keep double line breaks
        text = re.sub(r' +', ' ', text)  # Multiple spaces to single
        
        return text.strip()
    
    def start_auto_response(self):
        """Start automatic AI response mode"""
        print("🤖 Starting AI Auto-Response Mode...")
        print("Bot will automatically respond to user messages using AI.")
        print("Press Ctrl+C to stop.")
        print("-" * 50)
        
        seen_messages = set()
        
        # Get existing messages to avoid responding to old ones
        initial_messages = self.get_recent_messages(10)
        for message in initial_messages:
            seen_messages.add(message.id)
            
        print("✅ Bot is ready and listening for messages...")
        
        try:
            while True:
                current_messages = self.get_recent_messages(5)
                
                for message in reversed(current_messages):
                    # Check if it's a new message and if we should respond
                    if (message.id not in seen_messages and 
                        self.should_respond_to_message(message)):
                        
                        print(f"\n👤 User ({message.personEmail}): {message.text}")
                        
                        # Show typing indicator for longer responses
                        if len(message.text) > 20:  # For longer questions
                            typing_msg = "🤔 Thinking..."
                            typing_response = self.send_message(typing_msg)
                            print(f"💭 Typing indicator sent")
                        
                        # Get AI response
                        ai_response = self.get_ai_response(message.text)
                        print(f"🤖 AI Response: {ai_response}")
                        
                        # Send AI response to Webex
                        self.send_message(ai_response)
                        seen_messages.add(message.id)
                    
                    # Add all messages to seen_messages to avoid processing again
                    if message.id not in seen_messages:
                        seen_messages.add(message.id)
                
                time.sleep(1)  # Check every 1 second instead of 2 for faster response
                
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped.")

def main():
    """Main function"""
    print("🚀 Simple AI Webex Bot")
    print("=" * 30)
    
    # Configuration from bot_config.py
    print(f"🔗 Connecting to Webex Teams...")
    print(f"🤖 Bot email: {BOT_EMAIL}")
    print(f"🌐 LangChain API: {LANGCHAIN_API_URL}")
    
    # Create bot
    bot = SimpleAIBot(ACCESS_TOKEN, BOT_EMAIL)
    
    # Find room with bot
    if not bot.select_room():
        print("❌ No room selected. Exiting.")
        return
    
    # Test LangChain API connection
    try:
        test_response = requests.get(f"{LANGCHAIN_API_URL}/health", timeout=5)
        if test_response.status_code == 200:
            print("✅ LangChain API is running")
        else:
            print("⚠️  LangChain API responded but may have issues")
    except:
        print("❌ LangChain API is not running. Please start it first:")
        print("   python langchain_api.py")
        return
    
    # Configure bot behavior
    print("\n🔧 Bot Configuration:")
    print(f"📧 Responds to mentions only: {bot.respond_to_mentions_only}")
    print(f"🔑 Trigger keywords: {', '.join(bot.respond_to_keywords)}")
    print(f"👥 Allowed users: {'All users' if not bot.allowed_users else ', '.join(bot.allowed_users)}")
    print()
    print("💡 Tip: Bot will only respond when mentioned (@jarvis127) or when keywords are used")
    print("💡 To change this, edit the settings in simple_ai_bot.py")
    
    # Start the bot
    bot.start_auto_response()

if __name__ == "__main__":
    main()
