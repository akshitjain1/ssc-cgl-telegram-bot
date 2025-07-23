# Daily Content Generator using Gemini API
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import google.generativeai as genai
import requests

logger = logging.getLogger(__name__)

# Load environment variables manually
def load_env_variables():
    """Load environment variables from .env file"""
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Load environment at module level
load_env_variables()

logger = logging.getLogger(__name__)

class GeminiContentGenerator:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.news_api_key = os.getenv('NEWS_API_KEY')
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables!")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Content generation settings
        self.vocab_count = int(os.getenv('DAILY_VOCAB_COUNT', 10))
        self.idioms_count = int(os.getenv('DAILY_IDIOMS_COUNT', 5))
        self.gk_count = int(os.getenv('DAILY_GK_COUNT', 10))
        
        logger.info("Gemini Content Generator initialized successfully")
    
    def generate_daily_vocabulary(self, date: datetime = None) -> List[Dict]:
        """Generate daily vocabulary words using Gemini API"""
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y-%m-%d")
        
        prompt = f"""
Generate exactly {self.vocab_count} vocabulary words for SSC-CGL exam preparation for date {date_str}.

Requirements:
- Mix of difficulty levels: 40% easy, 40% medium, 20% hard
- Words commonly used in SSC-CGL exams
- Include professional, academic, and formal words
- Each word should have: word, meaning, example sentence, synonym, difficulty level
- Avoid repeating words from previous days
- Focus on words that improve English comprehension

Return ONLY a valid JSON array in this exact format:
[
  {{
    "id": 1,
    "word": "Example",
    "meaning": "clear definition",
    "example": "example sentence using the word naturally",
    "synonym": "similar word",
    "difficulty": "easy|medium|hard"
  }}
]

Generate {self.vocab_count} unique vocabulary words now:
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Parse the JSON response
            content = response.text.strip()
            
            # Clean the response to extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
            
            vocab_data = json.loads(content)
            
            # Validate and clean the data
            validated_vocab = []
            for i, item in enumerate(vocab_data[:self.vocab_count], 1):
                validated_item = {
                    "id": i,
                    "word": item.get("word", "").strip(),
                    "meaning": item.get("meaning", "").strip(),
                    "example": item.get("example", "").strip(),
                    "synonym": item.get("synonym", "").strip(),
                    "difficulty": item.get("difficulty", "medium").lower(),
                    "generated_date": date_str,
                    "source": "gemini"
                }
                
                # Ensure all required fields are present
                if all([validated_item["word"], validated_item["meaning"], validated_item["example"]]):
                    validated_vocab.append(validated_item)
            
            logger.info(f"Generated {len(validated_vocab)} vocabulary words for {date_str}")
            return validated_vocab
            
        except Exception as e:
            logger.error(f"Error generating vocabulary: {e}")
            return self._get_fallback_vocabulary(date)
    
    def generate_daily_idioms(self, date: datetime = None) -> List[Dict]:
        """Generate daily idioms using Gemini API"""
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y-%m-%d")
        
        prompt = f"""
Generate exactly {self.idioms_count} English idioms and phrases for SSC-CGL exam preparation for date {date_str}.

Requirements:
- Common idioms used in competitive exams
- Include business, daily life, and formal idioms
- Each idiom should have: idiom, meaning, example sentence, category
- Categories: common, business, emotions, time, difficulty, success, communication
- Practical idioms that students can use in writing and speaking

Return ONLY a valid JSON array in this exact format:
[
  {{
    "id": 1,
    "idiom": "Example idiom",
    "meaning": "clear explanation of what it means",
    "example": "natural sentence using the idiom",
    "category": "category name"
  }}
]

Generate {self.idioms_count} useful idioms now:
        """
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            
            # Clean the response to extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
            
            idioms_data = json.loads(content)
            
            # Validate and clean the data
            validated_idioms = []
            for i, item in enumerate(idioms_data[:self.idioms_count], 1):
                validated_item = {
                    "id": i,
                    "idiom": item.get("idiom", "").strip(),
                    "meaning": item.get("meaning", "").strip(),
                    "example": item.get("example", "").strip(),
                    "category": item.get("category", "common").lower(),
                    "generated_date": date_str,
                    "source": "gemini"
                }
                
                if all([validated_item["idiom"], validated_item["meaning"], validated_item["example"]]):
                    validated_idioms.append(validated_item)
            
            logger.info(f"Generated {len(validated_idioms)} idioms for {date_str}")
            return validated_idioms
            
        except Exception as e:
            logger.error(f"Error generating idioms: {e}")
            return self._get_fallback_idioms(date)
    
    def generate_daily_gk(self, date: datetime = None) -> List[Dict]:
        """Generate daily general knowledge facts using Gemini API"""
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y-%m-%d")
        
        # Get current affairs context
        current_affairs_context = self._get_current_affairs_context()
        
        prompt = f"""
Generate exactly {self.gk_count} General Knowledge questions for SSC-CGL exam preparation for date {date_str}.

Requirements:
- Mix of static GK and recent current affairs
- Categories: History, Geography, Science, Politics, Economics, Sports, Awards, Books & Authors
- Include recent events from 2024-2025
- Questions should be exam-level difficulty
- Each item should have: question, answer, category, difficulty

Current Affairs Context for today:
{current_affairs_context}

Return ONLY a valid JSON array in this exact format:
[
  {{
    "id": 1,
    "question": "Clear, specific question",
    "answer": "Accurate, concise answer",
    "category": "History|Geography|Science|Politics|Economics|Sports|Awards|Books",
    "difficulty": "easy|medium|hard"
  }}
]

Generate {self.gk_count} relevant GK questions now:
        """
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            
            # Clean the response to extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
            
            gk_data = json.loads(content)
            
            # Validate and clean the data
            validated_gk = []
            for i, item in enumerate(gk_data[:self.gk_count], 1):
                validated_item = {
                    "id": i,
                    "question": item.get("question", "").strip(),
                    "answer": item.get("answer", "").strip(),
                    "category": item.get("category", "General").strip(),
                    "difficulty": item.get("difficulty", "medium").lower(),
                    "generated_date": date_str,
                    "source": "gemini"
                }
                
                if all([validated_item["question"], validated_item["answer"]]):
                    validated_gk.append(validated_item)
            
            logger.info(f"Generated {len(validated_gk)} GK questions for {date_str}")
            return validated_gk
            
        except Exception as e:
            logger.error(f"Error generating GK: {e}")
            return self._get_fallback_gk(date)
    
    def _get_current_affairs_context(self) -> str:
        """Get recent current affairs for GK context"""
        try:
            if not self.news_api_key:
                return "Recent developments in India and world affairs"
            
            # Get recent India news
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                'country': 'in',
                'category': 'general',
                'pageSize': 5,
                'apiKey': self.news_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            news_data = response.json()
            
            context = "Recent News Headlines:\n"
            for article in news_data.get('articles', [])[:3]:
                title = article.get('title', '')
                if title:
                    context += f"- {title}\n"
            
            return context
            
        except Exception as e:
            logger.error(f"Error fetching current affairs context: {e}")
            return "Recent developments in Indian government, economy, and international relations"
    
    def generate_all_daily_content(self, date: datetime = None) -> Dict:
        """Generate all types of daily content"""
        if date is None:
            date = datetime.now()
        
        logger.info(f"Generating all daily content for {date.strftime('%Y-%m-%d')}")
        
        # Generate all content types
        vocab_data = self.generate_daily_vocabulary(date)
        idioms_data = self.generate_daily_idioms(date)
        gk_data = self.generate_daily_gk(date)
        current_affairs_data = self._get_current_affairs_data()
        
        daily_content = {
            "date": date.strftime('%Y-%m-%d'),
            "generated_timestamp": datetime.now().isoformat(),
            "vocab_data": vocab_data,
            "idioms_data": idioms_data,
            "gk_data": gk_data,
            "current_affairs_data": current_affairs_data,
            "content_stats": {
                "vocab_count": len(vocab_data),
                "idioms_count": len(idioms_data),
                "gk_count": len(gk_data),
                "current_affairs_count": len(current_affairs_data)
            }
        }
        
        # Save to file
        self._save_daily_content(daily_content, date)
        
        logger.info(f"Successfully generated daily content: {daily_content['content_stats']}")
        return daily_content
    
    def _get_current_affairs_data(self) -> List[Dict]:
        """Get current affairs data from news API"""
        try:
            if not self.news_api_key:
                return self._get_fallback_current_affairs()
            
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                'country': 'in',
                'pageSize': 10,
                'apiKey': self.news_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            news_data = response.json()
            
            current_affairs = []
            for i, article in enumerate(news_data.get('articles', [])[:10], 1):
                if article.get('title') and article.get('description'):
                    current_affairs.append({
                        "id": i,
                        "title": article['title'],
                        "description": article['description'][:200] + "..." if len(article['description']) > 200 else article['description'],
                        "url": article.get('url', ''),
                        "published_at": article.get('publishedAt', ''),
                        "source": article.get('source', {}).get('name', 'News Source')
                    })
            
            return current_affairs
            
        except Exception as e:
            logger.error(f"Error fetching current affairs: {e}")
            return self._get_fallback_current_affairs()
    
    def _save_daily_content(self, content: Dict, date: datetime):
        """Save daily content to file"""
        try:
            os.makedirs("content/daily", exist_ok=True)
            
            filename = f"content/daily/daily_{date.strftime('%Y-%m-%d')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved daily content to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving daily content: {e}")
    
    def load_daily_content(self, date: datetime = None) -> Optional[Dict]:
        """Load daily content from file"""
        if date is None:
            date = datetime.now()
        
        try:
            filename = f"content/daily/daily_{date.strftime('%Y-%m-%d')}.json"
            
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            logger.error(f"Error loading daily content: {e}")
            return None
    
    def _get_fallback_vocabulary(self, date: datetime) -> List[Dict]:
        """Fallback vocabulary if Gemini fails"""
        return [
            {"id": 1, "word": "Articulate", "meaning": "express thoughts clearly", "example": "She is very articulate in her speech.", "synonym": "eloquent", "difficulty": "medium"},
            {"id": 2, "word": "Coherent", "meaning": "logical and consistent", "example": "His argument was coherent and convincing.", "synonym": "logical", "difficulty": "medium"},
            {"id": 3, "word": "Diligent", "meaning": "showing care and effort", "example": "She is a diligent student who studies regularly.", "synonym": "hardworking", "difficulty": "easy"},
            {"id": 4, "word": "Eloquent", "meaning": "fluent and persuasive", "example": "The eloquent speaker moved the audience.", "synonym": "articulate", "difficulty": "medium"},
            {"id": 5, "word": "Feasible", "meaning": "possible to do easily", "example": "The project seems feasible within our budget.", "synonym": "viable", "difficulty": "medium"}
        ]
    
    def _get_fallback_idioms(self, date: datetime) -> List[Dict]:
        """Fallback idioms if Gemini fails"""
        return [
            {"id": 1, "idiom": "Time flies", "meaning": "time passes quickly", "example": "Time flies when you're having fun.", "category": "time"},
            {"id": 2, "idiom": "Break the ice", "meaning": "start a conversation", "example": "He told a joke to break the ice.", "category": "communication"},
            {"id": 3, "idiom": "Hit the books", "meaning": "study hard", "example": "I need to hit the books for my exam.", "category": "education"}
        ]
    
    def _get_fallback_gk(self, date: datetime) -> List[Dict]:
        """Fallback GK if Gemini fails"""
        return [
            {"id": 1, "question": "What is the capital of India?", "answer": "New Delhi", "category": "Geography", "difficulty": "easy"},
            {"id": 2, "question": "Who wrote the Indian National Anthem?", "answer": "Rabindranath Tagore", "category": "History", "difficulty": "medium"},
            {"id": 3, "question": "Which planet is known as the Red Planet?", "answer": "Mars", "category": "Science", "difficulty": "easy"}
        ]
    
    def _get_fallback_current_affairs(self) -> List[Dict]:
        """Fallback current affairs if API fails"""
        return [
            {"id": 1, "title": "Government Policy Updates", "description": "Recent developments in government policies affecting various sectors.", "source": "Government News"},
            {"id": 2, "title": "Economic Indicators", "description": "Latest economic data and market trends in India.", "source": "Economic Times"},
            {"id": 3, "title": "International Relations", "description": "Recent diplomatic developments and international agreements.", "source": "Foreign Affairs"}
        ]

# Main function for testing
def main():
    """Test the content generator"""
    try:
        generator = GeminiContentGenerator()
        
        print("🚀 Testing Gemini Content Generator...")
        
        # Generate today's content
        daily_content = generator.generate_all_daily_content()
        
        print(f"✅ Generated content for {daily_content['date']}")
        print(f"📚 Vocabulary: {daily_content['content_stats']['vocab_count']} words")
        print(f"🗣️ Idioms: {daily_content['content_stats']['idioms_count']} phrases")  
        print(f"🧠 GK: {daily_content['content_stats']['gk_count']} questions")
        print(f"📰 Current Affairs: {daily_content['content_stats']['current_affairs_count']} items")
        
        # Show sample content
        if daily_content['vocab_data']:
            print(f"\n📖 Sample Vocabulary: {daily_content['vocab_data'][0]['word']} - {daily_content['vocab_data'][0]['meaning']}")
        
        if daily_content['idioms_data']:
            print(f"💬 Sample Idiom: {daily_content['idioms_data'][0]['idiom']} - {daily_content['idioms_data'][0]['meaning']}")
        
        if daily_content['gk_data']:
            print(f"❓ Sample GK: {daily_content['gk_data'][0]['question']}")
        
        print("\n🎉 Content generation test completed successfully!")
        
    except Exception as e:
        print(f"❌ Content generation test failed: {e}")

if __name__ == "__main__":
    main()
