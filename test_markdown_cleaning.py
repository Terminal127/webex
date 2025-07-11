#!/usr/bin/env python3
"""
Test script to verify markdown cleaning functionality
"""

import re

def clean_markdown_for_webex(text):
    """Clean markdown formatting for better Webex display"""
    
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

# Test cases
test_texts = [
    "Hello **world** this is *italic* text",
    "Check out this `code snippet` and **bold text**",
    "Visit [Google](https://google.com) for more info",
    "## Header Text\nSome content with **bold** and *italic*",
    "Multiple   spaces    should be   cleaned",
    "Line breaks\n\n\n\nshould be normalized"
]

print("🧪 Testing Markdown Cleaning Function")
print("=" * 50)

for i, test_text in enumerate(test_texts, 1):
    print(f"\nTest {i}:")
    print(f"Input:  {repr(test_text)}")
    cleaned = clean_markdown_for_webex(test_text)
    print(f"Output: {repr(cleaned)}")
    print(f"Result: {cleaned}")

print("\n✅ Markdown cleaning test completed!")
