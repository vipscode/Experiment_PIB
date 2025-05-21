"""
Article summarization module for PIB news articles
This module fetches article content and generates two-line summaries
"""

import requests
from bs4 import BeautifulSoup
import re
from transformers import pipeline
from newspaper import Article
import nltk
import time
import random

# Download necessary nltk data (only needs to be done once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Initialize the summarization pipeline with a smaller model for efficiency
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", max_length=60, min_length=30)

def clean_html_content(html_content):
    """Clean the HTML content by removing unnecessary tags and whitespace."""
    # Remove script and style elements
    soup = BeautifulSoup(html_content, 'html.parser')
    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.extract()
    
    # Get text and clean whitespace
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text

def extract_article_content(url):
    """Extract article content from a URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # First attempt with requests and BeautifulSoup
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            html_content = response.text
            
            # Parse with BeautifulSoup for PIB-specific extraction
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for PIB article content - typically in content divs or with specific classes
            content_containers = soup.select('.PrintReleaseContent, .content, #content, .main-content, article')
            
            if content_containers:
                # Get the largest content container (most likely the article body)
                main_content = max(content_containers, key=len)
                text = clean_html_content(str(main_content))
                
                # Remove unrelated text often found in news sites
                text = re.sub(r'Share\s+on\s+|Print\s+|Tweet\s+|Email\s+|WhatsApp\s+|Follow\s+Us\s+on', '', text)
                text = re.sub(r'Comments\s+|Post\s+Comment\s+|Related\s+Articles', '', text)
                
                if len(text.strip()) > 100:  # Reasonable article length
                    return text
        
        # If the first method fails, try with newspaper3k as backup
        article = Article(url)
        article.download()
        article.parse()
        
        if article.text and len(article.text.strip()) > 100:
            return article.text
            
        # If still no content, return empty string
        return ""
        
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return ""

def generate_summary(text, title=""):
    """Generate a two-line summary of the article."""
    if not text or len(text.strip()) < 50:
        # If no meaningful content, return a message
        return "No article content available for summarization."
    
    try:
        # Combine title and text if available, as titles often contain key information
        if title:
            input_text = f"{title}. {text}"
        else:
            input_text = text
            
        # Truncate if too long for model (BART models typically have a 1024 token limit)
        max_chars = 3000  # Conservative estimate to stay under token limits
        if len(input_text) > max_chars:
            input_text = input_text[:max_chars]
        
        # Generate summary using transformer model
        summary = summarizer(input_text, max_length=60, min_length=30, do_sample=False)[0]['summary_text']
        
        # Clean the summary and ensure it's two lines
        summary = summary.replace('\n', ' ').strip()
        sentences = nltk.sent_tokenize(summary)
        
        # Limit to roughly two lines (2-3 sentences)
        if len(sentences) > 3:
            summary = ' '.join(sentences[:3])
        
        return summary
        
    except Exception as e:
        print(f"Error generating summary: {e}")
        
        # Fallback to naive extractive summary if transformer fails
        try:
            sentences = nltk.sent_tokenize(text)
            if sentences and len(sentences) >= 2:
                return ' '.join(sentences[:2])
            elif sentences:
                return sentences[0]
            else:
                return "Unable to generate summary from available content."
        except:
            return "Error in summarization process."

def get_article_summary(url, title=""):
    """Extract content and generate summary from a URL."""
    # Add a small delay to avoid overwhelming the server
    time.sleep(random.uniform(1, 3))
    
    # Extract the article content
    content = extract_article_content(url)
    
    # Generate a summary
    summary = generate_summary(content, title)
    
    return summary, content