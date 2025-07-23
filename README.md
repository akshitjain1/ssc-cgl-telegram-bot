# SSC-CGL Telegram Bot

A comprehensive Telegram bot designed to help students prepare for the SSC-CGL (Staff Selection Commission - Combined Graduate Level) examination.

## Features

- **Daily Vocabulary**: Learn new words with definitions and examples
- **Idioms & Phrases**: Master common idioms used in English
- **General Knowledge**: Practice GK questions across various categories
- **Current Affairs**: Stay updated with latest news and events
- **Spaced Repetition**: Intelligent learning system that optimizes review timing
- **Daily Scheduling**: Automated daily content delivery

## Project Structure

```
ssc-cgl-telegram-bot/
│
├── main.py               # Main bot logic
├── content/              # For vocab, idioms, GK
│   ├── vocab.json
│   ├── idioms.json
│   └── gk.json
├── database/             # For SQLite user data
│   └── user_data.db
├── utils/                # Utility scripts
│   ├── fetch_current_affairs.py
│   └── spaced_repetition.py
├── scheduler/            # Daily scheduling
│   └── daily_tasks.py
├── requirements.txt      # Dependencies list
├── .env                  # Environment secrets
└── README.md
```

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ssc-cgl-telegram-bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
1. Copy `.env` file and rename it (remove the example suffix if any)
2. Fill in your actual values:
   - Get your Telegram Bot Token from [@BotFather](https://t.me/botfather)
   - Optionally, get a News API key from [NewsAPI.org](https://newsapi.org)

### 4. Database Setup
The SQLite database will be created automatically when the bot runs for the first time.

### 5. Run the Bot
```bash
python main.py
```

## 🚀 Deployment (24x7 Operation)

### Option 1: Render.com (Recommended - Free Tier Available)

1. **Prepare for deployment:**
   ```bash
   bash deploy_prep.sh
   ```

2. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Deploy to Render.com"
   git push origin main
   ```

3. **Deploy on Render.com:**
   - Go to [render.com](https://render.com)
   - Create new "Web Service" 
   - Connect your GitHub repository
   - Add environment variables from `.env.production`
   - Deploy!

4. **Required Environment Variables on Render:**
   ```
   BOT_TOKEN=your_bot_token_here
   GEMINI_API_KEY=your_gemini_api_key
   ADMIN_USER_ID=your_telegram_user_id
   ENABLE_SCHEDULER=true
   TIMEZONE=Asia/Kolkata
   ```

📖 **Complete Instructions:** See `RENDER_DEPLOYMENT.md`

### Option 2: Other Cloud Platforms
- **Heroku:** Use provided `Procfile`
- **DigitalOcean App Platform:** Use `start.sh` script
- **Railway:** Similar to Render setup
- **VPS/Server:** Run with systemd or Docker

### Deployment Files
- `Procfile` - Process definition for cloud platforms
- `start.sh` - Startup script with production settings
- `requirements.txt` - Dependencies (auto-updated)
- `.env.production` - Environment template
- `RENDER_DEPLOYMENT.md` - Detailed deployment guide

## Bot Commands

- `/start` - Start the bot and get welcome message
- `/help` - Show available commands
- `/vocab` - Get vocabulary words
- `/idioms` - Get idioms and phrases
- `/gk` - Get general knowledge questions
- `/current_affairs` - Get current affairs updates

## Features Overview

### Spaced Repetition System
The bot implements the SuperMemo 2 algorithm to optimize learning:
- Tracks user performance on each item
- Adjusts review intervals based on difficulty
- Prioritizes items that need more practice

### Daily Scheduling
Automated daily tasks include:
- **8:00 AM** - Daily vocabulary word
- **9:00 AM** - Current affairs update
- **2:00 PM** - Practice questions
- **6:00 PM** - Spaced repetition reminders
- **2:00 AM** - Database cleanup (maintenance)

### Content Management
- **Vocabulary**: Curated list with difficulty levels
- **Idioms**: Categorized by usage context
- **General Knowledge**: Organized by subjects (History, Geography, Science, etc.)
- **Current Affairs**: Fetched from news APIs with Indian focus

## Development

### Adding New Content
1. **Vocabulary**: Add entries to `content/vocab.json`
2. **Idioms**: Add entries to `content/idioms.json`
3. **GK Questions**: Add entries to `content/gk.json`

### Database Schema
The bot uses SQLite with tables for:
- User profiles and preferences
- Learning progress and statistics
- Spaced repetition data
- Session logs

### Extending Functionality
- Add new command handlers in `main.py`
- Create utility functions in the `utils/` directory
- Implement new scheduled tasks in `scheduler/daily_tasks.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team

## Disclaimer

This bot is designed for educational purposes to help with SSC-CGL preparation. Content accuracy and exam relevance should be verified from official sources.
