import streamlit as st
import pandas as pd
import datetime
import schedule
import time
import threading
import os
from utils.news_processor import scan_feeds
from utils.openai_service import analyze_article, generate_summary
from utils.data_manager import load_psychology_terms, load_rss_feeds, save_analyzed_articles, load_analyzed_articles

# Set page configuration
st.set_page_config(
    page_title="PsychNews Connect",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App title and description
st.title("PsychNews Connect")
st.markdown("""
Connect AP Psychology terms to current news events with AI-powered educational summaries.
This tool helps students understand psychological concepts in real-world contexts.
""")

# Initialize session state
if 'analyzed_articles' not in st.session_state:
    st.session_state.analyzed_articles = load_analyzed_articles()
if 'last_scan_time' not in st.session_state:
    st.session_state.last_scan_time = None
if 'scan_in_progress' not in st.session_state:
    st.session_state.scan_in_progress = False
if 'api_key_set' not in st.session_state:
    st.session_state.api_key_set = False

# Initialize data
psychology_terms = load_psychology_terms()
rss_feeds = load_rss_feeds()

# Sidebar for controls
with st.sidebar:
    st.header("Settings")
    
    # The API key is now set automatically in the backend
    # Set API key set flag to true since we have it configured as an environment variable
    st.session_state.api_key_set = True
    
    # Display last scan time
    if st.session_state.last_scan_time:
        st.info(f"Last scan: {st.session_state.last_scan_time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.info("No scans performed yet")
    
    # On-demand scan button
    if st.button("Scan News Now", disabled=st.session_state.scan_in_progress):
        st.session_state.scan_in_progress = True
        with st.spinner("Scanning RSS feeds for psychology-related news..."):
            # Pass existing articles to avoid duplicates
            new_articles = scan_feeds(rss_feeds, psychology_terms, st.session_state.analyzed_articles)
            
            if new_articles:
                st.info(f"Found {len(new_articles)} potential articles. Analyzing with OpenAI...")
                analyzed_count = 0
                
                # Process articles with OpenAI
                for i, article in enumerate(new_articles):
                    status_msg = st.empty()
                    status_msg.write(f"Analyzing article {i+1} of {len(new_articles)}: {article['title']}")
                    
                    terms = analyze_article(article, psychology_terms)
                    if terms:
                        article['psychology_terms'] = terms
                        
                        # Generate educational summary if psychology terms were found
                        status_msg.write(f"Generating educational summary for article {i+1}")
                        article['summary'] = generate_summary(article, terms)
                        
                        # Add to our collection
                        st.session_state.analyzed_articles.append(article)
                        analyzed_count += 1
                
                # Save updated articles
                status_msg = st.empty()
                status_msg.write("Saving analyzed articles...")
                save_analyzed_articles(st.session_state.analyzed_articles)
                
                if analyzed_count > 0:
                    st.success(f"Successfully analyzed {analyzed_count} psychology-related articles!")
                else:
                    st.info("No articles with relevant psychological concepts were found")
            else:
                st.info("No new psychology-related articles found")
            
            st.session_state.last_scan_time = datetime.datetime.now()
        st.session_state.scan_in_progress = False
        st.rerun()
    
    # Filter options
    st.subheader("Filter Options")
    
    # Filter by psychology term
    term_filter = st.multiselect("Filter by Psychology Term", 
                                options=[term for term in psychology_terms['Term']],
                                help="Select specific psychology terms to focus on")
    
    # Show source feeds
    st.subheader("News Sources")
    st.dataframe(rss_feeds[['name', 'quality_rating']], hide_index=True)

# Main content area
tab1, tab2 = st.tabs(["Psychology News", "Term Reference"])

with tab1:
    # Filter articles based on sidebar selections
    filtered_articles = st.session_state.analyzed_articles
    
    # Apply term filter if selected
    if term_filter:
        filtered_articles = [
            article for article in filtered_articles 
            if any(term in article.get('psychology_terms', []) for term in term_filter)
        ]
    
    # Sort by date (newest first)
    filtered_articles = sorted(filtered_articles, key=lambda x: x.get('published_parsed', 0), reverse=True)
    
    if not filtered_articles:
        st.info("No articles found with the current filters. Try adjusting your filters or scanning for new articles.")
    
    # Display articles
    for i, article in enumerate(filtered_articles):
        with st.expander(f"{article['title']} ({article.get('source_name', 'Unknown source')})"):
            st.markdown(f"**Published:** {article.get('published', 'Unknown date')}")
            st.markdown(f"**Source:** {article.get('source_name', 'Unknown')}")
            st.markdown(f"**Link:** [{article['link']}]({article['link']})")
            
            # Display related psychology terms
            if 'psychology_terms' in article:
                st.markdown("**Related Psychology Concepts:**")
                st.write(", ".join(article['psychology_terms']))
            
            # Display the AI-generated summary
            if 'summary' in article:
                st.markdown("### Educational Summary")
                st.markdown(article['summary'])
            
            # Bottom border for visual separation
            st.markdown("---")

with tab2:
    # Display psychology terms reference
    st.header("AP Psychology Terms Reference")
    st.dataframe(psychology_terms, hide_index=True)

# Background scheduler
def scheduled_scan():
    if st.session_state.api_key_set and not st.session_state.scan_in_progress:
        # Pass existing articles to avoid duplicates
        new_articles = scan_feeds(rss_feeds, psychology_terms, st.session_state.analyzed_articles)
        
        if new_articles:
            analyzed_count = 0
            
            # Process articles with OpenAI
            for article in new_articles:
                terms = analyze_article(article, psychology_terms)
                if terms:
                    article['psychology_terms'] = terms
                    article['summary'] = generate_summary(article, terms)
                    st.session_state.analyzed_articles.append(article)
                    analyzed_count += 1
            
            # Save updated articles
            save_analyzed_articles(st.session_state.analyzed_articles)
            print(f"Scheduled scan: Added {analyzed_count} new psychology-related articles")
        
        st.session_state.last_scan_time = datetime.datetime.now()

def run_scheduler():
    schedule.every().day.at("00:00").do(scheduled_scan)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

# Start scheduler in a separate thread
if not st.session_state.get('scheduler_started', False):
    threading.Thread(target=run_scheduler, daemon=True).start()
    st.session_state.scheduler_started = True
