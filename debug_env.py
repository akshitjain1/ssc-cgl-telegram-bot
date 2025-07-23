#!/usr/bin/env python3
"""
Debug script to check environment loading
"""

import os
from dotenv import load_dotenv

print("🔍 Debug: Environment Variable Loading")
print("=" * 50)

# Test 1: Check if .env.local exists
if os.path.exists('.env.local'):
    print("✓ .env.local file exists")
else:
    print("❌ .env.local file NOT found")

# Test 2: Load .env.local explicitly
print("\n📂 Loading .env.local...")
load_dotenv('.env.local')

# Test 3: Check what we get
bot_token = os.getenv('BOT_TOKEN')
gemini_key = os.getenv('GEMINI_API_KEY')
admin_id = os.getenv('ADMIN_USER_ID')

print(f"BOT_TOKEN: {bot_token[:20] + '...' if bot_token else 'None'}")
print(f"GEMINI_API_KEY: {gemini_key[:20] + '...' if gemini_key else 'None'}")
print(f"ADMIN_USER_ID: {admin_id}")

# Test 4: Check if there's an issue with the main.py loading logic
print("\n🔧 Testing main.py loading logic...")
if os.path.exists('.env.local'):
    print("🔧 Loading local environment variables for testing...")
    load_dotenv('.env.local')
else:
    print("🌐 Loading production environment variables...")
    load_dotenv()

bot_token_after = os.getenv('BOT_TOKEN')
print(f"BOT_TOKEN after main.py logic: {bot_token_after[:20] + '...' if bot_token_after else 'None'}")

# Test 5: Check current working directory
print(f"\n📍 Current working directory: {os.getcwd()}")
print(f"📂 Files in current directory:")
for file in os.listdir('.'):
    if file.startswith('.env'):
        print(f"   - {file}")
