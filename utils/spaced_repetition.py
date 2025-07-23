# Spaced repetition algorithm for learning optimization
from datetime import datetime, timedelta
import json
import math
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

class ItemType(Enum):
    VOCABULARY = "vocabulary"
    IDIOM = "idiom"
    GRAMMAR = "grammar"
    QUIZ_QUESTION = "quiz_question"
    GENERAL_KNOWLEDGE = "general_knowledge"
    CURRENT_AFFAIRS = "current_affairs"

class LearningStage(Enum):
    NEW = "new"
    LEARNING = "learning"
    REVIEW = "review"
    MASTERED = "mastered"

@dataclass
class ReviewItem:
    item_id: str
    item_type: ItemType
    content: Dict
    stage: LearningStage
    priority: float
    days_overdue: int
    difficulty_score: float

@dataclass
class LearningStats:
    total_items: int
    new_items: int
    learning_items: int
    review_items: int
    mastered_items: int
    due_items: int
    accuracy_rate: float
    streak_days: int
    total_study_time: float

class SpacedRepetition:
    def __init__(self, db_manager=None):
        # SuperMemo 2 algorithm parameters
        self.ease_factor_default = 2.5
        self.ease_factor_min = 1.3
        self.grade_threshold = 3  # Minimum grade for successful recall
        self.db_manager = db_manager
        
        # Enhanced parameters
        self.mastery_threshold = 21  # Days interval for mastery
        self.max_daily_reviews = 50  # Maximum reviews per day
        self.learning_steps = [1, 10]  # Minutes for learning phase
        self.graduation_interval = 1  # Days to graduate from learning
        self.easy_bonus = 1.3  # Bonus multiplier for easy responses
    
    def calculate_next_review(self, interval, ease_factor, grade, repetitions, item_stage=LearningStage.REVIEW):
        """
        Enhanced spaced repetition calculation with learning stages
        
        Args:
            interval: Current interval in days
            ease_factor: Current ease factor
            grade: User's performance grade (0-5)
            repetitions: Number of successful repetitions
            item_stage: Current learning stage
        
        Returns:
            dict: Contains next_interval, new_ease_factor, new_repetitions, new_stage
        """
        if grade < self.grade_threshold:
            # Failed recall - reset to learning phase
            if item_stage == LearningStage.NEW:
                new_interval = self.learning_steps[0] / (24 * 60)  # Convert minutes to days
                new_stage = LearningStage.LEARNING
            else:
                new_interval = 1
                new_stage = LearningStage.LEARNING
            
            new_repetitions = 0
            new_ease_factor = max(ease_factor - 0.2, self.ease_factor_min)
        else:
            # Successful recall
            new_repetitions = repetitions + 1
            
            if item_stage == LearningStage.NEW:
                # First successful review
                new_interval = self.learning_steps[0] / (24 * 60)
                new_stage = LearningStage.LEARNING
                new_ease_factor = ease_factor
            elif item_stage == LearningStage.LEARNING:
                # In learning phase
                if new_repetitions >= len(self.learning_steps):
                    new_interval = self.graduation_interval
                    new_stage = LearningStage.REVIEW
                else:
                    new_interval = self.learning_steps[new_repetitions - 1] / (24 * 60)
                    new_stage = LearningStage.LEARNING
                new_ease_factor = ease_factor
            else:
                # In review phase
                if new_repetitions == 1:
                    new_interval = 1
                elif new_repetitions == 2:
                    new_interval = 6
                else:
                    new_interval = math.ceil(interval * ease_factor)
                
                # Apply easy bonus for grade 5
                if grade == 5:
                    new_interval = math.ceil(new_interval * self.easy_bonus)
                
                # Check for mastery
                if new_interval >= self.mastery_threshold:
                    new_stage = LearningStage.MASTERED
                else:
                    new_stage = LearningStage.REVIEW
                
                # Update ease factor based on grade
                new_ease_factor = ease_factor + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02))
                new_ease_factor = max(new_ease_factor, self.ease_factor_min)
        
        return {
            'next_interval': new_interval,
            'ease_factor': new_ease_factor,
            'repetitions': new_repetitions,
            'stage': new_stage,
            'next_review_date': datetime.now() + timedelta(days=new_interval)
        }
    
    def get_due_items(self, user_progress, max_items=None, item_types=None):
        """
        Get items that are due for review with enhanced filtering
        
        Args:
            user_progress: Dictionary containing user's learning progress
            max_items: Maximum number of items to return
            item_types: List of item types to filter by
        
        Returns:
            list: ReviewItem objects that need to be reviewed
        """
        due_items = []
        current_time = datetime.now()
        max_items = max_items or self.max_daily_reviews
        
        for item_id, progress in user_progress.items():
            # Filter by item type if specified
            if item_types and progress.get('type') not in item_types:
                continue
                
            next_review = datetime.fromisoformat(progress.get('next_review_date', current_time.isoformat()))
            
            if next_review <= current_time:
                priority = self._calculate_priority(progress, current_time)
                days_overdue = max(0, (current_time - next_review).days)
                
                # Calculate difficulty score
                difficulty_score = self._calculate_difficulty_score(progress)
                
                # Determine learning stage
                stage_value = progress.get('stage', LearningStage.NEW.value)
                stage = LearningStage(stage_value) if isinstance(stage_value, str) else stage_value
                
                # Determine item type
                type_value = progress.get('type', ItemType.VOCABULARY.value)
                try:
                    item_type = ItemType(type_value) if isinstance(type_value, str) else type_value
                except ValueError:
                    item_type = ItemType.VOCABULARY  # Default fallback
                
                review_item = ReviewItem(
                    item_id=item_id,
                    item_type=item_type,
                    content=progress.get('content', {}),
                    stage=stage,
                    priority=priority,
                    days_overdue=days_overdue,
                    difficulty_score=difficulty_score
                )
                
                due_items.append(review_item)
        
        # Sort by priority (higher priority first)
        due_items.sort(key=lambda x: x.priority, reverse=True)
        
        # Return limited number of items
        return due_items[:max_items]

    def _calculate_difficulty_score(self, progress):
        """Calculate difficulty score based on user performance"""
        total_reviews = progress.get('total_reviews', 0)
        correct_reviews = progress.get('correct_reviews', 0)
        
        if total_reviews == 0:
            return 1.0  # New items are moderately difficult
        
        accuracy = correct_reviews / total_reviews
        ease_factor = progress.get('ease_factor', self.ease_factor_default)
        
        # Lower accuracy and ease factor = higher difficulty
        difficulty = (1 - accuracy) + (3.0 - ease_factor) / 2.0
        return max(0.1, min(2.0, difficulty))

    def get_learning_stats(self, user_progress):
        """Get comprehensive learning statistics"""
        current_time = datetime.now()
        stats = {
            'total_items': 0,
            'new_items': 0,
            'learning_items': 0,
            'review_items': 0,
            'mastered_items': 0,
            'due_items': 0,
            'total_reviews': 0,
            'correct_reviews': 0,
            'study_streak': 0
        }
        
        for item_id, progress in user_progress.items():
            stats['total_items'] += 1
            stats['total_reviews'] += progress.get('total_reviews', 0)
            stats['correct_reviews'] += progress.get('correct_reviews', 0)
            
            stage = progress.get('stage', LearningStage.NEW.value)
            if stage == LearningStage.NEW.value:
                stats['new_items'] += 1
            elif stage == LearningStage.LEARNING.value:
                stats['learning_items'] += 1
            elif stage == LearningStage.REVIEW.value:
                stats['review_items'] += 1
            elif stage == LearningStage.MASTERED.value:
                stats['mastered_items'] += 1
            
            # Check if item is due
            next_review = datetime.fromisoformat(progress.get('next_review_date', current_time.isoformat()))
            if next_review <= current_time:
                stats['due_items'] += 1
        
        # Calculate accuracy rate
        if stats['total_reviews'] > 0:
            stats['accuracy_rate'] = stats['correct_reviews'] / stats['total_reviews']
        else:
            stats['accuracy_rate'] = 0.0
        
        return LearningStats(
            total_items=stats['total_items'],
            new_items=stats['new_items'],
            learning_items=stats['learning_items'],
            review_items=stats['review_items'],
            mastered_items=stats['mastered_items'],
            due_items=stats['due_items'],
            accuracy_rate=stats['accuracy_rate'],
            streak_days=stats['study_streak'],
            total_study_time=0.0  # Would be calculated from session data
        )
    
    def _calculate_priority(self, progress, current_time):
        """Calculate priority based on how overdue an item is"""
        next_review = datetime.fromisoformat(progress.get('next_review_date', current_time.isoformat()))
        days_overdue = (current_time - next_review).days
        ease_factor = progress.get('ease_factor', self.ease_factor_default)
        
        # Higher priority for overdue items and difficult items (low ease factor)
        priority = days_overdue + (3.0 - ease_factor)
        return max(priority, 0)
    
    def initialize_item(self, item_id, item_type, content=None):
        """Initialize a new item for spaced repetition with enhanced tracking"""
        return {
            'item_id': item_id,
            'type': item_type.value if isinstance(item_type, ItemType) else item_type,
            'content': content or {},
            'interval': 1,
            'ease_factor': self.ease_factor_default,
            'repetitions': 0,
            'stage': LearningStage.NEW.value,
            'next_review_date': datetime.now().isoformat(),
            'created_date': datetime.now().isoformat(),
            'last_review_date': None,
            'total_reviews': 0,
            'correct_reviews': 0,
            'review_history': [],
            'difficulty_level': 1.0,
            'tags': [],
            'source': 'system'
        }

    def update_progress(self, progress, grade, response_time=None):
        """Update progress after a review session with enhanced tracking"""
        current_stage = LearningStage(progress.get('stage', LearningStage.NEW.value))
        
        result = self.calculate_next_review(
            progress['interval'],
            progress['ease_factor'],
            grade,
            progress['repetitions'],
            current_stage
        )
        
        # Add to review history
        review_entry = {
            'date': datetime.now().isoformat(),
            'grade': grade,
            'response_time': response_time,
            'previous_interval': progress['interval'],
            'new_interval': result['next_interval']
        }
        
        review_history = progress.get('review_history', [])
        review_history.append(review_entry)
        
        # Keep only last 20 reviews
        if len(review_history) > 20:
            review_history = review_history[-20:]
        
        progress.update({
            'interval': result['next_interval'],
            'ease_factor': result['ease_factor'],
            'repetitions': result['repetitions'],
            'stage': result['stage'].value,
            'next_review_date': result['next_review_date'].isoformat(),
            'last_review_date': datetime.now().isoformat(),
            'total_reviews': progress.get('total_reviews', 0) + 1,
            'correct_reviews': progress.get('correct_reviews', 0) + (1 if grade >= self.grade_threshold else 0),
            'review_history': review_history
        })
        
        # Update difficulty level based on recent performance
        self._update_difficulty_level(progress)
        
        return progress

    def _update_difficulty_level(self, progress):
        """Update difficulty level based on recent performance"""
        review_history = progress.get('review_history', [])
        if len(review_history) < 3:
            return
        
        # Look at last 5 reviews
        recent_reviews = review_history[-5:]
        recent_grades = [r['grade'] for r in recent_reviews]
        avg_grade = sum(recent_grades) / len(recent_grades)
        
        # Adjust difficulty based on performance
        if avg_grade >= 4.5:
            progress['difficulty_level'] = max(0.5, progress.get('difficulty_level', 1.0) - 0.1)
        elif avg_grade < 3.0:
            progress['difficulty_level'] = min(2.0, progress.get('difficulty_level', 1.0) + 0.2)

    def create_review_session(self, user_id, session_type='mixed', max_items=10):
        """Create an optimized review session"""
        if not self.db_manager:
            return []
        
        # Load user progress from database
        user_progress = self._load_user_progress(user_id)
        
        # Get due items based on session type
        if session_type == 'new':
            item_types = None
            due_items = [item for item in self.get_due_items(user_progress, max_items) 
                        if item.stage == LearningStage.NEW]
        elif session_type == 'review':
            due_items = [item for item in self.get_due_items(user_progress, max_items) 
                        if item.stage in [LearningStage.LEARNING, LearningStage.REVIEW]]
        elif session_type == 'weak_areas':
            due_items = [item for item in self.get_due_items(user_progress, max_items) 
                        if item.difficulty_score > 1.0]
        else:  # mixed
            due_items = self.get_due_items(user_progress, max_items)
        
        return due_items[:max_items]

    def get_retention_prediction(self, progress):
        """Predict retention probability for an item"""
        if progress.get('total_reviews', 0) == 0:
            return 0.5  # 50% for new items
        
        ease_factor = progress.get('ease_factor', self.ease_factor_default)
        days_since_last_review = 0
        
        if progress.get('last_review_date'):
            last_review = datetime.fromisoformat(progress['last_review_date'])
            days_since_last_review = (datetime.now() - last_review).days
        
        # Simple retention model based on ease factor and time
        retention = ease_factor / 3.0 * math.exp(-days_since_last_review / 10.0)
        return max(0.1, min(0.95, retention))

    def suggest_study_plan(self, user_id, target_items_per_day=20):
        """Generate personalized study plan"""
        user_progress = self._load_user_progress(user_id)
        stats = self.get_learning_stats(user_progress)
        due_items = self.get_due_items(user_progress)
        
        plan = {
            'daily_target': target_items_per_day,
            'current_due': len(due_items),
            'recommended_sessions': [],
            'focus_areas': [],
            'difficulty_adjustment': 'maintain'
        }
        
        # Analyze weak areas
        weak_items = [item for item in due_items if item.difficulty_score > 1.2]
        if weak_items:
            weak_types = {}
            for item in weak_items:
                item_type = item.item_type.value
                weak_types[item_type] = weak_types.get(item_type, 0) + 1
            
            plan['focus_areas'] = [f"{k} ({v} items)" for k, v in weak_types.items()]
        
        # Recommend session distribution
        if stats.due_items > target_items_per_day:
            plan['recommended_sessions'] = [
                {'type': 'review', 'items': target_items_per_day // 2},
                {'type': 'new', 'items': target_items_per_day // 4},
                {'type': 'weak_areas', 'items': target_items_per_day // 4}
            ]
        else:
            plan['recommended_sessions'] = [
                {'type': 'mixed', 'items': min(target_items_per_day, stats.due_items)}
            ]
        
        # Suggest difficulty adjustment
        if stats.accuracy_rate > 0.9:
            plan['difficulty_adjustment'] = 'increase'
        elif stats.accuracy_rate < 0.6:
            plan['difficulty_adjustment'] = 'decrease'
        
        return plan

    def _load_user_progress(self, user_id):
        """Load user progress from database (placeholder)"""
        # This would typically query the database
        # For now, return empty dict
        return {}

    def _save_user_progress(self, user_id, progress):
        """Save user progress to database (placeholder)"""
        # This would typically save to database
        if self.db_manager:
            try:
                # Save to database
                logger.info(f"Saved progress for user {user_id}")
            except Exception as e:
                logger.error(f"Error saving progress: {e}")

    def export_progress_data(self, user_id):
        """Export user's learning data for analysis"""
        if not self.db_manager:
            return {}
        
        user_progress = self._load_user_progress(user_id)
        stats = self.get_learning_stats(user_progress)
        
        export_data = {
            'user_id': user_id,
            'export_date': datetime.now().isoformat(),
            'statistics': {
                'total_items': stats.total_items,
                'accuracy_rate': stats.accuracy_rate,
                'mastered_items': stats.mastered_items,
                'due_items': stats.due_items
            },
            'learning_progress': user_progress,
            'retention_analysis': {}
        }
        
        # Add retention analysis
        for item_id, progress in user_progress.items():
            retention = self.get_retention_prediction(progress)
            export_data['retention_analysis'][item_id] = retention
        
        return export_data

# Example usage functions
def create_study_session(user_id, session_size=10):
    """Create a study session for a user"""
    # This would typically load from database
    user_progress = {}  # Load user's progress from database
    
    sr = SpacedRepetition()
    due_items = sr.get_due_items(user_progress)
    
    # Return top items for study session
    return due_items[:session_size]

def process_user_response(user_id, item_id, grade):
    """Process user's response to a study item"""
    # This would typically interact with database
    sr = SpacedRepetition()
    
    # Load user progress for this item
    progress = {}  # Load from database
    
    # Update progress
    updated_progress = sr.update_progress(progress, grade)
    
    # Save back to database
    return updated_progress
