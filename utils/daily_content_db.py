# Database integration for daily content storage
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from database.db_manager import DatabaseManager
import json

logger = logging.getLogger(__name__)

class DailyContentDB:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def save_daily_content(self, content: Dict, date: datetime = None) -> bool:
        """Save daily content to database"""
        if date is None:
            date = datetime.now()
        
        try:
            date_str = date.strftime('%Y-%m-%d')
            
            # Prepare data for database
            vocab_json = json.dumps(content.get('vocab_data', []))
            idioms_json = json.dumps(content.get('idioms_data', []))
            gk_json = json.dumps(content.get('gk_data', []))
            current_affairs_json = json.dumps(content.get('current_affairs_data', []))
            
            # Insert or replace daily content
            query = '''
                INSERT OR REPLACE INTO daily_content 
                (content_date, vocab_data, idioms_data, gk_data, current_affairs_data)
                VALUES (?, ?, ?, ?, ?)
            '''
            
            params = (date_str, vocab_json, idioms_json, gk_json, current_affairs_json)
            
            if self.db.execute_update(query, params):
                logger.info(f"Saved daily content to database for {date_str}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error saving daily content to database: {e}")
            return False
    
    def load_daily_content(self, date: datetime = None) -> Optional[Dict]:
        """Load daily content from database"""
        if date is None:
            date = datetime.now()
        
        try:
            date_str = date.strftime('%Y-%m-%d')
            
            result = self.db.execute_query(
                "SELECT * FROM daily_content WHERE content_date = ?",
                (date_str,)
            )
            
            if result:
                content_row = result[0]
                
                # Parse JSON data
                daily_content = {
                    'date': date_str,
                    'vocab_data': json.loads(content_row['vocab_data']) if content_row['vocab_data'] else [],
                    'idioms_data': json.loads(content_row['idioms_data']) if content_row['idioms_data'] else [],
                    'gk_data': json.loads(content_row['gk_data']) if content_row['gk_data'] else [],
                    'current_affairs_data': json.loads(content_row['current_affairs_data']) if content_row['current_affairs_data'] else [],
                    'created_timestamp': content_row['created_timestamp']
                }
                
                # Add content stats
                daily_content['content_stats'] = {
                    'vocab_count': len(daily_content['vocab_data']),
                    'idioms_count': len(daily_content['idioms_data']),
                    'gk_count': len(daily_content['gk_data']),
                    'current_affairs_count': len(daily_content['current_affairs_data'])
                }
                
                logger.info(f"Loaded daily content from database for {date_str}")
                return daily_content
            
            return None
            
        except Exception as e:
            logger.error(f"Error loading daily content from database: {e}")
            return None
    
    def get_content_history(self, days: int = 7) -> List[Dict]:
        """Get content history for the last N days"""
        try:
            query = '''
                SELECT content_date, created_timestamp 
                FROM daily_content 
                ORDER BY content_date DESC 
                LIMIT ?
            '''
            
            results = self.db.execute_query(query, (days,))
            
            history = []
            for row in results:
                history.append({
                    'date': row['content_date'],
                    'created_timestamp': row['created_timestamp']
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting content history: {e}")
            return []
    
    def delete_old_content(self, days_to_keep: int = 30) -> bool:
        """Delete content older than specified days"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).strftime('%Y-%m-%d')
            
            query = "DELETE FROM daily_content WHERE content_date < ?"
            
            if self.db.execute_update(query, (cutoff_date,)):
                logger.info(f"Deleted content older than {cutoff_date}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting old content: {e}")
            return False
