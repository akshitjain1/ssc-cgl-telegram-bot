#!/usr/bin/env python3
"""
Health check script for SSC-CGL Telegram Bot
Can be used for monitoring and ensuring the bot is responsive
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError

# Load environment variables
load_dotenv()

async def health_check():
    """Check if the bot is healthy and responsive"""
    bot_token = os.getenv('BOT_TOKEN')
    
    if not bot_token:
        print("❌ HEALTH CHECK FAILED: BOT_TOKEN not found")
        return False
    
    try:
        bot = Bot(token=bot_token)
        
        # Test bot connection
        async with bot:
            bot_info = await bot.get_me()
            
        print(f"✅ HEALTH CHECK PASSED")
        print(f"🤖 Bot: @{bot_info.username} ({bot_info.first_name})")
        print(f"🆔 Bot ID: {bot_info.id}")
        print(f"⏰ Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔗 Bot Link: https://t.me/{bot_info.username}")
        
        return True
        
    except TelegramError as e:
        print(f"❌ HEALTH CHECK FAILED: Telegram API Error - {e}")
        return False
        
    except Exception as e:
        print(f"❌ HEALTH CHECK FAILED: Unexpected Error - {e}")
        return False

async def main():
    """Main health check function"""
    print("🏥 SSC-CGL Bot Health Check")
    print("=" * 40)
    
    success = await health_check()
    
    print("=" * 40)
    if success:
        print("🎉 Bot is healthy and operational!")
        sys.exit(0)
    else:
        print("🚨 Bot health check failed!")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Health check cancelled")
        sys.exit(1)
