import pandas as pd
import os
import json
from datetime import datetime

# File paths
TERMS_FILE = "data/psychology_terms.csv"
RSS_FEEDS_FILE = "data/rss_feeds.csv"
ARTICLES_FILE = "data/analyzed_articles.json"

def load_psychology_terms():
    """
    Load psychology terms from CSV file or create default if not exists
    
    Returns:
        pd.DataFrame: DataFrame containing psychology terms and definitions
    """
    if os.path.exists(TERMS_FILE):
        return pd.read_csv(TERMS_FILE)
    else:
        # Create a default psychology terms CSV file for testing
        terms_data = {
            'Term': [
                'Classical Conditioning',
                'Operant Conditioning',
                'Cognitive Dissonance',
                'Confirmation Bias',
                'Social Facilitation',
                'Group Polarization',
                'Bystander Effect',
                'Fundamental Attribution Error',
                'Attachment Theory',
                'Maslow\'s Hierarchy of Needs'
            ],
            'Definition': [
                'Learning process that occurs through associations between environmental stimuli and naturally occurring stimuli.',
                'Learning process in which behavior is modified by its consequences, reinforced or punished.',
                'Mental discomfort that results from holding conflicting beliefs, values, or attitudes.',
                'Tendency to search for information that confirms one\'s preexisting beliefs.',
                'Tendency for people to perform better on simple tasks when in the presence of others.',
                'Phenomenon where group discussion strengthens the dominant position among group members.',
                'The decreased likelihood of a person intervening in an emergency when others are present.',
                'Tendency to overestimate the influence of personality and underestimate the influence of situations.',
                'Theory suggesting that children form attachment styles with caregivers that influence relationships throughout life.',
                'Theory in psychology proposing a hierarchy of human needs from basic physiological needs to self-actualization.'
            ]
        }
        df = pd.DataFrame(terms_data)
        os.makedirs(os.path.dirname(TERMS_FILE), exist_ok=True)
        df.to_csv(TERMS_FILE, index=False)
        return df

def load_rss_feeds():
    """
    Load RSS feeds from CSV file or create default if not exists
    
    Returns:
        pd.DataFrame: DataFrame containing RSS feeds and metadata
    """
    if os.path.exists(RSS_FEEDS_FILE):
        return pd.read_csv(RSS_FEEDS_FILE)
    else:
        # Create a default RSS feeds CSV file for testing
        feeds_data = {
            'name': [
                'NPR Health',
                'Science Daily Psychology',
                'Psychology Today',
                'BBC News - Health',
                'New York Times - Health'
            ],
            'url': [
                'https://feeds.npr.org/1001/rss.xml',
                'https://www.sciencedaily.com/rss/mind_brain/psychology.xml',
                'https://www.psychologytoday.com/rss.xml',
                'http://feeds.bbci.co.uk/news/health/rss.xml',
                'https://rss.nytimes.com/services/xml/rss/nyt/Health.xml'
            ],
            'quality_rating': [5, 5, 4, 5, 5]
        }
        df = pd.DataFrame(feeds_data)
        os.makedirs(os.path.dirname(RSS_FEEDS_FILE), exist_ok=True)
        df.to_csv(RSS_FEEDS_FILE, index=False)
        return df

def save_analyzed_articles(articles):
    """
    Save analyzed articles to JSON file
    
    Args:
        articles (list): List of article dictionaries
    """
    # Convert datetime objects to strings
    for article in articles:
        if 'published_parsed' in article and hasattr(article['published_parsed'], 'strftime'):
            article['published_parsed'] = article['published_parsed'].strftime('%Y-%m-%d %H:%M:%S')
    
    os.makedirs(os.path.dirname(ARTICLES_FILE), exist_ok=True)
    with open(ARTICLES_FILE, 'w') as f:
        json.dump(articles, f, indent=2)

def load_analyzed_articles():
    """
    Load analyzed articles from JSON file
    
    Returns:
        list: List of article dictionaries
    """
    if os.path.exists(ARTICLES_FILE):
        try:
            with open(ARTICLES_FILE, 'r') as f:
                articles = json.load(f)
            
            # Convert string dates back to datetime objects
            for article in articles:
                if 'published_parsed' in article and isinstance(article['published_parsed'], str):
                    try:
                        article['published_parsed'] = datetime.strptime(article['published_parsed'], '%Y-%m-%d %H:%M:%S')
                    except:
                        article['published_parsed'] = datetime.now()
                        
            return articles
        except:
            return []
    else:
        return []
