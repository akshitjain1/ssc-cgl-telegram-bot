#!/bin/bash
# Start script for SSC-CGL Telegram Bot on Render.com

echo "🚀 Starting SSC-CGL Telegram Bot..."
echo "📅 Start time: $(date)"

# Set Python to use UTF-8 encoding (helps with emojis)
export PYTHONIOENCODING=utf-8

# Create directories if they don't exist
mkdir -p database
mkdir -p content

# Start the bot
echo "🤖 Launching bot process..."
python main.py
