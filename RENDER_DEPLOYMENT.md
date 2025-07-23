# 🚀 SSC-CGL Bot - Render.com Deployment Guide

## 📋 Pre-Deployment Checklist

### ✅ Files Required for Render.com
- [x] `Procfile` - Tells Render how to start your bot
- [x] `start.sh` - Startup script with proper configurations
- [x] `requirements.txt` - Python dependencies
- [x] `main.py` - Your bot code
- [x] All supporting files (utils/, database/, scheduler/, etc.)

## 🌐 Render.com Deployment Steps

### 1. **Prepare Your Repository**
```bash
# Make sure all files are committed to Git
git add .
git commit -m "Prepare for Render.com deployment"
git push origin main
```

### 2. **Create Render Account & Service**
1. Go to [render.com](https://render.com) and create an account
2. Click "New +" → "Web Service" (for persistent services) or "Background Worker"
3. Connect your GitHub repository
4. Choose your repository: `ssc-cgl-telegram-bot`

### 3. **Service Configuration**
- **Name:** `ssc-cgl-bot` (or your preferred name)
- **Environment:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `bash start.sh` (this is in your Procfile)
- **Plan:** Free tier is sufficient for testing

## 🔧 Environment Variables Required

### **Essential Environment Variables** (Add these in Render Dashboard):

```bash
# Telegram Bot Configuration
BOT_TOKEN=8034557764:AAGde_xnqqxEMSuqNED6SUf1rgObdTrOha0
BOT_USERNAME=myGKL_bot

# AI Service
GEMINI_API_KEY=AIzaSyC4eg3m_15VR3467tWN7DgId_GafvXc9us

# Admin Configuration
ADMIN_USER_ID=7772027400  # Replace with your Telegram user ID

# News API (Optional)
NEWS_API_KEY=5c73199076cf47e6b80b75c08a1f6910

# Database
DATABASE_URL=sqlite:///database/user_data.db

# Scheduling
ENABLE_SCHEDULER=true
TIMEZONE=Asia/Kolkata

# Feature Flags
ENABLE_CURRENT_AFFAIRS=true
ENABLE_SPACED_REPETITION=true
ENABLE_DAILY_VOCAB=true

# Content Settings
DAILY_VOCAB_COUNT=10
DAILY_IDIOMS_COUNT=5
DAILY_GK_COUNT=10
CONTENT_DIFFICULTY_MIX=easy:40,medium:40,hard:20

# Logging
LOG_LEVEL=INFO
LOG_FILE=bot.log

# Python Configuration
PYTHONIOENCODING=utf-8
```

### **How to Add Environment Variables:**
1. In Render Dashboard → Your Service → Environment
2. Click "Add Environment Variable"
3. Add each variable from the list above
4. **Important:** Don't include quotes around values

## 📁 File Structure Check
```
ssc-cgl-telegram-bot/
├── Procfile                 ← NEW: Tells Render how to start
├── start.sh                 ← NEW: Startup script
├── requirements.txt         ← UPDATED: Complete dependencies
├── main.py                  ← Your bot code
├── .env                     ← Keep for local development
├── database/
├── utils/
├── scheduler/
├── content/
└── tests/
```

## 🎯 Deployment Process

### **Step 1: Deploy**
1. Push your code to GitHub
2. In Render, click "Deploy Latest Commit"
3. Watch the build logs for any errors

### **Step 2: Monitor**
- Check "Logs" tab for startup messages
- Look for: `🎉 SSC-CGL Bot is fully operational!`
- Verify no error messages

### **Step 3: Test**
1. Open Telegram → Search `@myGKL_bot`
2. Send `/start` command
3. Try `/help` to see all commands
4. Test `/vocab`, `/quiz`, etc.

## 🔍 Troubleshooting

### **Common Issues & Solutions:**

#### **Build Fails:**
```bash
# If spaCy model fails to download:
# Add this to requirements.txt before the spaCy model line:
spacy>=3.8.0

# If memory issues during build:
# Use smaller model or upgrade Render plan
```

#### **Bot Doesn't Respond:**
- Check BOT_TOKEN is correct
- Verify all environment variables are set
- Check logs for connection errors

#### **Scheduler Issues:**
- Ensure TIMEZONE is set correctly
- Check ENABLE_SCHEDULER=true
- Verify admin commands work with correct ADMIN_USER_ID

#### **Database Issues:**
- Render's file system is ephemeral
- For persistent data, consider upgrading to PostgreSQL
- Current SQLite setup will reset on each deployment

## 📈 Production Recommendations

### **For Heavy Usage:**
1. **Upgrade to Paid Plan** for better performance
2. **Use PostgreSQL** instead of SQLite for persistence
3. **Enable Auto-Deploy** from GitHub for continuous deployment
4. **Add Health Checks** for monitoring

### **Database Upgrade to PostgreSQL:**
```python
# Update DATABASE_URL to:
DATABASE_URL=postgresql://username:password@host:port/dbname

# Render provides PostgreSQL addon
```

### **Monitoring Setup:**
- Enable "Auto-Deploy" from main branch
- Set up health check endpoint
- Configure alert notifications

## 🎉 Success Checklist

After successful deployment, your bot should:
- [x] Respond to `/start` command
- [x] Show all commands with `/help`
- [x] Generate vocabulary with `/vocab`
- [x] Provide grammar feedback
- [x] Run interactive quizzes
- [x] Send scheduled daily content
- [x] Track user progress

## 📞 Support

If you encounter issues:
1. Check Render logs for error messages
2. Verify all environment variables are set
3. Test bot token with the test script: `python test_bot_token.py`
4. Ensure your GitHub repository is up to date

## 🔄 Continuous Deployment

To update your bot:
1. Make changes to your code
2. Commit and push to GitHub
3. Render will automatically deploy (if auto-deploy is enabled)
4. Or manually click "Deploy Latest Commit"

**Your SSC-CGL bot will now run 24x7 on Render.com!** 🚀

---
*Last updated: July 23, 2025*
