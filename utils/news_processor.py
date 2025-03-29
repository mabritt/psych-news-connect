import feedparser
import datetime
import time
import hashlib
from dateutil import parser as date_parser

def scan_feeds(rss_feeds, psychology_terms):
    """
    Scan RSS feeds for new articles related to psychology terms
    
    Args:
        rss_feeds (pd.DataFrame): DataFrame containing RSS feed URLs and metadata
        psychology_terms (pd.DataFrame): DataFrame containing psychology terms
    
    Returns:
        list: List of dictionaries containing article data
    """
    all_new_articles = []
    
    # Extract all terms as a list for easier comparison
    terms_list = psychology_terms['Term'].tolist()
    
    # Scan each feed
    for _, feed in rss_feeds.iterrows():
        try:
            parsed_feed = feedparser.parse(feed['url'])
            
            # Process each article in the feed
            for entry in parsed_feed.entries:
                # Create a unique ID for the article based on its URL
                article_id = hashlib.md5(entry.link.encode()).hexdigest()
                
                # Extract article content
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                description = entry.get('description', '')
                content = title + " " + summary + " " + description
                
                # Set published date
                published = entry.get('published', '')
                published_parsed = None
                if published:
                    try:
                        published_parsed = entry.get('published_parsed')
                        if not published_parsed:
                            published_parsed = date_parser.parse(published)
                    except:
                        published_parsed = datetime.datetime.now()
                else:
                    published = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    published_parsed = datetime.datetime.now()
                
                # Create article object
                article = {
                    'id': article_id,
                    'title': title,
                    'summary': summary,
                    'description': description,
                    'link': entry.link,
                    'published': published,
                    'published_parsed': published_parsed,
                    'source_name': feed['name'],
                    'source_quality': feed['quality_rating'],
                    'content_for_analysis': content
                }
                
                all_new_articles.append(article)
        except Exception as e:
            print(f"Error processing feed {feed['name']}: {str(e)}")
    
    return all_new_articles

def filter_articles_by_quality(articles, quality_threshold):
    """
    Filter articles based on source quality
    
    Args:
        articles (list): List of article dictionaries
        quality_threshold (int): Minimum quality threshold (1-5)
    
    Returns:
        list: Filtered list of articles
    """
    return [article for article in articles if article.get('source_quality', 0) >= quality_threshold]
