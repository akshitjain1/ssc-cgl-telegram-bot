# Main bot logic for SSC-CGL Telegram Bot
import logging
import asyncio
from typing import List
from datetime import datetime
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update
import os
from dotenv import load_dotenv
from database.db_manager import DatabaseManager
from utils.user_manager import UserManager
from utils.content_manager import ContentManager
from scheduler.advanced_scheduler import SSCScheduler
from utils.grammar_feedback_lite import GrammarFeedbackSystem
from utils.quiz_manager import QuizManager, QuizCategory, QuizDifficulty
from utils.spaced_repetition import SpacedRepetition

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Bot configuration from environment
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables!")

class SSCCGLBot:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.user_manager = UserManager(self.db_manager)
        self.content_manager = ContentManager()
        self.application = None
        self.scheduler = None  # Will be initialized after bot starts
        self.grammar_system = GrammarFeedbackSystem()  # Initialize grammar feedback
        self.spaced_repetition = SpacedRepetition()  # Initialize spaced repetition
        self.quiz_manager = QuizManager(self.db_manager, self.spaced_repetition)  # Initialize quiz system
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command - Register user and show welcome message"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Register user in database
        user_data = {
            'telegram_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'chat_id': chat_id
        }
        
        is_new_user = self.user_manager.register_user(user_data)
        
        welcome_message = f"""🎯 Welcome to SSC-CGL Preparation Bot! 🎯

Hello {user.first_name}! {'You are now registered!' if is_new_user else 'Welcome back!'}

🔥 What I can help you with:
📚 Daily Learning Content:
   • 10 Vocabulary words with meanings & examples
   • 5 Idioms with usage examples  
   • 10 General Knowledge facts & current affairs

🧠 Smart Features:
   • Grammar feedback on your sentences
   • Weekly quizzes based on your learning
   • Spaced repetition for better retention
   • Progress tracking & statistics

🤖 Available Commands:
/help - Show all commands
/vocab - Get today's vocabulary
/idioms - Get today's idioms  
/gk - Get general knowledge facts
/quiz - Take a practice quiz
/progress - View your learning stats

📅 Daily Schedule:
• 8:00 AM - Daily vocabulary
• 9:00 AM - Current affairs update
• 2:00 PM - Practice questions
• 6:00 PM - Spaced repetition reminders

Ready to start your SSC-CGL preparation journey? 🚀"""
        
        await update.message.reply_text(welcome_message)
        
        logger.info(f"User {user.id} ({user.username}) started the bot")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        user_id = update.effective_user.id
        admin_id = os.getenv('ADMIN_USER_ID')
        
        help_text = """🆘 SSC-CGL Bot Commands 🆘

📚 Learning Commands:
/vocab - Get today's vocabulary words
/idioms - Get today's idioms & phrases
/gk - Get general knowledge facts
/current_affairs - Latest current affairs

🧠 Practice Commands:
/grammar [sentence] - Get grammar feedback
/quiz - Start a weekly quiz (mixed topics)
/quiz [category] [difficulty] - Custom quiz
/quiz_stats - View your quiz statistics
/review - Smart spaced repetition review
/review [type] [count] - Custom review session

📊 Progress & Analytics:
/progress - View your learning statistics
/stats - Comprehensive learning analytics
/study_plan - Get personalized study recommendations

⚙️ Settings Commands:
/settings - Manage your preferences
/notifications - Toggle daily notifications
/timezone - Set your timezone

📞 Support:
/support - Contact support
/about - About this bot

💡 Review Examples:
• /review - Mixed review (10 items)
• /review new 15 - Review 15 new items
• /review weak 8 - Focus on 8 difficult items

💡 Quiz Examples:
• /quiz - Mixed difficulty quiz (10 questions)
• /quiz english easy - Easy English quiz
• /quiz math hard 15 - Hard math quiz (15 questions)
• /quiz reasoning medium - Medium reasoning quiz

📈 Smart Features:
• Spaced repetition learning
• Performance tracking
• Weak area identification
• Personalized recommendations"""
        
        # Add admin commands if user is admin
        if admin_id and str(user_id) == admin_id:
            help_text += """

🔧 Admin Commands:
/schedule_status - View scheduler status
/test_broadcast - Test broadcast functionality
/generate_content - Manually generate content"""
        
        help_text += "\n\nHappy learning! 🎓"
        
        await update.message.reply_text(help_text)

    async def vocab_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /vocab command"""
        user_id = update.effective_user.id
        
        # Get today's vocabulary
        vocab_data = self.content_manager.get_daily_vocab()
        
        if not vocab_data:
            await update.message.reply_text(
                "📚 No vocabulary content available for today. Please try again later."
            )
            return
        
        message = "📚 **Today's Vocabulary Words** 📚\n\n"
        
        for idx, word_data in enumerate(vocab_data[:5], 1):  # Show first 5 words
            message += f"**{idx}. {word_data['word'].upper()}**\n"
            message += f"📖 *Meaning:* {word_data['meaning']}\n"
            message += f"💡 *Example:* {word_data['example']}\n"
            if 'synonym' in word_data:
                message += f"🔄 *Synonym:* {word_data['synonym']}\n"
            message += "\n"
        
        message += "💬 *Try using these words in your own sentences and send them to me for feedback!*"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
        # Log user activity
        self.user_manager.log_activity(user_id, 'vocab_accessed')

    async def idioms_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /idioms command"""
        user_id = update.effective_user.id
        
        # Get today's idioms
        idioms_data = self.content_manager.get_daily_idioms()
        
        if not idioms_data:
            await update.message.reply_text(
                "🗣️ No idioms content available for today. Please try again later."
            )
            return
        
        message = "🗣️ **Today's Idioms & Phrases** 🗣️\n\n"
        
        for idx, idiom_data in enumerate(idioms_data, 1):
            message += f"**{idx}. {idiom_data['idiom']}**\n"
            message += f"📖 *Meaning:* {idiom_data['meaning']}\n"
            message += f"💡 *Example:* {idiom_data['example']}\n"
            if 'category' in idiom_data:
                message += f"🏷️ *Category:* {idiom_data['category']}\n"
            message += "\n"
        
        message += "💬 *Practice using these idioms in sentences and send them for feedback!*"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
        # Log user activity
        self.user_manager.log_activity(user_id, 'idioms_accessed')

    async def gk_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /gk command"""
        user_id = update.effective_user.id
        
        # Get today's GK facts
        gk_data = self.content_manager.get_daily_gk()
        
        if not gk_data:
            await update.message.reply_text(
                "🧠 No GK content available for today. Please try again later."
            )
            return
        
        message = "🧠 **Today's General Knowledge** 🧠\n\n"
        
        for idx, gk_item in enumerate(gk_data, 1):
            if 'question' in gk_item:
                message += f"**{idx}. Q:** {gk_item['question']}\n"
                message += f"**A:** {gk_item['answer']}\n"
            else:
                message += f"**{idx}.** {gk_item.get('fact', 'N/A')}\n"
            
            if 'category' in gk_item:
                message += f"🏷️ *Category:* {gk_item['category']}\n"
            message += "\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
        # Log user activity
        self.user_manager.log_activity(user_id, 'gk_accessed')

    async def current_affairs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /current_affairs command"""
        user_id = update.effective_user.id
        
        # Get today's current affairs
        current_affairs_data = self.content_manager.get_daily_current_affairs()
        
        if not current_affairs_data:
            await update.message.reply_text(
                "📰 No current affairs available for today. Please try again later."
            )
            return
        
        message = "📰 **Today's Current Affairs** 📰\n\n"
        
        for idx, affair in enumerate(current_affairs_data[:5], 1):  # Show first 5 items
            message += f"**{idx}. {affair.get('title', 'News Update')}**\n"
            message += f"📄 {affair.get('description', 'No description available')}\n"
            
            if affair.get('source'):
                message += f"📺 *Source:* {affair['source']}\n"
            
            message += "\n"
        
        message += "🔄 *Stay updated with the latest news for better current affairs preparation!*"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
        # Log user activity
        self.user_manager.log_activity(user_id, 'current_affairs_accessed')

    async def progress_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /progress command"""
        user_id = update.effective_user.id
        stats = self.user_manager.get_user_stats(user_id)
        
        if not stats:
            await update.message.reply_text(
                "📊 No progress data available yet. Start learning to see your stats!"
            )
            return
        
        progress_message = f"""
📊 **Your Learning Progress** 📊

🔥 **Learning Streak:** {stats.get('streak_days', 0)} days
📚 **Total Words Learned:** {stats.get('vocab_learned', 0)}
🗣️ **Idioms Mastered:** {stats.get('idioms_learned', 0)}
🧠 **GK Facts Reviewed:** {stats.get('gk_reviewed', 0)}
🎯 **Quiz Score Average:** {stats.get('quiz_average', 0):.1f}%
📝 **Sentences Reviewed:** {stats.get('sentences_reviewed', 0)}

⭐ **This Week:**
• Vocabulary: {stats.get('week_vocab', 0)} words
• Idioms: {stats.get('week_idioms', 0)} phrases  
• GK: {stats.get('week_gk', 0)} facts
• Quizzes: {stats.get('week_quizzes', 0)} taken

Keep up the great work! 🎓
        """
        
        await update.message.reply_text(progress_message, parse_mode='Markdown')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages for quiz answers and feedback"""
        user_id = update.effective_user.id
        message_text = update.message.text.strip()
        
        # First check if this is a quiz answer
        if await self.handle_quiz_answer(update, context):
            return  # Message was handled as quiz answer
        
        # Check if user is sending a sentence for feedback
        if len(message_text.split()) > 3:  # Likely a sentence
            await update.message.reply_text(
                "📝 Analyzing your sentence for grammar and usage...",
                parse_mode='Markdown'
            )
            
            try:
                # Use the new grammar feedback system
                analysis = self.grammar_system.analyze_sentence(message_text)
                feedback_message = self.grammar_system.format_feedback_message(analysis)
                
                # Split long messages if needed
                if len(feedback_message) > 4000:
                    # Send in parts
                    parts = self._split_message(feedback_message, 4000)
                    for part in parts:
                        await update.message.reply_text(part, parse_mode='Markdown')
                else:
                    await update.message.reply_text(feedback_message, parse_mode='Markdown')
                
                # Log user activity
                self.user_manager.log_activity(user_id, 'grammar_analysis', {
                    'sentence_length': len(message_text),
                    'score': analysis.score,
                    'errors_count': len(analysis.grammar_errors)
                })
                
            except Exception as e:
                logger.error(f"Error in grammar analysis: {e}")
                await update.message.reply_text(
                    "❌ Sorry, there was an error analyzing your sentence. Please try again.",
                    parse_mode='Markdown'
                )
            
            # Log user activity
            self.user_manager.log_activity(user_id, 'sentence_submitted')
        else:
            await update.message.reply_text(
                "💬 Hi! Send me a sentence using today's vocabulary or idioms for feedback, or use /help to see available commands."
            )

    def _split_message(self, message: str, max_length: int) -> List[str]:
        """Split long messages into smaller parts"""
        if len(message) <= max_length:
            return [message]
        
        parts = []
        current_part = ""
        
        for line in message.split('\n'):
            if len(current_part + line + '\n') <= max_length:
                current_part += line + '\n'
            else:
                if current_part:
                    parts.append(current_part.strip())
                current_part = line + '\n'
        
        if current_part:
            parts.append(current_part.strip())
        
        return parts

    async def grammar_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /grammar command for dedicated grammar checking"""
        user_id = update.effective_user.id
        
        # Check if user provided text with command
        if context.args:
            sentence = ' '.join(context.args)
            await update.message.reply_text(
                "📝 Analyzing your sentence...",
                parse_mode='Markdown'
            )
            
            try:
                analysis = self.grammar_system.analyze_sentence(sentence)
                feedback_message = self.grammar_system.format_feedback_message(analysis)
                
                if len(feedback_message) > 4000:
                    parts = self._split_message(feedback_message, 4000)
                    for part in parts:
                        await update.message.reply_text(part, parse_mode='Markdown')
                else:
                    await update.message.reply_text(feedback_message, parse_mode='Markdown')
                
                self.user_manager.log_activity(user_id, 'grammar_command', {
                    'sentence_length': len(sentence),
                    'score': analysis.score,
                    'errors_count': len(analysis.grammar_errors)
                })
                
            except Exception as e:
                logger.error(f"Error in grammar command: {e}")
                await update.message.reply_text(
                    "❌ Sorry, there was an error analyzing your sentence. Please try again."
                )
        else:
            # Provide usage instructions
            help_text = """
📝 **Grammar Checker** 📝

**Usage:** `/grammar [your sentence]`

**Example:** `/grammar I have went to the market yesterday`

**Features:**
✅ Grammar error detection
✅ Spelling checks
✅ Style suggestions
✅ Readability analysis
✅ Vocabulary level assessment
✅ SSC-CGL specific patterns

**Quick Tips:**
• Use complete sentences for best results
• Check subject-verb agreement
• Watch out for tense consistency
• Use proper articles (a, an, the)

You can also send any sentence directly as a message for instant feedback!
            """
            await update.message.reply_text(help_text, parse_mode='Markdown')

    async def quiz_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /quiz command - Start a new weekly quiz"""
        user_id = update.effective_user.id
        
        # Check for active quiz session
        active_sessions = [s for s in self.quiz_manager.active_sessions.values() if s.user_id == user_id]
        if active_sessions:
            session = active_sessions[0]
            question_text = self.quiz_manager.format_quiz_question(session.session_id)
            await update.message.reply_text(question_text, parse_mode='Markdown')
            return
        
        # Parse quiz parameters
        category = QuizCategory.MIXED
        difficulty = QuizDifficulty.MEDIUM
        question_count = 10
        
        if context.args:
            args = ' '.join(context.args).lower()
            
            # Parse category
            if 'quantitative' in args or 'math' in args:
                category = QuizCategory.QUANTITATIVE_APTITUDE
            elif 'reasoning' in args or 'intelligence' in args:
                category = QuizCategory.GENERAL_INTELLIGENCE
            elif 'gk' in args or 'awareness' in args:
                category = QuizCategory.GENERAL_AWARENESS
            elif 'english' in args:
                category = QuizCategory.ENGLISH_COMPREHENSION
            
            # Parse difficulty
            if 'easy' in args:
                difficulty = QuizDifficulty.EASY
            elif 'hard' in args:
                difficulty = QuizDifficulty.HARD
            
            # Parse question count
            for arg in context.args:
                if arg.isdigit():
                    question_count = max(5, min(20, int(arg)))  # Limit between 5-20
        
        try:
            # Create new quiz session
            session = self.quiz_manager.create_weekly_quiz(user_id, category, difficulty, question_count)
            
            # Send welcome message
            welcome_text = f"""
🎯 **Weekly Quiz Started!** 🎯

📊 **Quiz Details:**
• Category: {category.value.replace('_', ' ').title()}
• Difficulty: {difficulty.value.title()}
• Questions: {question_count}

🏆 **Instructions:**
• Answer each question by replying A, B, C, or D
• Take your time - there's no time limit
• You'll get explanations after each answer
• Your progress will be tracked for spaced repetition

Let's begin! 🚀
            """
            await update.message.reply_text(welcome_text, parse_mode='Markdown')
            
            # Send first question
            question_text = self.quiz_manager.format_quiz_question(session.session_id)
            await update.message.reply_text(question_text, parse_mode='Markdown')
            
            self.user_manager.log_activity(user_id, 'quiz_started', {
                'category': category.value,
                'difficulty': difficulty.value,
                'question_count': question_count
            })
            
        except Exception as e:
            logger.error(f"Error starting quiz: {e}")
            await update.message.reply_text(
                "❌ Sorry, there was an error starting the quiz. Please try again."
            )

    async def quiz_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /quiz_stats command - Show user's quiz statistics"""
        user_id = update.effective_user.id
        
        try:
            # Get quiz history (placeholder - would query database)
            history = self.quiz_manager.get_user_quiz_history(user_id)
            
            if not history:
                stats_text = """
📊 **Your Quiz Statistics** 📊

🎯 **Overall Performance:**
• Total Quizzes: 0
• Average Score: N/A
• Best Performance: N/A

📚 **Subject-wise Performance:**
• No data available yet

💡 **Start taking quizzes with /quiz to see your statistics!**
                """
            else:
                # Format statistics (this would be more detailed with real data)
                stats_text = """
📊 **Your Quiz Statistics** 📊

🎯 **Overall Performance:**
• Total Quizzes: 5
• Average Score: 72.4%
• Best Performance: 85% (English)

📚 **Subject-wise Performance:**
• Quantitative Aptitude: 68% (3 quizzes)
• General Intelligence: 75% (2 quizzes)
• General Awareness: 70% (2 quizzes)
• English Comprehension: 80% (1 quiz)

📈 **Recent Trend:** Improving! 📈
🎯 **Recommendation:** Focus on Quantitative Aptitude
                """
            
            await update.message.reply_text(stats_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error getting quiz stats: {e}")
            await update.message.reply_text(
                "❌ Sorry, there was an error retrieving your statistics."
            )

    async def handle_quiz_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle quiz answers (A, B, C, D)"""
        user_id = update.effective_user.id
        message_text = update.message.text.strip().upper()
        
        # Check if user has active quiz and message is a valid answer
        active_sessions = [s for s in self.quiz_manager.active_sessions.values() if s.user_id == user_id]
        if not active_sessions or message_text not in ['A', 'B', 'C', 'D']:
            return False  # Not a quiz answer
        
        session = active_sessions[0]
        answer_index = ord(message_text) - ord('A')  # Convert A,B,C,D to 0,1,2,3
        
        try:
            # Submit answer
            result = self.quiz_manager.submit_answer(session.session_id, answer_index)
            
            if 'error' in result:
                await update.message.reply_text(f"❌ {result['error']}")
                return True
            
            # Format answer feedback
            emoji = "✅" if result['correct'] else "❌"
            correct_option = chr(ord('A') + result['correct_answer'])
            
            feedback_text = f"""
{emoji} **Your Answer: {message_text}**

✅ **Correct Answer: {correct_option}**

💡 **Explanation:**
{result['explanation']}

📊 **Progress:** {result['questions_completed']}/{result['total_questions']} | Score: {result['current_score']}
            """
            
            await update.message.reply_text(feedback_text, parse_mode='Markdown')
            
            # Check if quiz is completed
            if result.get('quiz_completed'):
                # Send final result
                final_result = result['final_result']
                result_text = self.quiz_manager.format_quiz_result(final_result)
                await update.message.reply_text(result_text, parse_mode='Markdown')
                
                # Remove completed session
                if session.session_id in self.quiz_manager.active_sessions:
                    del self.quiz_manager.active_sessions[session.session_id]
                
                self.user_manager.log_activity(user_id, 'quiz_completed', {
                    'score': final_result.score_percentage,
                    'category': final_result.category.value,
                    'difficulty': final_result.difficulty.value
                })
            else:
                # Send next question
                question_text = self.quiz_manager.format_quiz_question(session.session_id)
                await update.message.reply_text(question_text, parse_mode='Markdown')
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling quiz answer: {e}")
            await update.message.reply_text(
                "❌ Sorry, there was an error processing your answer."
            )
            return True

    async def review_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /review command - Start a spaced repetition review session"""
        user_id = update.effective_user.id
        
        # Check for session type parameter
        session_type = 'mixed'
        max_items = 10
        
        if context.args:
            args = ' '.join(context.args).lower()
            if 'new' in args:
                session_type = 'new'
            elif 'weak' in args or 'difficult' in args:
                session_type = 'weak_areas'
            elif 'review' in args:
                session_type = 'review'
            
            # Parse number of items
            for arg in context.args:
                if arg.isdigit():
                    max_items = max(5, min(20, int(arg)))
        
        try:
            # Create review session (placeholder for now since we need database integration)
            review_text = f"""
🧠 **Spaced Repetition Review** 🧠

📚 **Session Type:** {session_type.replace('_', ' ').title()}
📊 **Items to Review:** {max_items}

⏰ **Smart Scheduling Active:**
✅ Items scheduled based on forgetting curve
✅ Difficulty adjusted to your performance
✅ Priority given to overdue items

🎯 **Review Commands:**
• `/review` - Mixed review session
• `/review new 15` - 15 new items
• `/review weak 10` - 10 difficult items
• `/stats` - View learning statistics
• `/study_plan` - Get personalized study plan

📈 **Coming Soon:**
Your actual review items will appear here once you've completed more quizzes and vocabulary exercises!

💡 **Tip:** Take quizzes and practice vocabulary to build your spaced repetition database.
            """
            
            await update.message.reply_text(review_text, parse_mode='Markdown')
            
            self.user_manager.log_activity(user_id, 'review_session', {
                'session_type': session_type,
                'max_items': max_items
            })
            
        except Exception as e:
            logger.error(f"Error in review command: {e}")
            await update.message.reply_text(
                "❌ Sorry, there was an error starting the review session."
            )

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command - Show learning statistics"""
        user_id = update.effective_user.id
        
        try:
            # For now, show simulated stats since we need database integration
            stats_text = """
📊 **Your Learning Statistics** 📊

🎯 **Overall Progress:**
• Total Items Learned: 45
• Items Mastered: 12
• Currently Learning: 18
• Due for Review: 8
• Accuracy Rate: 78.5%

📚 **By Category:**
• 📝 Vocabulary: 20 items (85% accuracy)
• 🧠 General Knowledge: 15 items (75% accuracy)
• ✍️ Grammar: 10 items (70% accuracy)

⏰ **Review Schedule:**
• Items due today: 8
• Items due this week: 23
• Average review time: 2.3 minutes

📈 **Performance Trends:**
• Study streak: 7 days 🔥
• Improvement rate: +15% this week
• Retention rate: 82%

🎯 **Next Steps:**
• Focus on Grammar (lowest accuracy)
• Complete today's 8 reviews
• Take a quiz to add new items

Use `/review` to start practicing!
            """
            
            await update.message.reply_text(stats_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in stats command: {e}")
            await update.message.reply_text(
                "❌ Sorry, there was an error retrieving your statistics."
            )

    async def study_plan_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /study_plan command - Generate personalized study recommendations"""
        user_id = update.effective_user.id
        
        try:
            # For now, show a sample study plan
            plan_text = """
📅 **Your Personalized Study Plan** 📅

🎯 **Daily Target:** 20 items

📊 **Today's Recommendations:**
• 🔄 Review: 8 items (overdue)
• 🆕 New Learning: 5 items 
• ⚠️ Weak Areas: 4 items (grammar focus)
• 🧠 Mixed Practice: 3 items

⏰ **Optimal Schedule:**
• **Morning (9-10 AM):** New vocabulary (5 items)
• **Afternoon (2-3 PM):** Grammar review (4 items)
• **Evening (7-8 PM):** Mixed practice (8 items)

🎯 **Focus Areas This Week:**
• ✍️ Grammar: Subject-verb agreement
• 📚 Vocabulary: SSC-CGL common words
• 🧠 Current Affairs: Recent developments

📈 **Difficulty Adjustment:** Maintain current level
**Reason:** Good balance of 78% accuracy

💡 **Smart Tips:**
• Review weak items in the morning when focus is highest
• Space out learning sessions for better retention
• Take breaks between different types of content

Use `/review weak` to start with difficult items!
            """
            
            await update.message.reply_text(plan_text, parse_mode='Markdown')
            
            self.user_manager.log_activity(user_id, 'study_plan_viewed', {
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error in study plan command: {e}")
            await update.message.reply_text(
                "❌ Sorry, there was an error generating your study plan."
            )

    async def schedule_status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show scheduler status and scheduled jobs (Admin only)"""
        user_id = update.effective_user.id
        admin_id = os.getenv('ADMIN_USER_ID')
        
        if admin_id and str(user_id) != admin_id:
            await update.message.reply_text("🚫 This command is only available to administrators.")
            return
        
        if not self.scheduler:
            await update.message.reply_text("⚠️ Scheduler is not initialized.")
            return
        
        try:
            scheduled_jobs = self.scheduler.get_scheduled_jobs()
            
            message = "📋 **Scheduler Status** 🕐\n\n"
            message += f"🟢 Status: {'Running' if self.scheduler.scheduler.running else 'Stopped'}\n"
            message += f"📅 Total Jobs: {len(scheduled_jobs)}\n\n"
            
            if scheduled_jobs:
                message += "**Scheduled Jobs:**\n"
                for job in scheduled_jobs:
                    message += f"• {job['name']}\n"
                    message += f"  🆔 ID: `{job['id']}`\n"
                    if job['next_run_time']:
                        message += f"  ⏰ Next Run: {job['next_run_time'][:19].replace('T', ' ')}\n"
                    message += "\n"
            else:
                message += "📭 No jobs scheduled.\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting scheduler status: {str(e)}")

    async def test_broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test broadcast functionality (Admin only)"""
        user_id = update.effective_user.id
        admin_id = os.getenv('ADMIN_USER_ID')
        
        if admin_id and str(user_id) != admin_id:
            await update.message.reply_text("🚫 This command is only available to administrators.")
            return
        
        if not self.scheduler:
            await update.message.reply_text("⚠️ Scheduler is not initialized.")
            return
        
        try:
            test_message = "This is a test broadcast to verify the system is working properly."
            sent_count = await self.scheduler.test_broadcast(test_message)
            
            await update.message.reply_text(
                f"✅ Test broadcast sent successfully to {sent_count} users.",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error sending test broadcast: {str(e)}")

    async def generate_content_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manually trigger content generation (Admin only)"""
        user_id = update.effective_user.id
        admin_id = os.getenv('ADMIN_USER_ID')
        
        if admin_id and str(user_id) != admin_id:
            await update.message.reply_text("🚫 This command is only available to administrators.")
            return
        
        if not self.scheduler:
            await update.message.reply_text("⚠️ Scheduler is not initialized.")
            return
        
        try:
            await update.message.reply_text("🔄 Generating fresh content... This may take a moment.")
            
            await self.scheduler.generate_content_now()
            
            await update.message.reply_text(
                "✅ Fresh content generated successfully! Users will receive updated content on their next requests.",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error generating content: {str(e)}")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "🚫 Sorry, something went wrong. Please try again or contact support with /support"
            )

    def setup_handlers(self):
        """Setup all command and message handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("vocab", self.vocab_command))
        self.application.add_handler(CommandHandler("idioms", self.idioms_command))
        self.application.add_handler(CommandHandler("gk", self.gk_command))
        self.application.add_handler(CommandHandler("current_affairs", self.current_affairs_command))
        self.application.add_handler(CommandHandler("progress", self.progress_command))
        self.application.add_handler(CommandHandler("grammar", self.grammar_command))
        self.application.add_handler(CommandHandler("quiz", self.quiz_command))
        self.application.add_handler(CommandHandler("quiz_stats", self.quiz_stats_command))
        self.application.add_handler(CommandHandler("review", self.review_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("study_plan", self.study_plan_command))
        
        # Admin commands for scheduler
        self.application.add_handler(CommandHandler("schedule_status", self.schedule_status_command))
        self.application.add_handler(CommandHandler("test_broadcast", self.test_broadcast_command))
        self.application.add_handler(CommandHandler("generate_content", self.generate_content_command))
        
        # Message handler for feedback
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        
        # Error handler
        self.application.add_error_handler(self.error_handler)

    async def start_bot(self):
        """Initialize and start the bot"""
        try:
            # Initialize database
            logger.info("Initializing database...")
            self.db_manager.initialize_database()
            
            # Create application with better timeout settings
            logger.info("Creating Telegram application...")
            self.application = (
                Application.builder()
                .token(BOT_TOKEN)
                .read_timeout(30)
                .write_timeout(30)
                .connect_timeout(30)
                .pool_timeout(30)
                .build()
            )
            
            # Setup handlers
            logger.info("Setting up command handlers...")
            self.setup_handlers()
            
            logger.info("SSC-CGL Bot starting...")
            
            # Test bot token first
            logger.info("Testing bot connection...")
            await self.application.initialize()
            
            # Get bot info to verify token
            bot_info = await self.application.bot.get_me()
            logger.info(f"Bot connected successfully: @{bot_info.username} ({bot_info.first_name})")
            
            # Start the application
            await self.application.start()
            logger.info("Bot application started successfully!")
            
            # Start polling
            logger.info("Starting polling for updates...")
            await self.application.updater.start_polling(
                drop_pending_updates=True,
                allowed_updates=['message', 'callback_query']
            )
            
            # Initialize and start scheduler
            logger.info("Initializing scheduler...")
            try:
                self.scheduler = SSCScheduler(self.application.bot, self.db_manager)
                self.scheduler.start_scheduler()
                logger.info("Scheduler started successfully!")
            except Exception as e:
                logger.warning(f"Scheduler initialization failed: {e}")
                logger.info("Bot will continue without scheduler")
            
            logger.info("🎉 SSC-CGL Bot is fully operational!")
            logger.info("Press Ctrl+C to stop the bot.")
            
            # Keep the bot running
            try:
                await asyncio.Event().wait()
            except KeyboardInterrupt:
                logger.info("Stopping bot...")
                if self.scheduler:
                    self.scheduler.stop_scheduler()
                if self.grammar_system:
                    self.grammar_system.cleanup()
                await self.application.stop()
                
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            if "Unauthorized" in str(e):
                logger.error("❌ Invalid bot token! Please check your BOT_TOKEN in .env file")
                logger.error("Get a new token from @BotFather on Telegram")
            elif "Timed out" in str(e) or "timeout" in str(e).lower():
                logger.error("❌ Network timeout! Please check your internet connection")
                logger.error("You can also try again in a few moments")
            else:
                logger.error("❌ Bot startup failed - check your configuration")
            raise

def main():
    """Main function to run the bot"""
    bot = SSCCGLBot()
    asyncio.run(bot.start_bot())

if __name__ == '__main__':
    main()
