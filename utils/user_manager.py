# User Manager for SSC-CGL Bot
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class UserManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def register_user(self, user_data: Dict) -> bool:
        """Register a new user or update existing user info"""
        try:
            # Check if user already exists
            existing_user = self.db.get_user_by_telegram_id(user_data['telegram_id'])
            is_new_user = existing_user is None
            
            # Insert or update user
            user_id = self.db.insert_user(user_data)
            
            if user_id:
                # Initialize user stats if new user
                if is_new_user:
                    self._initialize_user_stats(user_id)
                    logger.info(f"New user registered: {user_data['telegram_id']}")
                else:
                    logger.info(f"User updated: {user_data['telegram_id']}")
                
                # Log registration activity
                self.log_activity(
                    user_data['telegram_id'], 
                    'user_registered' if is_new_user else 'user_updated',
                    user_data
                )
                
                return is_new_user
            
            return False
            
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return False
    
    def _initialize_user_stats(self, user_id: int):
        """Initialize statistics for a new user"""
        try:
            query = '''
                INSERT INTO user_stats (user_id, stat_date, streak_days)
                VALUES (?, ?, ?)
            '''
            params = (user_id, datetime.now().date(), 0)
            self.db.execute_update(query, params)
            
        except Exception as e:
            logger.error(f"Error initializing user stats: {e}")
    
    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict]:
        """Get user information by telegram ID"""
        return self.db.get_user_by_telegram_id(telegram_id)
    
    def get_user_id(self, telegram_id: int) -> Optional[int]:
        """Get internal user ID from telegram ID"""
        user = self.get_user_by_telegram_id(telegram_id)
        return user['id'] if user else None
    
    def update_user_activity(self, telegram_id: int):
        """Update user's last activity and streak"""
        try:
            user = self.get_user_by_telegram_id(telegram_id)
            if not user:
                return False
            
            user_id = user['id']
            today = datetime.now().date()
            
            # Update last active
            self.db.update_user_activity(user_id)
            
            # Update or create today's stats
            self._update_daily_stats(user_id, today)
            
            # Update streak
            self._update_streak(user_id, today)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating user activity: {e}")
            return False
    
    def _update_daily_stats(self, user_id: int, stat_date):
        """Update or create daily statistics"""
        try:
            # Check if today's stats exist
            existing_stats = self.db.execute_query(
                "SELECT * FROM user_stats WHERE user_id = ? AND stat_date = ?",
                (user_id, stat_date)
            )
            
            if not existing_stats:
                # Create new daily stats
                query = '''
                    INSERT INTO user_stats (user_id, stat_date)
                    VALUES (?, ?)
                '''
                self.db.execute_update(query, (user_id, stat_date))
            
        except Exception as e:
            logger.error(f"Error updating daily stats: {e}")
    
    def _update_streak(self, user_id: int, current_date):
        """Update user's learning streak"""
        try:
            # Get recent stats to calculate streak
            recent_stats = self.db.execute_query('''
                SELECT stat_date FROM user_stats 
                WHERE user_id = ? 
                ORDER BY stat_date DESC 
                LIMIT 7
            ''', (user_id,))
            
            if not recent_stats:
                return
            
            # Calculate streak
            streak_days = 1  # At least today
            yesterday = current_date - timedelta(days=1)
            
            for stat in recent_stats[1:]:  # Skip today
                stat_date = datetime.strptime(stat['stat_date'], '%Y-%m-%d').date()
                if stat_date == yesterday:
                    streak_days += 1
                    yesterday -= timedelta(days=1)
                else:
                    break
            
            # Update today's streak
            query = '''
                UPDATE user_stats 
                SET streak_days = ? 
                WHERE user_id = ? AND stat_date = ?
            '''
            self.db.execute_update(query, (streak_days, user_id, current_date))
            
        except Exception as e:
            logger.error(f"Error updating streak: {e}")
    
    def log_activity(self, telegram_id: int, activity_type: str, activity_data: Dict = None):
        """Log user activity"""
        try:
            user_id = self.get_user_id(telegram_id)
            if user_id:
                self.db.log_activity(user_id, activity_type, activity_data)
                self.update_user_activity(telegram_id)
                
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
    
    def increment_stat(self, telegram_id: int, stat_name: str, increment: int = 1):
        """Increment a specific user statistic"""
        try:
            user_id = self.get_user_id(telegram_id)
            if not user_id:
                return False
            
            today = datetime.now().date()
            
            # Ensure today's stats exist
            self._update_daily_stats(user_id, today)
            
            # Update the specific stat
            query = f'''
                UPDATE user_stats 
                SET {stat_name} = {stat_name} + ? 
                WHERE user_id = ? AND stat_date = ?
            '''
            
            # Validate stat_name to prevent SQL injection
            valid_stats = [
                'vocab_learned', 'idioms_learned', 'gk_reviewed', 
                'sentences_submitted', 'quizzes_taken', 'quiz_score_total'
            ]
            
            if stat_name in valid_stats:
                return self.db.execute_update(query, (increment, user_id, today))
            else:
                logger.error(f"Invalid stat name: {stat_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error incrementing stat {stat_name}: {e}")
            return False
    
    def get_user_stats(self, telegram_id: int) -> Optional[Dict]:
        """Get comprehensive user statistics"""
        try:
            user_id = self.get_user_id(telegram_id)
            if not user_id:
                return None
            
            stats = self.db.get_user_stats(user_id)
            
            if stats:
                # Add calculated fields
                total_reviews = stats.get('total_reviews', 0) or 0
                correct_reviews = stats.get('correct_reviews', 0) or 0
                
                if total_reviews > 0:
                    stats['accuracy_percentage'] = (correct_reviews / total_reviews) * 100
                else:
                    stats['accuracy_percentage'] = 0
                
                # Add quiz average
                quiz_score_total = stats.get('quiz_score_total', 0) or 0
                quizzes_taken = stats.get('quizzes_taken', 0) or 0
                
                if quizzes_taken > 0:
                    stats['quiz_average'] = quiz_score_total / quizzes_taken
                else:
                    stats['quiz_average'] = 0
                
                # Get weekly stats
                weekly_stats = self._get_weekly_stats(user_id)
                stats.update(weekly_stats)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return None
    
    def _get_weekly_stats(self, user_id: int) -> Dict:
        """Get statistics for the current week"""
        try:
            week_start = datetime.now().date() - timedelta(days=7)
            
            weekly_stats = self.db.execute_query('''
                SELECT 
                    SUM(vocab_learned) as week_vocab,
                    SUM(idioms_learned) as week_idioms,
                    SUM(gk_reviewed) as week_gk,
                    SUM(quizzes_taken) as week_quizzes,
                    SUM(sentences_submitted) as week_sentences
                FROM user_stats 
                WHERE user_id = ? AND stat_date >= ?
            ''', (user_id, week_start))
            
            if weekly_stats:
                return weekly_stats[0]
            
            return {
                'week_vocab': 0, 'week_idioms': 0, 'week_gk': 0,
                'week_quizzes': 0, 'week_sentences': 0
            }
            
        except Exception as e:
            logger.error(f"Error getting weekly stats: {e}")
            return {}
    
    def get_all_active_users(self) -> List[Dict]:
        """Get all active users for broadcasting"""
        return self.db.get_all_active_users()
    
    def toggle_notifications(self, telegram_id: int) -> bool:
        """Toggle user notifications on/off"""
        try:
            user = self.get_user_by_telegram_id(telegram_id)
            if not user:
                return False
            
            current_status = user.get('notifications_enabled', 1)
            new_status = 0 if current_status else 1
            
            query = "UPDATE users SET notifications_enabled = ? WHERE telegram_id = ?"
            return self.db.execute_update(query, (new_status, telegram_id))
            
        except Exception as e:
            logger.error(f"Error toggling notifications: {e}")
            return False
    
    def set_user_timezone(self, telegram_id: int, timezone: str) -> bool:
        """Set user's timezone"""
        try:
            query = "UPDATE users SET timezone = ? WHERE telegram_id = ?"
            return self.db.execute_update(query, (timezone, telegram_id))
            
        except Exception as e:
            logger.error(f"Error setting timezone: {e}")
            return False
