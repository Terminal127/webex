#!/usr/bin/env python3
"""
Simple Startup Script for AI Webex Bot
Starts both the LangChain API server and the Webex bot
"""

import subprocess
import time
import sys
import requests
from pathlib import Path

def check_port(port, service_name):
    """Check if a service is running on the given port"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=2)
        if response.status_code == 200:
            print(f"✅ {service_name} is already running on port {port}")
            return True
    except:
        pass
    return False

def start_langchain_api():
    """Start the LangChain API server"""
    print("🚀 Starting LangChain API server...")
    try:
        # Start the API server as a subprocess
        process = subprocess.Popen([
            sys.executable, "langchain_api.py"
        ], cwd=Path(__file__).parent)
        
        # Wait for the server to start
        for i in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            if check_port(8000, "LangChain API"):
                return process
            print(f"⏳ Waiting for API server to start... ({i+1}/30)")
        
        print("❌ API server failed to start within 30 seconds")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        return None

def start_webex_bot():
    """Start the Webex bot"""
    print("\n🤖 Starting Webex AI Bot...")
    try:
        subprocess.run([sys.executable, "simple_ai_bot.py"], cwd=Path(__file__).parent)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")

def main():
    """Main startup function"""
    print("🚀 AI Webex Bot Startup")
    print("=" * 40)
    print("This script will start:")
    print("  1. LangChain API server (localhost:8000)")
    print("  2. Webex AI Bot")
    print("-" * 40)
    
    # Check if API is already running
    if check_port(8000, "LangChain API"):
        print("👍 LangChain API is already running, starting bot directly...")
        start_webex_bot()
        return
    
    # Start API server
    api_process = start_langchain_api()
    if not api_process:
        print("❌ Cannot start without the API server")
        return
    
    try:
        # Start the bot
        start_webex_bot()
    finally:
        # Clean up API server
        print("\n🧹 Cleaning up...")
        if api_process:
            api_process.terminate()
            try:
                api_process.wait(timeout=5)
                print("✅ API server stopped")
            except subprocess.TimeoutExpired:
                api_process.kill()
                print("🔪 API server force-killed")

if __name__ == "__main__":
    main()
