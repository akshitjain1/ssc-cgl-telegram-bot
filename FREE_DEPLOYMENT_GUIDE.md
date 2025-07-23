# 🆓 FREE 24/7 Deployment Guide for SSC-CGL Bot

## 🚀 Railway.app Deployment (RECOMMENDED - 100% FREE)

Railway offers 500 hours per month FREE (enough for 24/7 operation).

### Step 1: Prepare for Railway

1. **Create Railway Account**:
   - Go to [Railway.app](https://railway.app)
   - Sign up with GitHub (free)

2. **Push to GitHub** (if not done):
   ```bash
   git add .
   git commit -m "Ready for Railway deployment"
   git push origin main
   ```

### Step 2: Create Railway Configuration

Create `railway.toml`:
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python main.py"

[env]
PORT = "8080"
```

### Step 3: Deploy

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `ssc-cgl-telegram-bot` repository
4. Railway will auto-detect Python and deploy!

### Step 4: Add Environment Variables

In Railway dashboard:
1. Go to your project → Variables
2. Add these variables:
   - `BOT_TOKEN`: 8034557764:AAGde_xnqqxEMSuqNED6SUf1rgObdTrOha0
   - `GEMINI_API_KEY`: AIzaSyC4eg3m_15VR3467tWN7DgId_GafvXc9us
   - `ADMIN_USER_ID`: 7772027400
   - `NEWS_API_KEY`: 5c73199076cf47e6b80b75c08a1f6910
   - `ENVIRONMENT`: production

### Step 5: Done! 🎉
Your bot will be live 24/7 for FREE!

---

## 🪂 Alternative: Fly.io Deployment

### Step 1: Install Fly CLI
```bash
# Windows (using PowerShell)
iwr https://fly.io/install.ps1 -useb | iex
```

### Step 2: Login & Initialize
```bash
fly auth login
fly launch --no-deploy
```

### Step 3: Configure fly.toml
```toml
app = "ssc-cgl-bot"
primary_region = "iad"

[build]

[env]
  PORT = "8080"

[[services]]
  internal_port = 8080
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
```

### Step 4: Set Environment Variables
```bash
fly secrets set BOT_TOKEN=8034557764:AAGde_xnqqxEMSuqNED6SUf1rgObdTrOha0
fly secrets set GEMINI_API_KEY=AIzaSyC4eg3m_15VR3467tWN7DgId_GafvXc9us
fly secrets set ADMIN_USER_ID=7772027400
fly secrets set NEWS_API_KEY=5c73199076cf47e6b80b75c08a1f6910
```

### Step 5: Deploy
```bash
fly deploy
```

---

## 🐍 Alternative: PythonAnywhere

### Step 1: Create Account
- Go to [PythonAnywhere.com](https://www.pythonanywhere.com)
- Sign up for FREE account

### Step 2: Upload Code
1. Use the "Files" tab to upload your bot files
2. Or clone from GitHub:
   ```bash
   git clone https://github.com/akshitjain1/ssc-cgl-telegram-bot.git
   ```

### Step 3: Install Dependencies
In PythonAnywhere console:
```bash
cd ssc-cgl-telegram-bot
pip3.10 install --user -r requirements.txt
```

### Step 4: Create .env file
```bash
nano .env
```
Add your environment variables

### Step 5: Create Always-On Task
- Go to "Tasks" tab
- Create new task: `python3.10 /home/yourusername/ssc-cgl-telegram-bot/main.py`
- Set to run "Always"

---

## 📱 Mobile Access

Once deployed to ANY of these platforms, you can access your bot:

### On Your Mobile:
1. **Open Telegram app**
2. **Search for your bot**: `@myGKL_bot`
3. **Start chatting** - it works 24/7!

### Bot Commands on Mobile:
- `/start` - Welcome message
- `/help` - List all commands  
- `/quiz easy` - Start practice quiz
- `/syllabus` - Get study materials
- `/notes quantitative` - Get math notes
- `/study_plan` - Personalized study plan
- Send any text for grammar check

### Admin Commands (Only You):
- `/admin_stats` - Bot usage statistics
- `/admin_broadcast message` - Send to all users

---

## 💡 **My Recommendation: Railway.app**

**Why Railway?**
- ✅ **500 hours FREE** monthly (24/7 coverage)
- ✅ **No credit card** required
- ✅ **GitHub integration** (auto-deploy)
- ✅ **Easy setup** (5 minutes)
- ✅ **No container knowledge** needed

**Setup Time**: ~5 minutes
**Monthly Cost**: $0.00
**Uptime**: 24/7

Would you like me to help you set up Railway deployment step by step?
