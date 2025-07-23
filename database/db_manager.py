# Database Manager for SSC-CGL Bot
import sqlite3
import logging
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "database/user_data.db"):
        self.db_path = db_path
        self.connection = None
    
    def get_connection(self):
        """Get database connection"""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access
        return self.connection
    
    def initialize_database(self):
        """Initialize all database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    chat_id INTEGER,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    timezone TEXT DEFAULT 'Asia/Kolkata',
                    notifications_enabled BOOLEAN DEFAULT 1
                )
            ''')
            
            # User progress table for spaced repetition
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    content_id TEXT,
                    content_type TEXT, -- 'vocab', 'idiom', 'gk'
                    ease_factor REAL DEFAULT 2.5,
                    interval_days INTEGER DEFAULT 1,
                    repetitions INTEGER DEFAULT 0,
                    last_review TIMESTAMP,
                    next_review TIMESTAMP,
                    total_reviews INTEGER DEFAULT 0,
                    correct_reviews INTEGER DEFAULT 0,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(user_id, content_id, content_type)
                )
            ''')
            
            # User statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    stat_date DATE,
                    vocab_learned INTEGER DEFAULT 0,
                    idioms_learned INTEGER DEFAULT 0,
                    gk_reviewed INTEGER DEFAULT 0,
                    sentences_submitted INTEGER DEFAULT 0,
                    quizzes_taken INTEGER DEFAULT 0,
                    quiz_score_total INTEGER DEFAULT 0,
                    streak_days INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(user_id, stat_date)
                )
            ''')
            
            # Activity log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    activity_type TEXT,
                    activity_data TEXT, -- JSON data
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Quiz results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quiz_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    quiz_type TEXT,
                    quiz_date DATE,
                    total_questions INTEGER,
                    correct_answers INTEGER,
                    score_percentage REAL,
                    time_taken INTEGER, -- in seconds
                    questions_data TEXT, -- JSON of questions and answers
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Daily content table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_date DATE UNIQUE,
                    vocab_data TEXT, -- JSON
                    idioms_data TEXT, -- JSON
                    gk_data TEXT, -- JSON
                    current_affairs_data TEXT, -- JSON
                    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Feedback submissions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback_submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    submitted_text TEXT,
                    feedback_text TEXT,
                    grammar_score REAL,
                    suggestions TEXT, -- JSON
                    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            conn.rollback()
            raise
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute a SELECT query and return results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            return [dict(row) for row in cursor.fetchall()]
        
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return []
    
    def execute_update(self, query: str, params: tuple = None) -> bool:
        """Execute an INSERT/UPDATE/DELETE query"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            conn.commit()
            return True
        
        except Exception as e:
            logger.error(f"Error executing update: {e}")
            conn.rollback()
            return False
    
    def insert_user(self, user_data: Dict) -> Optional[int]:
        """Insert a new user or update existing user"""
        query = '''
            INSERT OR REPLACE INTO users 
            (telegram_id, username, first_name, last_name, chat_id, last_active)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        params = (
            user_data['telegram_id'],
            user_data.get('username'),
            user_data.get('first_name'),
            user_data.get('last_name'),
            user_data.get('chat_id'),
            datetime.now()
        )
        
        if self.execute_update(query, params):
            # Get the user ID
            result = self.execute_query(
                "SELECT id FROM users WHERE telegram_id = ?",
                (user_data['telegram_id'],)
            )
            return result[0]['id'] if result else None
        return None
    
    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict]:
        """Get user by telegram ID"""
        result = self.execute_query(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        return result[0] if result else None
    
    def get_all_active_users(self) -> List[Dict]:
        """Get all active users for broadcasting"""
        return self.execute_query(
            "SELECT * FROM users WHERE is_active = 1 AND notifications_enabled = 1"
        )
    
    def update_user_activity(self, user_id: int):
        """Update user's last active timestamp"""
        self.execute_update(
            "UPDATE users SET last_active = ? WHERE id = ?",
            (datetime.now(), user_id)
        )
    
    def log_activity(self, user_id: int, activity_type: str, activity_data: Dict = None):
        """Log user activity"""
        query = '''
            INSERT INTO activity_log (user_id, activity_type, activity_data)
            VALUES (?, ?, ?)
        '''
        params = (
            user_id,
            activity_type,
            json.dumps(activity_data) if activity_data else None
        )
        self.execute_update(query, params)
    
    def get_user_stats(self, user_id: int) -> Optional[Dict]:
        """Get comprehensive user statistics"""
        # Get current stats
        current_stats = self.execute_query(
            "SELECT * FROM user_stats WHERE user_id = ? ORDER BY stat_date DESC LIMIT 1",
            (user_id,)
        )
        
        # Get total progress
        progress_stats = self.execute_query('''
            SELECT 
                COUNT(*) as total_items,
                AVG(ease_factor) as avg_ease_factor,
                SUM(total_reviews) as total_reviews,
                SUM(correct_reviews) as correct_reviews
            FROM user_progress 
            WHERE user_id = ?
        ''', (user_id,))
        
        # Get quiz stats
        quiz_stats = self.execute_query('''
            SELECT 
                COUNT(*) as total_quizzes,
                AVG(score_percentage) as avg_score,
                MAX(score_percentage) as best_score
            FROM quiz_results 
            WHERE user_id = ?
        ''', (user_id,))
        
        if current_stats:
            stats = current_stats[0]
            if progress_stats:
                stats.update(progress_stats[0])
            if quiz_stats:
                stats.update(quiz_stats[0])
            return stats
        
        return None
    
    def close_connection(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
