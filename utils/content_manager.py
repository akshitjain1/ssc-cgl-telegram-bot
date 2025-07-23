# Content Manager for SSC-CGL Bot
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os

logger = logging.getLogger(__name__)

class ContentManager:
    def __init__(self):
        self.content_dir = "content"
        self.vocab_file = os.path.join(self.content_dir, "vocab.json")
        self.idioms_file = os.path.join(self.content_dir, "idioms.json")
        self.gk_file = os.path.join(self.content_dir, "gk.json")
    
    def load_json_file(self, file_path: str) -> List[Dict]:
        """Load content from JSON file"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            else:
                logger.warning(f"File not found: {file_path}")
                return []
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return []
    
    def save_json_file(self, file_path: str, data: List[Dict]) -> bool:
        """Save content to JSON file"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving {file_path}: {e}")
            return False
    
# Content Manager for SSC-CGL Bot
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os

logger = logging.getLogger(__name__)

class ContentManager:
    def __init__(self):
        self.content_dir = "content"
        self.daily_content_dir = "content/daily"
        self.vocab_file = os.path.join(self.content_dir, "vocab.json")
        self.idioms_file = os.path.join(self.content_dir, "idioms.json")
        self.gk_file = os.path.join(self.content_dir, "gk.json")
        
        # Initialize daily content directory
        os.makedirs(self.daily_content_dir, exist_ok=True)
    
    def load_json_file(self, file_path: str) -> List[Dict]:
        """Load content from JSON file"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            else:
                logger.warning(f"File not found: {file_path}")
                return []
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return []
    
    def save_json_file(self, file_path: str, data: List[Dict]) -> bool:
        """Save content to JSON file"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving {file_path}: {e}")
            return False
    
    def get_daily_content(self, date: datetime = None) -> Optional[Dict]:
        """Get daily content from Gemini-generated files or fallback to static content"""
        if date is None:
            date = datetime.now()
        
        # Try to load Gemini-generated content first
        daily_content_file = os.path.join(
            self.daily_content_dir, 
            f"daily_{date.strftime('%Y-%m-%d')}.json"
        )
        
        if os.path.exists(daily_content_file):
            try:
                with open(daily_content_file, 'r', encoding='utf-8') as f:
                    daily_content = json.load(f)
                    logger.info(f"Loaded Gemini-generated content for {date.strftime('%Y-%m-%d')}")
                    return daily_content
            except Exception as e:
                logger.error(f"Error loading daily content: {e}")
        
        # Fallback to static content if daily content not available
        logger.info(f"Using fallback static content for {date.strftime('%Y-%m-%d')}")
        return None
    
    def get_daily_vocab(self, date: datetime = None, count: int = 10) -> List[Dict]:
        """Get vocabulary words for a specific date"""
        if date is None:
            date = datetime.now()
        
        # Try to get from daily generated content first
        daily_content = self.get_daily_content(date)
        if daily_content and 'vocab_data' in daily_content:
            vocab_data = daily_content['vocab_data'][:count]
            logger.info(f"Retrieved {len(vocab_data)} vocabulary words from daily content")
            return vocab_data
        
        # Fallback to static content
        return self._get_static_vocab(date, count)
    
    def get_daily_idioms(self, date: datetime = None, count: int = 5) -> List[Dict]:
        """Get idioms for a specific date"""
        if date is None:
            date = datetime.now()
        
        # Try to get from daily generated content first
        daily_content = self.get_daily_content(date)
        if daily_content and 'idioms_data' in daily_content:
            idioms_data = daily_content['idioms_data'][:count]
            logger.info(f"Retrieved {len(idioms_data)} idioms from daily content")
            return idioms_data
        
        # Fallback to static content
        return self._get_static_idioms(date, count)
    
    def get_daily_gk(self, date: datetime = None, count: int = 10) -> List[Dict]:
        """Get general knowledge facts for a specific date"""
        if date is None:
            date = datetime.now()
        
        # Try to get from daily generated content first
        daily_content = self.get_daily_content(date)
        if daily_content and 'gk_data' in daily_content:
            gk_data = daily_content['gk_data'][:count]
            logger.info(f"Retrieved {len(gk_data)} GK items from daily content")
            return gk_data
        
        # Fallback to static content
        return self._get_static_gk(date, count)
    
    def get_daily_current_affairs(self, date: datetime = None, count: int = 10) -> List[Dict]:
        """Get current affairs for a specific date"""
        if date is None:
            date = datetime.now()
        
        # Try to get from daily generated content first
        daily_content = self.get_daily_content(date)
        if daily_content and 'current_affairs_data' in daily_content:
            current_affairs_data = daily_content['current_affairs_data'][:count]
            logger.info(f"Retrieved {len(current_affairs_data)} current affairs from daily content")
            return current_affairs_data
        
        # Fallback content
        return self._get_fallback_current_affairs()
    
    def _get_static_vocab(self, date: datetime, count: int) -> List[Dict]:
        """Get vocabulary from static file with date-based rotation"""
        vocab_data = self.load_json_file(self.vocab_file)
        
        if not vocab_data:
            return self._get_fallback_vocab()
        
        # Use date to select different words each day
        day_of_year = date.timetuple().tm_yday
        start_index = (day_of_year * 3) % len(vocab_data)  # Rotate through content
        
        selected_words = []
        for i in range(count):
            word_index = (start_index + i) % len(vocab_data)
            selected_words.append(vocab_data[word_index])
        
        return selected_words
    
    def _get_static_idioms(self, date: datetime, count: int) -> List[Dict]:
        """Get idioms from static file with date-based rotation"""
        idioms_data = self.load_json_file(self.idioms_file)
        
        if not idioms_data:
            return self._get_fallback_idioms()
        
        # Use date to select different idioms each day
        day_of_year = date.timetuple().tm_yday
        start_index = (day_of_year * 2) % len(idioms_data)
        
        selected_idioms = []
        for i in range(count):
            idiom_index = (start_index + i) % len(idioms_data)
            selected_idioms.append(idioms_data[idiom_index])
        
        return selected_idioms
    
    def _get_static_gk(self, date: datetime, count: int) -> List[Dict]:
        """Get GK from static file with date-based rotation"""
        gk_data = self.load_json_file(self.gk_file)
        
        if not gk_data:
            return self._get_fallback_gk()
        
        # Use date to select different GK items each day
        day_of_year = date.timetuple().tm_yday
        start_index = (day_of_year * 4) % len(gk_data)
        
        selected_gk = []
        for i in range(count):
            gk_index = (start_index + i) % len(gk_data)
            selected_gk.append(gk_data[gk_index])
        
        return selected_gk
    
    def check_content_availability(self, date: datetime = None) -> Dict[str, bool]:
        """Check what types of content are available for a date"""
        if date is None:
            date = datetime.now()
        
        daily_content = self.get_daily_content(date)
        
        availability = {
            'daily_content_exists': daily_content is not None,
            'vocab_available': False,
            'idioms_available': False,
            'gk_available': False,
            'current_affairs_available': False
        }
        
        if daily_content:
            availability.update({
                'vocab_available': bool(daily_content.get('vocab_data')),
                'idioms_available': bool(daily_content.get('idioms_data')),
                'gk_available': bool(daily_content.get('gk_data')),
                'current_affairs_available': bool(daily_content.get('current_affairs_data'))
            })
        
        return availability
    
    def get_content_stats(self, date: datetime = None) -> Dict[str, int]:
        """Get statistics about available content"""
        if date is None:
            date = datetime.now()
        
        daily_content = self.get_daily_content(date)
        
        if daily_content and 'content_stats' in daily_content:
            return daily_content['content_stats']
        
        # Count static content
        return {
            'vocab_count': len(self.load_json_file(self.vocab_file)),
            'idioms_count': len(self.load_json_file(self.idioms_file)),
            'gk_count': len(self.load_json_file(self.gk_file)),
            'current_affairs_count': 0,
            'source': 'static'
        }
    
    def _get_fallback_vocab(self) -> List[Dict]:
        """Fallback vocabulary words if file not available"""
        return [
            {
                "id": 1,
                "word": "Eloquent",
                "meaning": "fluent or persuasive in speaking or writing",
                "example": "The eloquent speaker captivated the audience.",
                "synonym": "articulate",
                "difficulty": "medium"
            },
            {
                "id": 2,
                "word": "Pragmatic",
                "meaning": "dealing with things sensibly and realistically",
                "example": "She took a pragmatic approach to solving the problem.",
                "synonym": "practical",
                "difficulty": "medium"
            },
            {
                "id": 3,
                "word": "Verbose",
                "meaning": "using or expressed in more words than are needed",
                "example": "His verbose explanation confused rather than clarified.",
                "synonym": "wordy",
                "difficulty": "medium"
            },
            {
                "id": 4,
                "word": "Candid",
                "meaning": "truthful and straightforward; frank",
                "example": "I appreciate your candid feedback on my work.",
                "synonym": "honest",
                "difficulty": "easy"
            },
            {
                "id": 5,
                "word": "Resilient",
                "meaning": "able to withstand or recover quickly from difficult conditions",
                "example": "The resilient community rebuilt after the disaster.",
                "synonym": "tough",
                "difficulty": "medium"
            }
        ]
    
    def _get_fallback_idioms(self) -> List[Dict]:
        """Fallback idioms if file not available"""
        return [
            {
                "id": 1,
                "idiom": "Hit the nail on the head",
                "meaning": "to describe exactly what is causing a situation or problem",
                "example": "You hit the nail on the head when you said the project lacks clear goals.",
                "category": "accuracy"
            },
            {
                "id": 2,
                "idiom": "The ball is in your court",
                "meaning": "it is up to you to make the next decision or step",
                "example": "I've given you all the information; now the ball is in your court.",
                "category": "responsibility"
            },
            {
                "id": 3,
                "idiom": "Break a leg",
                "meaning": "good luck (especially in a performance)",
                "example": "Break a leg in your presentation tomorrow!",
                "category": "encouragement"
            },
            {
                "id": 4,
                "idiom": "Piece of cake",
                "meaning": "something very easy to do",
                "example": "The math test was a piece of cake for her.",
                "category": "difficulty"
            },
            {
                "id": 5,
                "idiom": "Spill the beans",
                "meaning": "to reveal secret information",
                "example": "Who spilled the beans about the surprise party?",
                "category": "secrets"
            }
        ]
    
    def _get_fallback_gk(self) -> List[Dict]:
        """Fallback general knowledge if file not available"""
        return [
            {
                "id": 1,
                "question": "What is the capital of India?",
                "answer": "New Delhi",
                "category": "Geography",
                "difficulty": "easy"
            },
            {
                "id": 2,
                "question": "Who is known as the Father of the Nation in India?",
                "answer": "Mahatma Gandhi",
                "category": "History",
                "difficulty": "easy"
            },
            {
                "id": 3,
                "question": "Which is the largest planet in our solar system?",
                "answer": "Jupiter",
                "category": "Science",
                "difficulty": "easy"
            },
            {
                "id": 4,
                "question": "What is the chemical symbol for gold?",
                "answer": "Au",
                "category": "Science",
                "difficulty": "medium"
            },
            {
                "id": 5,
                "question": "In which year did India gain independence?",
                "answer": "1947",
                "category": "History",
                "difficulty": "easy"
            }
        ]
    
    def _get_fallback_current_affairs(self) -> List[Dict]:
        """Fallback current affairs if API fails"""
        return [
            {
                "id": 1,
                "title": "Government Policy Updates",
                "description": "Recent developments in government policies affecting various sectors.",
                "source": "Government News"
            },
            {
                "id": 2,
                "title": "Economic Indicators",
                "description": "Latest economic data and market trends in India.",
                "source": "Economic Times"
            },
            {
                "id": 3,
                "title": "International Relations",
                "description": "Recent diplomatic developments and international agreements.",
                "source": "Foreign Affairs"
            },
            {
                "id": 4,
                "title": "Technology Advancements",
                "description": "Latest developments in technology and innovation.",
                "source": "Tech News"
            },
            {
                "id": 5,
                "title": "Educational Reforms",
                "description": "Recent changes in educational policies and systems.",
                "source": "Education Ministry"
            }
        ]
    
    def search_content(self, query: str, content_type: str = "all") -> List[Dict]:
        """Search for content based on query"""
        results = []
        query_lower = query.lower()
        
        if content_type in ["all", "vocab"]:
            vocab_data = self.load_json_file(self.vocab_file)
            for item in vocab_data:
                if (query_lower in item.get('word', '').lower() or 
                    query_lower in item.get('meaning', '').lower()):
                    item['content_type'] = 'vocab'
                    results.append(item)
        
        if content_type in ["all", "idiom"]:
            idioms_data = self.load_json_file(self.idioms_file)
            for item in idioms_data:
                if (query_lower in item.get('idiom', '').lower() or 
                    query_lower in item.get('meaning', '').lower()):
                    item['content_type'] = 'idiom'
                    results.append(item)
        
        if content_type in ["all", "gk"]:
            gk_data = self.load_json_file(self.gk_file)
            for item in gk_data:
                if (query_lower in item.get('question', '').lower() or 
                    query_lower in item.get('answer', '').lower() or
                    query_lower in item.get('category', '').lower()):
                    item['content_type'] = 'gk'
                    results.append(item)
        
        return results
    
    def get_content_by_category(self, category: str, content_type: str) -> List[Dict]:
        """Get content filtered by category"""
        if content_type == "vocab":
            data = self.load_json_file(self.vocab_file)
            return [item for item in data if item.get('difficulty') == category]
        
        elif content_type == "idiom":
            data = self.load_json_file(self.idioms_file)
            return [item for item in data if item.get('category') == category]
        
        elif content_type == "gk":
            data = self.load_json_file(self.gk_file)
            return [item for item in data if item.get('category', '').lower() == category.lower()]
        
        return []
    
    def add_content(self, content_type: str, content_data: Dict) -> bool:
        """Add new content to the respective file"""
        try:
            if content_type == "vocab":
                file_path = self.vocab_file
            elif content_type == "idiom":
                file_path = self.idioms_file
            elif content_type == "gk":
                file_path = self.gk_file
            else:
                logger.error(f"Invalid content type: {content_type}")
                return False
            
            # Load existing data
            existing_data = self.load_json_file(file_path)
            
            # Add new ID if not present
            if 'id' not in content_data:
                max_id = max([item.get('id', 0) for item in existing_data], default=0)
                content_data['id'] = max_id + 1
            
            # Add the new content
            existing_data.append(content_data)
            
            # Save back to file
            return self.save_json_file(file_path, existing_data)
            
        except Exception as e:
            logger.error(f"Error adding content: {e}")
            return False
    
    def get_random_quiz_questions(self, count: int = 10, content_types: List[str] = None) -> List[Dict]:
        """Get random questions for quiz from all content types"""
        if content_types is None:
            content_types = ["vocab", "idiom", "gk"]
        
        quiz_questions = []
        
        for content_type in content_types:
            if content_type == "vocab":
                vocab_data = self.load_json_file(self.vocab_file)
                for item in vocab_data[:count//len(content_types)]:
                    quiz_questions.append({
                        'type': 'vocab',
                        'question': f"What does '{item['word']}' mean?",
                        'correct_answer': item['meaning'],
                        'content_id': item['id']
                    })
            
            elif content_type == "idiom":
                idioms_data = self.load_json_file(self.idioms_file)
                for item in idioms_data[:count//len(content_types)]:
                    quiz_questions.append({
                        'type': 'idiom',
                        'question': f"What does '{item['idiom']}' mean?",
                        'correct_answer': item['meaning'],
                        'content_id': item['id']
                    })
            
            elif content_type == "gk":
                gk_data = self.load_json_file(self.gk_file)
                for item in gk_data[:count//len(content_types)]:
                    quiz_questions.append({
                        'type': 'gk',
                        'question': item['question'],
                        'correct_answer': item['answer'],
                        'content_id': item['id']
                    })
        
        return quiz_questions[:count]
    
    def _get_fallback_vocab(self) -> List[Dict]:
        """Fallback vocabulary words if file not available"""
        return [
            {
                "id": 1,
                "word": "Eloquent",
                "meaning": "fluent or persuasive in speaking or writing",
                "example": "The eloquent speaker captivated the audience.",
                "synonym": "articulate",
                "difficulty": "medium"
            },
            {
                "id": 2,
                "word": "Pragmatic",
                "meaning": "dealing with things sensibly and realistically",
                "example": "She took a pragmatic approach to solving the problem.",
                "synonym": "practical",
                "difficulty": "medium"
            },
            {
                "id": 3,
                "word": "Verbose",
                "meaning": "using or expressed in more words than are needed",
                "example": "His verbose explanation confused rather than clarified.",
                "synonym": "wordy",
                "difficulty": "medium"
            },
            {
                "id": 4,
                "word": "Candid",
                "meaning": "truthful and straightforward; frank",
                "example": "I appreciate your candid feedback on my work.",
                "synonym": "honest",
                "difficulty": "easy"
            },
            {
                "id": 5,
                "word": "Resilient",
                "meaning": "able to withstand or recover quickly from difficult conditions",
                "example": "The resilient community rebuilt after the disaster.",
                "synonym": "tough",
                "difficulty": "medium"
            }
        ]
    
    def _get_fallback_idioms(self) -> List[Dict]:
        """Fallback idioms if file not available"""
        return [
            {
                "id": 1,
                "idiom": "Hit the nail on the head",
                "meaning": "to describe exactly what is causing a situation or problem",
                "example": "You hit the nail on the head when you said the project lacks clear goals.",
                "category": "accuracy"
            },
            {
                "id": 2,
                "idiom": "The ball is in your court",
                "meaning": "it is up to you to make the next decision or step",
                "example": "I've given you all the information; now the ball is in your court.",
                "category": "responsibility"
            },
            {
                "id": 3,
                "idiom": "Break a leg",
                "meaning": "good luck (especially in a performance)",
                "example": "Break a leg in your presentation tomorrow!",
                "category": "encouragement"
            },
            {
                "id": 4,
                "idiom": "Piece of cake",
                "meaning": "something very easy to do",
                "example": "The math test was a piece of cake for her.",
                "category": "difficulty"
            },
            {
                "id": 5,
                "idiom": "Spill the beans",
                "meaning": "to reveal secret information",
                "example": "Who spilled the beans about the surprise party?",
                "category": "secrets"
            }
        ]
    
    def _get_fallback_gk(self) -> List[Dict]:
        """Fallback general knowledge if file not available"""
        return [
            {
                "id": 1,
                "question": "What is the capital of India?",
                "answer": "New Delhi",
                "category": "Geography",
                "difficulty": "easy"
            },
            {
                "id": 2,
                "question": "Who is known as the Father of the Nation in India?",
                "answer": "Mahatma Gandhi",
                "category": "History",
                "difficulty": "easy"
            },
            {
                "id": 3,
                "question": "Which is the largest planet in our solar system?",
                "answer": "Jupiter",
                "category": "Science",
                "difficulty": "easy"
            },
            {
                "id": 4,
                "question": "What is the chemical symbol for gold?",
                "answer": "Au",
                "category": "Science",
                "difficulty": "medium"
            },
            {
                "id": 5,
                "question": "In which year did India gain independence?",
                "answer": "1947",
                "category": "History",
                "difficulty": "easy"
            }
        ]
    
    def search_content(self, query: str, content_type: str = "all") -> List[Dict]:
        """Search for content based on query"""
        results = []
        query_lower = query.lower()
        
        if content_type in ["all", "vocab"]:
            vocab_data = self.load_json_file(self.vocab_file)
            for item in vocab_data:
                if (query_lower in item.get('word', '').lower() or 
                    query_lower in item.get('meaning', '').lower()):
                    item['content_type'] = 'vocab'
                    results.append(item)
        
        if content_type in ["all", "idiom"]:
            idioms_data = self.load_json_file(self.idioms_file)
            for item in idioms_data:
                if (query_lower in item.get('idiom', '').lower() or 
                    query_lower in item.get('meaning', '').lower()):
                    item['content_type'] = 'idiom'
                    results.append(item)
        
        if content_type in ["all", "gk"]:
            gk_data = self.load_json_file(self.gk_file)
            for item in gk_data:
                if (query_lower in item.get('question', '').lower() or 
                    query_lower in item.get('answer', '').lower() or
                    query_lower in item.get('category', '').lower()):
                    item['content_type'] = 'gk'
                    results.append(item)
        
        return results
    
    def get_content_by_category(self, category: str, content_type: str) -> List[Dict]:
        """Get content filtered by category"""
        if content_type == "vocab":
            data = self.load_json_file(self.vocab_file)
            return [item for item in data if item.get('difficulty') == category]
        
        elif content_type == "idiom":
            data = self.load_json_file(self.idioms_file)
            return [item for item in data if item.get('category') == category]
        
        elif content_type == "gk":
            data = self.load_json_file(self.gk_file)
            return [item for item in data if item.get('category', '').lower() == category.lower()]
        
        return []
    
    def add_content(self, content_type: str, content_data: Dict) -> bool:
        """Add new content to the respective file"""
        try:
            if content_type == "vocab":
                file_path = self.vocab_file
            elif content_type == "idiom":
                file_path = self.idioms_file
            elif content_type == "gk":
                file_path = self.gk_file
            else:
                logger.error(f"Invalid content type: {content_type}")
                return False
            
            # Load existing data
            existing_data = self.load_json_file(file_path)
            
            # Add new ID if not present
            if 'id' not in content_data:
                max_id = max([item.get('id', 0) for item in existing_data], default=0)
                content_data['id'] = max_id + 1
            
            # Add the new content
            existing_data.append(content_data)
            
            # Save back to file
            return self.save_json_file(file_path, existing_data)
            
        except Exception as e:
            logger.error(f"Error adding content: {e}")
            return False
    
    def get_random_quiz_questions(self, count: int = 10, content_types: List[str] = None) -> List[Dict]:
        """Get random questions for quiz from all content types"""
        if content_types is None:
            content_types = ["vocab", "idiom", "gk"]
        
        quiz_questions = []
        
        for content_type in content_types:
            if content_type == "vocab":
                vocab_data = self.load_json_file(self.vocab_file)
                for item in vocab_data[:count//len(content_types)]:
                    quiz_questions.append({
                        'type': 'vocab',
                        'question': f"What does '{item['word']}' mean?",
                        'correct_answer': item['meaning'],
                        'content_id': item['id']
                    })
            
            elif content_type == "idiom":
                idioms_data = self.load_json_file(self.idioms_file)
                for item in idioms_data[:count//len(content_types)]:
                    quiz_questions.append({
                        'type': 'idiom',
                        'question': f"What does '{item['idiom']}' mean?",
                        'correct_answer': item['meaning'],
                        'content_id': item['id']
                    })
            
            elif content_type == "gk":
                gk_data = self.load_json_file(self.gk_file)
                for item in gk_data[:count//len(content_types)]:
                    quiz_questions.append({
                        'type': 'gk',
                        'question': item['question'],
                        'correct_answer': item['answer'],
                        'content_id': item['id']
                    })
        
        return quiz_questions[:count]
