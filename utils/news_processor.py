import feedparser
import datetime
import time
import hashlib
from dateutil import parser as date_parser

def scan_feeds(rss_feeds, psychology_terms, existing_articles=None, max_articles=20):
    """
    Scan RSS feeds for new articles related to psychology terms
    
    Args:
        rss_feeds (pd.DataFrame): DataFrame containing RSS feed URLs and metadata
        psychology_terms (pd.DataFrame): DataFrame containing psychology terms
        existing_articles (list, optional): List of already processed articles to avoid duplicates
        max_articles (int, optional): Maximum number of articles to return, defaults to 20
        
    Returns:
        list: List of dictionaries containing article data, limited to the most recent max_articles
    """
    all_new_articles = []
    
    # Extract all terms as a list for easier comparison
    terms_list = psychology_terms['Term'].tolist()
    
    # Create a set of existing article IDs to avoid duplicates
    existing_ids = set()
    if existing_articles:
        existing_ids = {article.get('id', '') for article in existing_articles}
    
    # Scan each feed
    for _, feed in rss_feeds.iterrows():
        try:
            print(f"Scanning feed: {feed['name']} ({feed['url']})")
            parsed_feed = feedparser.parse(feed['url'])
            
            # Process each article in the feed
            for entry in parsed_feed.entries:
                # Create a unique ID for the article based on its URL
                article_id = hashlib.md5(entry.link.encode()).hexdigest()
                
                # Skip if this article is already processed
                if article_id in existing_ids:
                    continue
                
                # Extract article content
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                description = entry.get('description', '')
                content = title + " " + summary + " " + description
                
                # Check if the article contains any psychology-related terms
                # This is a basic keyword check - the OpenAI analysis will be more thorough
                is_psychology_related = False
                matched_terms = []
                
                # Basic keyword matching - this is just for initial filtering
                # The AI will do a more thorough analysis later
                for term in terms_list:
                    # Convert both to lowercase for case-insensitive matching
                    if term.lower() in content.lower():
                        is_psychology_related = True
                        matched_terms.append(term)
                        if len(matched_terms) >= 3:  # Found enough terms
                            break
                
                # If no direct term matches, we'll still include some articles for AI analysis
                # as the AI can identify psychological concepts even when terms aren't explicitly mentioned
                if not is_psychology_related and len(all_new_articles) < 15:
                    # Include some articles even without direct matches for deeper AI analysis
                    is_psychology_related = True
                
                if not is_psychology_related:
                    continue
                
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
                    'content_for_analysis': content,
                    'initial_matches': matched_terms
                }
                
                all_new_articles.append(article)
                print(f"Found potential psychology-related article: {title}")
        except Exception as e:
            print(f"Error processing feed {feed['name']}: {str(e)}")
    
    # Sort articles by date (newest first) before limiting
    # Convert any datetime objects to a timestamp for consistent comparison
    def get_sort_key(article):
        published = article.get('published_parsed')
        if published:
            # Handle various types of datetime objects that might come from feeds
            if isinstance(published, time.struct_time):
                return time.mktime(published)
            elif hasattr(published, 'timestamp'):
                return published.timestamp()
            else:
                # Default to current time if we can't determine
                return time.time()
        else:
            # If no date, treat as oldest
            return 0
    
    all_new_articles = sorted(all_new_articles, key=get_sort_key, reverse=True)
    
    # Limit to max_articles (default 20)
    limited_articles = all_new_articles[:max_articles]
    
    print(f"Found {len(all_new_articles)} new potential psychology-related articles")
    print(f"Limiting analysis to the {len(limited_articles)} most recent articles")
    
    return limited_articles

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
