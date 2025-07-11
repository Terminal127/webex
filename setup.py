#!/usr/bin/env python3
"""
Setup script for Webex Bot Client
"""

import os
import subprocess
import sys

def install_requirements():
    """Install required packages"""
    try:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing packages: {e}")
        return False

def setup_environment():
    """Help user set up environment variables"""
    print("\n=== Environment Setup ===")
    
    if not os.path.exists('.env'):
        print("Creating .env file from template...")
        with open('.env.example', 'r') as template:
            content = template.read()
        with open('.env', 'w') as env_file:
            env_file.write(content)
        print("✓ Created .env file")
    
    print("\nPlease edit the .env file with your actual values:")
    print("1. Get your Webex access token from: https://developer.webex.com/docs/getting-started")
    print("2. Set the WEBEX_ACCESS_TOKEN in .env")
    print("3. Set the WEBEX_BOT_EMAIL to the email of the bot you want to chat with")
    
    print("\nAlternatively, you can set environment variables directly:")
    print("set WEBEX_ACCESS_TOKEN=your_token_here")
    print("set WEBEX_BOT_EMAIL=bot@example.com")

def main():
    print("=== Webex Bot Client Setup ===\n")
    
    # Install requirements
    if not install_requirements():
        return
    
    # Setup environment
    setup_environment()
    
    print("\n=== Setup Complete ===")
    print("You can now run the bot client with:")
    print("python webex_bot_client.py")

if __name__ == "__main__":
    main()
