# 🔧 RENDER.COM ENVIRONMENT VARIABLES SETUP

## Go to Render Dashboard → Your Service → Environment Tab

Add each of these variables one by one:

### 🤖 TELEGRAM BOT SETTINGS
Variable Name: BOT_TOKEN
Value: [YOUR_ACTUAL_BOT_TOKEN_FROM_BOTFATHER]
Example: 1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ123456789

Variable Name: BOT_USERNAME  
Value: [YOUR_BOT_USERNAME_WITHOUT_@]
Example: myGKL_bot

Variable Name: ADMIN_USER_ID
Value: [YOUR_TELEGRAM_USER_ID_NUMBER]
Example: 123456789

### 🧠 AI SERVICES
Variable Name: GEMINI_API_KEY
Value: [YOUR_GOOGLE_GEMINI_API_KEY]
Example: AIzaSyABCDEFGHIJKLMNOPQRSTUVWXYZ1234567

Variable Name: NEWS_API_KEY
Value: [YOUR_NEWS_API_KEY_FROM_NEWSAPI_ORG]
Example: 1234567890abcdef1234567890abcdef
(Leave empty if you don't have one)

### 🗄️ DATABASE & CONFIG
Variable Name: DATABASE_URL
Value: sqlite:///database/user_data.db

Variable Name: TIMEZONE
Value: Asia/Kolkata

Variable Name: LOG_LEVEL
Value: INFO

Variable Name: PYTHONIOENCODING
Value: utf-8

### ⚙️ FEATURES
Variable Name: ENABLE_SCHEDULER
Value: true

Variable Name: ENABLE_CURRENT_AFFAIRS
Value: true

Variable Name: ENABLE_SPACED_REPETITION
Value: true

Variable Name: ENABLE_DAILY_VOCAB
Value: true

### 📊 CONTENT SETTINGS
Variable Name: DAILY_VOCAB_COUNT
Value: 10

Variable Name: DAILY_IDIOMS_COUNT
Value: 5

Variable Name: DAILY_GK_COUNT
Value: 10

Variable Name: CONTENT_DIFFICULTY_MIX
Value: easy:40,medium:40,hard:20

## ⚠️ IMPORTANT NOTES:
1. Do NOT include quotes around the values
2. Replace [YOUR_ACTUAL_...] with your real API keys
3. Make sure there are no extra spaces
4. Save each variable before adding the next one
