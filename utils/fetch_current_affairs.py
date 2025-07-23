# Utility script to fetch current affairs
import requests
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

class CurrentAffairsFetcher:
    def __init__(self):
        self.api_key = None  # Add your news API key here
        self.base_url = "https://newsapi.org/v2/top-headlines"
    
    def fetch_indian_news(self, days_back=1):
        """
        Fetch current affairs related to India from the last few days
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            params = {
                'country': 'in',
                'category': 'general',
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d'),
                'apiKey': self.api_key,
                'sortBy': 'publishedAt'
            }
            
            if not self.api_key:
                # Return sample data if no API key is configured
                return self._get_sample_current_affairs()
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return self._format_news_data(data['articles'])
            
        except Exception as e:
            logger.error(f"Error fetching current affairs: {e}")
            return self._get_sample_current_affairs()
    
    def _format_news_data(self, articles):
        """Format news articles for the bot"""
        formatted_news = []
        
        for article in articles[:10]:  # Limit to 10 articles
            formatted_article = {
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'url': article.get('url', ''),
                'published_at': article.get('publishedAt', ''),
                'source': article.get('source', {}).get('name', '')
            }
            formatted_news.append(formatted_article)
        
        return formatted_news
    
    def _get_sample_current_affairs(self):
        """Return sample current affairs data"""
        return [
            {
                'title': 'G20 Summit Updates',
                'description': 'Key developments from the latest G20 summit discussions.',
                'url': '#',
                'published_at': datetime.now().isoformat(),
                'source': 'Sample News'
            },
            {
                'title': 'Economic Policy Changes',
                'description': 'Recent changes in economic policies affecting various sectors.',
                'url': '#',
                'published_at': datetime.now().isoformat(),
                'source': 'Sample News'
            },
            {
                'title': 'Space Mission Success',
                'description': 'ISRO achieves another milestone in space exploration.',
                'url': '#',
                'published_at': datetime.now().isoformat(),
                'source': 'Sample News'
            }
        ]

def get_current_affairs():
    """Main function to get current affairs"""
    fetcher = CurrentAffairsFetcher()
    return fetcher.fetch_indian_news()

if __name__ == "__main__":
    current_affairs = get_current_affairs()
    print(json.dumps(current_affairs, indent=2))
