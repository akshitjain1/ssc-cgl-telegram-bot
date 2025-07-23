#!/bin/bash
# Quick deployment script for Railway

echo "🚀 Deploying SSC-CGL Bot to Railway (FREE)"
echo "=========================================="

# Check if we're in a git repo
if [ ! -d ".git" ]; then
    echo "❌ Not a git repository. Run: git init"
    exit 1
fi

# Add all files
echo "📦 Adding files..."
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "Deploy bot to Railway - $(date)"

# Push to GitHub
echo "⬆️ Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Code pushed to GitHub!"
echo ""
echo "🎯 Next Steps:"
echo "1. Go to https://railway.app"
echo "2. Sign up with GitHub (free)"
echo "3. Create new project → Deploy from GitHub"
echo "4. Select your 'ssc-cgl-telegram-bot' repository"
echo "5. Add environment variables in Railway dashboard:"
echo "   - BOT_TOKEN: 8034557764:AAGde_xnqqxEMSuqNED6SUf1rgObdTrOha0"
echo "   - GEMINI_API_KEY: AIzaSyC4eg3m_15VR3467tWN7DgId_GafvXc9us"
echo "   - ADMIN_USER_ID: 7772027400"
echo "   - NEWS_API_KEY: 5c73199076cf47e6b80b75c08a1f6910"
echo ""
echo "🎉 Your bot will be live 24/7 for FREE!"
echo "📱 Access it on mobile: @myGKL_bot"
