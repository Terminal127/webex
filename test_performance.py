#!/usr/bin/env python3
"""
Performance Test Script for Webex Bot API
Tests response times for different types of messages
"""

import requests
import time
import json

API_URL = "http://localhost:8000"

def test_response_time(message, test_name):
    """Test response time for a specific message"""
    print(f"\n🧪 Testing: {test_name}")
    print(f"📝 Message: {message}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={
                "message": message,
                "user_id": "test_user",
                "room_id": "test_room"
            },
            timeout=30
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            bot_response = data.get("bot_response", "")
            mode = data.get("mode", "")
            
            print(f"⏱️  Response time: {response_time:.2f} seconds")
            print(f"🤖 Bot response: {bot_response}")
            print(f"🏷️  Mode: {mode}")
            
            # Performance rating
            if response_time < 1:
                rating = "🟢 Excellent"
            elif response_time < 3:
                rating = "🟡 Good"
            elif response_time < 5:
                rating = "🟠 Fair"
            else:
                rating = "🔴 Slow"
            
            print(f"📊 Performance: {rating}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        end_time = time.time()
        print(f"❌ Request failed: {e}")
        print(f"⏱️  Time to failure: {end_time - start_time:.2f} seconds")

def main():
    """Run performance tests"""
    print("🚀 Webex Bot Performance Test")
    print("=" * 50)
    
    # Test if API is running
    try:
        health_response = requests.get(f"{API_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ API is running")
        else:
            print("⚠️  API responded but may have issues")
    except:
        print("❌ API is not running. Please start it first:")
        print("   python langchain_api.py")
        return
    
    # Test cases
    test_cases = [
        ("hi", "Quick Response Test (cached)"),
        ("hello", "Another Quick Response"),
        ("What is the weather like?", "Medium Complexity Question"),
        ("Can you explain quantum computing in simple terms?", "Complex Question"),
        ("help", "Help Request (cached)"),
        ("How are you doing today?", "Conversational Question")
    ]
    
    total_start = time.time()
    
    for message, test_name in test_cases:
        test_response_time(message, test_name)
        time.sleep(1)  # Small delay between tests
    
    total_end = time.time()
    
    print(f"\n📈 Total test time: {total_end - total_start:.2f} seconds")
    print(f"🧪 Tests completed: {len(test_cases)}")
    print(f"⚡ Average time per test: {(total_end - total_start) / len(test_cases):.2f} seconds")
    
    print("\n💡 Performance Tips:")
    print("   • Quick responses (hi, hello, help) should be < 1 second")
    print("   • AI responses should be < 5 seconds")
    print("   • If responses are slow, check your internet connection")
    print("   • The first AI response may be slower due to model initialization")

if __name__ == "__main__":
    main()
