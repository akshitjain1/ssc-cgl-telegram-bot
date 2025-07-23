# Advanced Scheduler for SSC-CGL Bot using APScheduler
import logging
import asyncio
from datetime import datetime, timedelta, time
import os
from typing import List, Dict, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import pytz

# Import our modules
from utils.generate_daily_content import GeminiContentGenerator
from utils.daily_content_db import DailyContentDB
from database.db_manager import DatabaseManager
from utils.user_manager import UserManager

logger = logging.getLogger(__name__)

class SSCScheduler:
    def __init__(self, bot_instance=None, db_manager: DatabaseManager = None):
        self.bot = bot_instance
        self.db_manager = db_manager or DatabaseManager()
        self.user_manager = UserManager(self.db_manager)
        self.content_generator = GeminiContentGenerator()
        self.content_db = DailyContentDB(self.db_manager)
        
        # Configure timezone first
        self.timezone = pytz.timezone(os.getenv('TIMEZONE', 'Asia/Kolkata'))
        
        # Configure APScheduler
        self.scheduler = self._setup_scheduler()
        
        # Scheduling configuration
        self.daily_schedule = {
            'content_generation': time(6, 0),    # 6:00 AM - Generate content
            'morning_vocab': time(8, 0),         # 8:00 AM - Send vocabulary
            'current_affairs': time(9, 0),       # 9:00 AM - Send current affairs
            'afternoon_practice': time(14, 0),   # 2:00 PM - Practice questions
            'evening_review': time(18, 0),       # 6:00 PM - Spaced repetition
            'night_cleanup': time(2, 0)          # 2:00 AM - Maintenance
        }
        
        logger.info("SSC Scheduler initialized successfully")
    
    def _setup_scheduler(self) -> AsyncIOScheduler:
        """Setup APScheduler with proper configuration"""
        # Use memory jobstore to avoid pickle issues with SQLite connections
        from apscheduler.jobstores.memory import MemoryJobStore
        
        jobstores = {
            'default': MemoryJobStore()
        }
        
        executors = {
            'default': AsyncIOExecutor()
        }
        
        job_defaults = {
            'coalesce': True,  # Combine multiple pending executions
            'max_instances': 1,  # Prevent multiple instances of the same job
            'misfire_grace_time': 300  # 5 minutes grace time for missed jobs
        }
        
        scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=self.timezone
        )
        
        # Add event listeners
        scheduler.add_listener(self._job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        
        return scheduler
    
    def _job_listener(self, event):
        """Listen to job execution events for logging"""
        if event.exception:
            logger.error(f"Job {event.job_id} crashed: {event.exception}")
        else:
            logger.info(f"Job {event.job_id} executed successfully")
    
    async def generate_daily_content_job(self):
        """Job to generate daily content using Gemini API"""
        try:
            logger.info("Starting daily content generation job...")
            
            # Generate today's content
            today = datetime.now(self.timezone).date()
            daily_content = self.content_generator.generate_all_daily_content(
                datetime.combine(today, datetime.min.time())
            )
            
            if daily_content:
                # Save to database
                self.content_db.save_daily_content(daily_content)
                logger.info(f"Successfully generated and saved daily content for {today}")
                
                # Send notification to admins (optional)
                await self._notify_admins_content_ready(daily_content)
            else:
                logger.error("Failed to generate daily content")
                
        except Exception as e:
            logger.error(f"Error in daily content generation job: {e}")
    
    async def send_morning_vocab_job(self):
        """Job to send morning vocabulary to all users"""
        try:
            logger.info("Starting morning vocabulary broadcast...")
            
            # Get today's vocabulary
            from utils.content_manager import ContentManager
            content_manager = ContentManager()
            vocab_data = content_manager.get_daily_vocab(count=5)
            
            if not vocab_data:
                logger.warning("No vocabulary data available for broadcast")
                return
            
            # Format message
            message = "🌅 **Good Morning! Today's Vocabulary** 📚\n\n"
            
            for idx, word_data in enumerate(vocab_data, 1):
                message += f"**{idx}. {word_data['word'].upper()}**\n"
                message += f"📖 *Meaning:* {word_data['meaning']}\n"
                message += f"💡 *Example:* {word_data['example']}\n"
                if word_data.get('synonym'):
                    message += f"🔄 *Synonym:* {word_data['synonym']}\n"
                message += "\n"
            
            message += "☕ *Start your day with new words! Practice using them in sentences.*"
            
            # Send to all active users
            sent_count = await self._broadcast_message(message)
            logger.info(f"Morning vocabulary sent to {sent_count} users")
            
        except Exception as e:
            logger.error(f"Error in morning vocabulary job: {e}")
    
    async def send_current_affairs_job(self):
        """Job to send current affairs to all users"""
        try:
            logger.info("Starting current affairs broadcast...")
            
            from utils.content_manager import ContentManager
            content_manager = ContentManager()
            current_affairs = content_manager.get_daily_current_affairs(count=3)
            
            if not current_affairs:
                logger.warning("No current affairs data available for broadcast")
                return
            
            message = "📰 **Daily Current Affairs Update** 🌍\n\n"
            
            for idx, affair in enumerate(current_affairs, 1):
                message += f"**{idx}. {affair.get('title', 'News Update')}**\n"
                message += f"📄 {affair.get('description', 'No description available')}\n"
                if affair.get('source'):
                    message += f"📺 *Source:* {affair['source']}\n"
                message += "\n"
            
            message += "🔄 *Stay informed for better exam preparation!*"
            
            sent_count = await self._broadcast_message(message)
            logger.info(f"Current affairs sent to {sent_count} users")
            
        except Exception as e:
            logger.error(f"Error in current affairs job: {e}")
    
    async def send_practice_questions_job(self):
        """Job to send afternoon practice questions"""
        try:
            logger.info("Starting practice questions broadcast...")
            
            from utils.content_manager import ContentManager
            content_manager = ContentManager()
            gk_data = content_manager.get_daily_gk(count=3)
            
            if not gk_data:
                logger.warning("No GK data available for practice questions")
                return
            
            message = "🧠 **Afternoon Practice Session** ❓\n\n"
            message += "*Test your knowledge with these questions:*\n\n"
            
            for idx, gk_item in enumerate(gk_data, 1):
                message += f"**Q{idx}.** {gk_item.get('question', 'Sample question')}\n"
                message += f"🏷️ *Category:* {gk_item.get('category', 'General')}\n\n"
            
            message += "💭 *Think about the answers, then use /gk to see the solutions!*"
            
            sent_count = await self._broadcast_message(message)
            logger.info(f"Practice questions sent to {sent_count} users")
            
        except Exception as e:
            logger.error(f"Error in practice questions job: {e}")
    
    async def send_spaced_repetition_job(self):
        """Job to send spaced repetition reminders"""
        try:
            logger.info("Starting spaced repetition reminders...")
            
            # Get all active users
            active_users = self.user_manager.get_all_active_users()
            
            reminder_count = 0
            for user in active_users:
                # Check if user has items due for review
                # This would integrate with the spaced repetition system
                # For now, send a general reminder
                
                user_chat_id = user.get('chat_id')
                if user_chat_id and self.bot:
                    try:
                        message = "🔄 **Evening Review Time** 🎯\n\n"
                        message += "Time to review what you've learned!\n\n"
                        message += "📚 Use /vocab to review today's words\n"
                        message += "🗣️ Use /idioms to practice phrases\n"
                        message += "🧠 Use /gk to test your knowledge\n"
                        message += "📊 Use /progress to see your stats\n\n"
                        message += "🌟 *Consistent review leads to better retention!*"
                        
                        await self.bot.send_message(
                            chat_id=user_chat_id,
                            text=message,
                            parse_mode='Markdown'
                        )
                        reminder_count += 1
                        
                        # Small delay to avoid hitting rate limits
                        await asyncio.sleep(0.1)
                        
                    except Exception as e:
                        logger.warning(f"Failed to send reminder to user {user['telegram_id']}: {e}")
            
            logger.info(f"Spaced repetition reminders sent to {reminder_count} users")
            
        except Exception as e:
            logger.error(f"Error in spaced repetition job: {e}")
    
    async def cleanup_job(self):
        """Job to perform maintenance and cleanup"""
        try:
            logger.info("Starting daily cleanup job...")
            
            # Clean old content (keep last 30 days)
            self.content_db.delete_old_content(days_to_keep=30)
            
            # Clean old activity logs (keep last 90 days)
            cutoff_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
            self.db_manager.execute_update(
                "DELETE FROM activity_log WHERE timestamp < ?",
                (cutoff_date,)
            )
            
            # Update user statistics
            await self._update_user_statistics()
            
            logger.info("Daily cleanup completed successfully")
            
        except Exception as e:
            logger.error(f"Error in cleanup job: {e}")
    
    async def _broadcast_message(self, message: str) -> int:
        """Broadcast message to all active users"""
        if not self.bot:
            logger.warning("Bot instance not available for broadcasting")
            return 0
        
        active_users = self.user_manager.get_all_active_users()
        sent_count = 0
        
        for user in active_users:
            chat_id = user.get('chat_id')
            if chat_id:
                try:
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                    sent_count += 1
                    
                    # Rate limiting - small delay between messages
                    await asyncio.sleep(0.05)  # 50ms delay
                    
                except Exception as e:
                    logger.warning(f"Failed to send message to user {user['telegram_id']}: {e}")
        
        return sent_count
    
    async def _notify_admins_content_ready(self, daily_content: Dict):
        """Notify admin users that daily content is ready"""
        admin_id = os.getenv('ADMIN_USER_ID')
        if admin_id and self.bot:
            try:
                stats = daily_content.get('content_stats', {})
                message = f"✅ **Daily Content Generated Successfully**\n\n"
                message += f"📅 Date: {daily_content['date']}\n"
                message += f"📚 Vocabulary: {stats.get('vocab_count', 0)} words\n"
                message += f"🗣️ Idioms: {stats.get('idioms_count', 0)} phrases\n"
                message += f"🧠 GK: {stats.get('gk_count', 0)} questions\n"
                message += f"📰 Current Affairs: {stats.get('current_affairs_count', 0)} items\n"
                message += f"⏰ Generated at: {datetime.now().strftime('%H:%M:%S')}"
                
                await self.bot.send_message(
                    chat_id=int(admin_id),
                    text=message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.warning(f"Failed to notify admin: {e}")
    
    async def _update_user_statistics(self):
        """Update daily user statistics"""
        try:
            # This would update various user statistics
            # For now, just log the operation
            total_users = len(self.user_manager.get_all_active_users())
            logger.info(f"Updated statistics for {total_users} users")
        except Exception as e:
            logger.error(f"Error updating user statistics: {e}")
    
    def schedule_daily_jobs(self):
        """Schedule all daily recurring jobs"""
        try:
            # Daily content generation
            self.scheduler.add_job(
                func=self.generate_daily_content_job,
                trigger=CronTrigger(
                    hour=self.daily_schedule['content_generation'].hour,
                    minute=self.daily_schedule['content_generation'].minute,
                    timezone=self.timezone
                ),
                id='daily_content_generation',
                name='Generate Daily Content',
                replace_existing=True
            )
            
            # Morning vocabulary
            self.scheduler.add_job(
                func=self.send_morning_vocab_job,
                trigger=CronTrigger(
                    hour=self.daily_schedule['morning_vocab'].hour,
                    minute=self.daily_schedule['morning_vocab'].minute,
                    timezone=self.timezone
                ),
                id='morning_vocab',
                name='Morning Vocabulary Broadcast',
                replace_existing=True
            )
            
            # Current affairs
            self.scheduler.add_job(
                func=self.send_current_affairs_job,
                trigger=CronTrigger(
                    hour=self.daily_schedule['current_affairs'].hour,
                    minute=self.daily_schedule['current_affairs'].minute,
                    timezone=self.timezone
                ),
                id='current_affairs',
                name='Current Affairs Broadcast',
                replace_existing=True
            )
            
            # Practice questions
            self.scheduler.add_job(
                func=self.send_practice_questions_job,
                trigger=CronTrigger(
                    hour=self.daily_schedule['afternoon_practice'].hour,
                    minute=self.daily_schedule['afternoon_practice'].minute,
                    timezone=self.timezone
                ),
                id='practice_questions',
                name='Practice Questions Broadcast',
                replace_existing=True
            )
            
            # Evening review
            self.scheduler.add_job(
                func=self.send_spaced_repetition_job,
                trigger=CronTrigger(
                    hour=self.daily_schedule['evening_review'].hour,
                    minute=self.daily_schedule['evening_review'].minute,
                    timezone=self.timezone
                ),
                id='evening_review',
                name='Evening Review Reminders',
                replace_existing=True
            )
            
            # Daily cleanup
            self.scheduler.add_job(
                func=self.cleanup_job,
                trigger=CronTrigger(
                    hour=self.daily_schedule['night_cleanup'].hour,
                    minute=self.daily_schedule['night_cleanup'].minute,
                    timezone=self.timezone
                ),
                id='daily_cleanup',
                name='Daily Cleanup',
                replace_existing=True
            )
            
            logger.info("All daily jobs scheduled successfully")
            
        except Exception as e:
            logger.error(f"Error scheduling daily jobs: {e}")
    
    def schedule_one_time_job(self, job_func, run_time: datetime, job_id: str):
        """Schedule a one-time job"""
        try:
            self.scheduler.add_job(
                func=job_func,
                trigger=DateTrigger(run_date=run_time, timezone=self.timezone),
                id=job_id,
                name=f'One-time job: {job_id}',
                replace_existing=True
            )
            logger.info(f"One-time job '{job_id}' scheduled for {run_time}")
        except Exception as e:
            logger.error(f"Error scheduling one-time job: {e}")
    
    def start_scheduler(self):
        """Start the scheduler"""
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                self.schedule_daily_jobs()
                logger.info("Scheduler started successfully")
            else:
                logger.warning("Scheduler is already running")
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=False)
                logger.info("Scheduler stopped successfully")
            else:
                logger.warning("Scheduler is not running")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    def get_scheduled_jobs(self) -> List[Dict]:
        """Get information about all scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            job_info = {
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            }
            jobs.append(job_info)
        return jobs
    
    async def test_broadcast(self, message: str) -> int:
        """Test broadcast functionality"""
        logger.info("Testing broadcast functionality...")
        return await self._broadcast_message(f"🧪 **Test Message**\n\n{message}")
    
    async def generate_content_now(self):
        """Manually trigger content generation"""
        logger.info("Manually triggering content generation...")
        await self.generate_daily_content_job()

# Helper function to start scheduler
async def start_scheduler_for_bot(bot_instance, db_manager: DatabaseManager):
    """Initialize and start scheduler for the bot"""
    scheduler = SSCScheduler(bot_instance, db_manager)
    scheduler.start_scheduler()
    return scheduler
