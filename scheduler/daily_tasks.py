# Daily scheduling tasks for the SSC-CGL bot
import asyncio
import schedule
import time
from datetime import datetime, timedelta
import logging
from utils.fetch_current_affairs import get_current_affairs
from utils.spaced_repetition import SpacedRepetition

logger = logging.getLogger(__name__)

class DailyScheduler:
    def __init__(self, bot_instance=None):
        self.bot = bot_instance
        self.sr = SpacedRepetition()
    
    async def send_daily_vocab(self):
        """Send daily vocabulary to all users"""
        try:
            logger.info("Sending daily vocabulary...")
            # This would fetch users from database and send vocab
            # For now, it's a placeholder
            vocab_message = "🔤 *Daily Vocabulary*\n\nWord of the day will be sent here!"
            # await self.bot.send_message_to_all_users(vocab_message)
            logger.info("Daily vocabulary sent successfully")
        except Exception as e:
            logger.error(f"Error sending daily vocabulary: {e}")
    
    async def send_current_affairs(self):
        """Send current affairs update"""
        try:
            logger.info("Fetching and sending current affairs...")
            current_affairs = get_current_affairs()
            
            if current_affairs:
                message = "📰 *Today's Current Affairs*\n\n"
                for idx, article in enumerate(current_affairs[:3], 1):
                    message += f"{idx}. *{article['title']}*\n"
                    message += f"   {article['description'][:100]}...\n\n"
                
                # await self.bot.send_message_to_all_users(message)
                logger.info("Current affairs sent successfully")
            
        except Exception as e:
            logger.error(f"Error sending current affairs: {e}")
    
    async def send_practice_questions(self):
        """Send daily practice questions"""
        try:
            logger.info("Sending daily practice questions...")
            # This would generate practice questions based on user progress
            practice_message = "❓ *Daily Practice Questions*\n\nYour personalized questions are ready!"
            # await self.bot.send_message_to_all_users(practice_message)
            logger.info("Practice questions sent successfully")
        except Exception as e:
            logger.error(f"Error sending practice questions: {e}")
    
    async def update_spaced_repetition(self):
        """Update spaced repetition schedules for all users"""
        try:
            logger.info("Updating spaced repetition schedules...")
            # This would process all users' spaced repetition data
            # and send personalized review reminders
            logger.info("Spaced repetition schedules updated")
        except Exception as e:
            logger.error(f"Error updating spaced repetition: {e}")
    
    async def cleanup_old_data(self):
        """Clean up old data from database"""
        try:
            logger.info("Cleaning up old data...")
            # Remove old logs, temporary data, etc.
            logger.info("Old data cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def schedule_daily_tasks(self):
        """Schedule all daily tasks"""
        # Morning tasks
        schedule.every().day.at("08:00").do(lambda: asyncio.create_task(self.send_daily_vocab()))
        schedule.every().day.at("09:00").do(lambda: asyncio.create_task(self.send_current_affairs()))
        
        # Afternoon tasks
        schedule.every().day.at("14:00").do(lambda: asyncio.create_task(self.send_practice_questions()))
        
        # Evening tasks
        schedule.every().day.at("18:00").do(lambda: asyncio.create_task(self.update_spaced_repetition()))
        
        # Maintenance tasks
        schedule.every().day.at("02:00").do(lambda: asyncio.create_task(self.cleanup_old_data()))
        
        logger.info("Daily tasks scheduled successfully")
    
    def run_scheduler(self):
        """Run the scheduler"""
        logger.info("Starting daily scheduler...")
        self.schedule_daily_tasks()
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

# Function to start scheduler in background
async def start_scheduler(bot_instance=None):
    """Start the daily scheduler"""
    scheduler = DailyScheduler(bot_instance)
    
    # Run scheduler in a separate thread or process
    import threading
    scheduler_thread = threading.Thread(target=scheduler.run_scheduler, daemon=True)
    scheduler_thread.start()
    
    logger.info("Daily scheduler started in background")

if __name__ == "__main__":
    # For testing purposes
    scheduler = DailyScheduler()
    scheduler.run_scheduler()
