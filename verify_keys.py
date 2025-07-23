#!/usr/bin/env python3
"""
Quick API Key Verification Script
This script checks if your API keys are properly formatted and working
"""

import os
import re
from dotenv import load_dotenv

def verify_api_keys():
    """Verify API key formats and basic functionality"""
    print("🔍 Verifying API Keys...")
    print("=" * 40)
    
    # Load environment variables
    if os.path.exists('.env.local'):
        load_dotenv('.env.local')
        print("✓ Loaded .env.local file")
    else:
        load_dotenv()
        print("✓ Loaded .env file")
    
    # Get values
    bot_token = os.getenv('BOT_TOKEN', '')
    gemini_key = os.getenv('GEMINI_API_KEY', '')
    admin_id = os.getenv('ADMIN_USER_ID', '')
    
    print("\n📋 API Key Status:")
    print("-" * 40)
    
    # Check BOT_TOKEN format
    bot_token_pattern = r'^\d+:[A-Za-z0-9_-]+$'
    if bot_token and bot_token != 'PASTE_YOUR_ACTUAL_BOT_TOKEN_HERE':
        if re.match(bot_token_pattern, bot_token):
            print("✅ BOT_TOKEN: Format is correct")
            print(f"   Preview: {bot_token[:10]}...{bot_token[-10:]}")
        else:
            print("❌ BOT_TOKEN: Invalid format")
            print("   Expected: 1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    else:
        print("⚠️  BOT_TOKEN: Not set (still using placeholder)")
    
    # Check GEMINI_API_KEY format
    gemini_key_pattern = r'^AIza[A-Za-z0-9_-]+$'
    if gemini_key and gemini_key != 'PASTE_YOUR_ACTUAL_GEMINI_API_KEY_HERE':
        if re.match(gemini_key_pattern, gemini_key):
            print("✅ GEMINI_API_KEY: Format is correct")
            print(f"   Preview: {gemini_key[:10]}...{gemini_key[-10:]}")
        else:
            print("❌ GEMINI_API_KEY: Invalid format")
            print("   Expected: AIzaSyABCDEFGHIJKLMNOPQRSTUVWXYZ1234567")
    else:
        print("⚠️  GEMINI_API_KEY: Not set (still using placeholder)")
    
    # Check ADMIN_USER_ID format
    if admin_id and admin_id != 'PASTE_YOUR_TELEGRAM_USER_ID_HERE':
        if admin_id.isdigit() and len(admin_id) >= 5:
            print("✅ ADMIN_USER_ID: Format is correct")
            print(f"   Value: {admin_id}")
        else:
            print("❌ ADMIN_USER_ID: Invalid format")
            print("   Expected: Numeric value (e.g., 123456789)")
    else:
        print("⚠️  ADMIN_USER_ID: Not set (still using placeholder)")
    
    print("\n" + "=" * 40)
    
    # Summary
    all_set = (
        bot_token and bot_token != 'PASTE_YOUR_ACTUAL_BOT_TOKEN_HERE' and
        gemini_key and gemini_key != 'PASTE_YOUR_ACTUAL_GEMINI_API_KEY_HERE' and
        admin_id and admin_id != 'PASTE_YOUR_TELEGRAM_USER_ID_HERE'
    )
    
    if all_set:
        print("🎉 All API keys are configured!")
        print("✅ You can now run: python main.py")
    else:
        print("📝 Next steps:")
        if not bot_token or bot_token == 'PASTE_YOUR_ACTUAL_BOT_TOKEN_HERE':
            print("1. Get bot token from @BotFather on Telegram")
        if not gemini_key or gemini_key == 'PASTE_YOUR_ACTUAL_GEMINI_API_KEY_HERE':
            print("2. Get Gemini API key from Google AI Studio")
        if not admin_id or admin_id == 'PASTE_YOUR_TELEGRAM_USER_ID_HERE':
            print("3. Get your user ID from @userinfobot on Telegram")
        print("4. Update the .env.local file with these values")
        print("5. Run this script again to verify")
    
    return all_set

if __name__ == "__main__":
    verify_api_keys()
