import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import random
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pib_scraper.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_directories():
    """Create necessary directories if they don't exist."""
    # Use relative paths based on the script's location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    dirs = [
        os.path.join(base_dir, 'data'),
        os.path.join(base_dir, 'data', 'raw'),
        os.path.join(base_dir, 'data', 'processed')
    ]
    
    for directory in dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")
    
    return dirs[0]  # Return the base data directory

def get_news_links(url, date_str):
    """Get all news links from the PIB archive for a specific date."""
    try:
        # Add random delay to avoid being blocked
        time.sleep(random.uniform(1, 3))
        
        response = requests.get(url)
        if response.status_code != 200:
            logger.error(f"Failed to fetch URL {url}: Status code {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        news_sections = soup.find_all('div', class_='content')
        
        all_links = []
        for section in news_sections:
            links = section.find_all('a')
            for link in links:
                href = link.get('href')
                if href and '/photo' not in href and href.startswith('/'):
                    # Convert relative links to absolute URLs
                    absolute_link = f"https://pib.gov.in{href}"
                    all_links.append(absolute_link)
        
        logger.info(f"Found {len(all_links)} news links for date {date_str}")
        return all_links
    
    except Exception as e:
        logger.error(f"Error fetching news links for {date_str}: {str(e)}")
        return []

def extract_news_content(url):
    """Extract content from a news article URL."""
    try:
        # Add random delay to avoid being blocked
        time.sleep(random.uniform(1, 3))
        
        response = requests.get(url)
        if response.status_code != 200:
            logger.error(f"Failed to fetch article {url}: Status code {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title_element = soup.find('h3', class_='release-title')
        title = title_element.text.strip() if title_element else "No title found"
        
        # Extract date
        date_element = soup.find('div', class_='ReleaseDateSubHeaddateTime')
        date = date_element.text.strip() if date_element else "No date found"
        
        # Extract ministry
        ministry_element = soup.find('div', class_='MinistryNameSubhead')
        ministry = ministry_element.text.strip() if ministry_element else "No ministry found"
        
        # Extract content
        content_element = soup.find('div', class_='PrintContent')
        content = content_element.text.strip() if content_element else "No content found"
        
        return {
            'title': title,
            'date': date,
            'ministry': ministry,
            'content': content,
            'url': url
        }
    
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {str(e)}")
        return None

def scrape_date_range(start_date, end_date):
    """Scrape news articles for a range of dates."""
    base_dir = create_directories()
    
    # Convert string dates to datetime objects if they are strings
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%d-%m-%Y')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%d-%m-%Y')
    
    current_date = start_date
    all_articles = []
    
    while current_date <= end_date:
        date_str = current_date.strftime('%d-%m-%Y')
        url = f"https://pib.gov.in/AllReleasem.aspx?MenuId=3&Date={date_str}"
        
        logger.info(f"Scraping news for date: {date_str}")
        news_links = get_news_links(url, date_str)
        
        date_articles = []
        for link in news_links:
            article = extract_news_content(link)
            if article:
                date_articles.append(article)
        
        # Save daily articles
        if date_articles:
            daily_df = pd.DataFrame(date_articles)
            output_file = os.path.join(base_dir, 'raw', f"pib_news_{current_date.strftime('%Y%m%d')}.csv")
            daily_df.to_csv(output_file, index=False, encoding='utf-8')
            logger.info(f"Saved {len(date_articles)} articles for {date_str} to {output_file}")
            
            all_articles.extend(date_articles)
        
        current_date += timedelta(days=1)
    
    # Save all articles to a combined file
    if all_articles:
        combined_df = pd.DataFrame(all_articles)
        output_file = os.path.join(base_dir, 'processed', f"pib_news_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.csv")
        combined_df.to_csv(output_file, index=False, encoding='utf-8')
        logger.info(f"Saved combined {len(all_articles)} articles to {output_file}")
    
    return all_articles

if __name__ == "__main__":
    # Example usage
    # Scrape last 7 days
    end_date = datetime.today()
    start_date = end_date - timedelta(days=7)
    
    logger.info(f"Starting scraping from {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}")
    articles = scrape_date_range(start_date, end_date)
    logger.info(f"Scraping completed. Total articles scraped: {len(articles)}")
