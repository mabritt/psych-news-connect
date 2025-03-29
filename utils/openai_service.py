import os
import json
from openai import OpenAI

# The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# Do not change this unless explicitly requested by the user
DEFAULT_MODEL = "gpt-4o"

def get_openai_client():
    """
    Get OpenAI client with API key from environment
    
    Returns:
        OpenAI: OpenAI client instance
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found. Please set your API key in the settings.")
    
    return OpenAI(api_key=api_key)

def analyze_article(article, psychology_terms):
    """
    Analyze article content to determine relevant psychology terms
    
    Args:
        article (dict): Article data
        psychology_terms (pd.DataFrame): DataFrame containing psychology terms
    
    Returns:
        list: List of relevant psychology terms
    """
    try:
        client = get_openai_client()
        
        # Extract terms for prompt
        term_list = psychology_terms['Term'].tolist()
        term_definitions = {}
        for _, row in psychology_terms.iterrows():
            term_definitions[row['Term']] = row['Definition']
        
        # Prepare the content for analysis
        content = article.get('content_for_analysis', '')
        if not content or len(content) < 10:
            return []
        
        # Limit content length to avoid token limits
        if len(content) > 8000:
            content = content[:8000]
        
        # Create the prompt
        prompt = f"""
        You are an educational assistant for AP Psychology students. Analyze the following news article 
        and identify which of the AP Psychology terms provided are relevant to the content. 
        For terms to be considered relevant, they should have a clear connection to the underlying 
        psychological principles in the article, even if the terms themselves aren't explicitly mentioned.

        News Article:
        {content}

        AP Psychology Terms (with definitions):
        {json.dumps(term_definitions, indent=2)}
        
        Return only the relevant terms in a JSON list format like this: ["Term1", "Term2"]
        If no terms are relevant, return an empty list [].
        """
        
        # Query OpenAI
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        # Extract and validate the result
        result = json.loads(response.choices[0].message.content)
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "terms" in result:
            return result["terms"]
        else:
            # Try to extract a list from the response if it's not properly formatted
            content = response.choices[0].message.content
            try:
                # Try to find a list in the response
                start_idx = content.find("[")
                end_idx = content.rfind("]")
                if start_idx >= 0 and end_idx > start_idx:
                    terms_json = content[start_idx:end_idx+1]
                    return json.loads(terms_json)
            except:
                pass
            
            # Fallback: return empty list
            return []
            
    except Exception as e:
        print(f"Error analyzing article: {str(e)}")
        return []

def generate_summary(article, terms):
    """
    Generate an educational summary linking the news article to psychology terms
    
    Args:
        article (dict): Article data
        terms (list): Relevant psychology terms
    
    Returns:
        str: Educational summary
    """
    try:
        client = get_openai_client()
        
        # Prepare the content for summarization
        content = article.get('content_for_analysis', '')
        if not content or len(content) < 10:
            return "Could not generate summary due to insufficient content."
        
        # Limit content length to avoid token limits
        if len(content) > 8000:
            content = content[:8000]
        
        # Format terms for the prompt
        terms_str = ", ".join(terms)
        
        # Create the prompt
        prompt = f"""
        You are an educational assistant for AP Psychology students. Create an educational summary 
        that explains how the following news article relates to these AP Psychology terms: {terms_str}.
        
        News Article:
        {content}
        
        Write a summary that:
        1. Summarizes the news article in 1-2 paragraphs
        2. Explains how each psychology term relates to the events or concepts in the article
        3. Provides educational insights that would help a student understand the real-world application of these concepts
        4. Is written in clear, engaging language appropriate for high school or college students
        
        The summary should be informative, accurate, and focused on helping students connect psychological concepts with current events.
        """
        
        # Query OpenAI
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        # Return the summary
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        return "An error occurred while generating the summary. Please try again later."
