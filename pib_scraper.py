from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os
import re
from datetime import datetime

# Configuration
geckodriver_path = r"C:\Users\vipul\geckodriver-v0.34.0-win64\geckodriver.exe"
headless_mode = False  # Set to True to run without browser window
wait_time = 10  # Seconds to wait for page load after applying filters

# Setup driver
service = Service(geckodriver_path)
options = webdriver.FirefoxOptions()
if headless_mode:
    options.add_argument("--headless")
driver = webdriver.Firefox(service=service, options=options)

# Function to clean text
def clean_text(text):
    if text is None:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

# Function to extract date in a standardized format
def extract_date(text):
    if not text:
        return None
    
    # Try to extract date using patterns
    date_patterns = [
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',  # DD/MM/YYYY or DD-MM-YYYY
        r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{2,4})'   # DD Month YYYY
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return None

# Function to parse and standardize date for comparison
def parse_date(date_str):
    if not date_str:
        return None
    
    try:
        # Check format with numeric month (DD/MM/YYYY)
        match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', date_str)
        if match:
            day, month, year = match.groups()
            # Ensure 4-digit year
            if len(year) == 2:
                year = '20' + year
            return datetime(int(year), int(month), int(day))
        
        # Check format with text month (DD Month YYYY)
        match = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{2,4})', date_str, re.IGNORECASE)
        if match:
            day, month_name, year = match.groups()
            month_map = {
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
            }
            month = month_map.get(month_name.lower()[:3], 1)  # Default to January if unknown
            return datetime(int(year), month, int(day))
    except:
        pass
    
    return None

def format_date(date_obj):
    if not date_obj:
        return "Unknown"
    return date_obj.strftime("%d %b %Y")

try:
    print("Opening PIB website...")
    driver.get("https://pib.gov.in/allRel.aspx?reg=3&lang=1")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    
    # Apply filters
    print("Applying filters...")
    
    # Day filter (All days)
    day_dropdown = driver.find_element(By.ID, "ContentPlaceHolder1_ddlday")
    Select(day_dropdown).select_by_value("0")
    time.sleep(2)
    
    # Month filter(put any value for the month, 4 = april etc.)
    month_dropdown = driver.find_element(By.ID, "ContentPlaceHolder1_ddlMonth")
    Select(month_dropdown).select_by_value("5")
    time.sleep(2)
    
    # Year filter (2025)
    year_dropdown = driver.find_element(By.ID, "ContentPlaceHolder1_ddlYear")
    Select(year_dropdown).select_by_value("2025")
    time.sleep(2)
    
    # Ministry filter (Health)
    ministry_dropdown = driver.find_element(By.ID, "ContentPlaceHolder1_ddlMinistry")
    Select(ministry_dropdown).select_by_value("31")
    
    # Wait for content to load after filters
    print(f"Waiting {wait_time} seconds for results to load...")
    time.sleep(wait_time)
    
    # ========== APPROACH 1: Look for table rows that contain both date and news items ==========
    print("\nATTEMPT 1: Searching for news items in table format...")
    news_items = []
    
    try:
        # First, look for tables or lists that contain news items
        tables = driver.find_elements(By.TAG_NAME, "table")
        for table in tables:
            try:
                # Check if this looks like a news table
                rows = table.find_elements(By.TAG_NAME, "tr")
                if len(rows) <= 1:  # Skip tables with just headers
                    continue
                
                print(f"Found table with {len(rows)} rows")
                
                for row in rows:
                    try:
                        # Most PIB tables have date in first column and title/link in second
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) < 2:
                            continue
                            
                        date_cell = cells[0]
                        title_cell = cells[1]
                        
                        date_text = clean_text(date_cell.text)
                        date_val = extract_date(date_text)
                        
                        # Look for links in the title cell
                        links = title_cell.find_elements(By.TAG_NAME, "a")
                        if links:
                            link = links[0]
                            url = link.get_attribute("href")
                            title = clean_text(link.text)
                            
                            if url and title and date_val:
                                news_items.append({
                                    'title': title,
                                    'date': date_val,
                                    'link': url,
                                    'source': 'table'
                                })
                    except Exception as e:
                        continue
            except:
                continue
        
        print(f"Found {len(news_items)} items in tables")
    except Exception as e:
        print(f"Error in table search: {e}")
    
    # ========== APPROACH 2: Look for news items in standardized DIV structure ==========
    if len(news_items) < 5:  # If we didn't find many items in tables, try div approach
        print("\nATTEMPT 2: Searching for news items in div structure...")
        
        # Look for common containers that hold news items
        containers = driver.find_elements(By.XPATH, 
            "//*[contains(@class, 'content') or contains(@class, 'news') or contains(@class, 'list')]")
        
        for container in containers:
            try:
                # Get all links in the container
                links = container.find_elements(By.TAG_NAME, "a")
                for link in links:
                    try:
                        url = link.get_attribute("href")
                        title = clean_text(link.text)
                        
                        # Skip navigation and empty links
                        if not url or not title or len(title) < 10 or url.endswith('#'):
                            continue
                            
                        # Check if this looks like a news link
                        if "release" not in url.lower() and "newsite" not in url.lower():
                            continue
                        
                        # Try to find a date near this link
                        date_val = None
                        
                        # Method 1: Check parent or parent's siblings for date
                        parent = link.find_element(By.XPATH, "./parent::*")
                        parent_text = clean_text(parent.text)
                        parent_date = extract_date(parent_text)
                        if parent_date:
                            date_val = parent_date
                        
                        # Method 2: Check siblings
                        if not date_val:
                            try:
                                siblings = parent.find_elements(By.XPATH, "./preceding-sibling::*[1] | ./following-sibling::*[1]")
                                for sibling in siblings:
                                    sibling_text = clean_text(sibling.text)
                                    sibling_date = extract_date(sibling_text)
                                    if sibling_date:
                                        date_val = sibling_date
                                        break
                            except:
                                pass
                        
                        # Method 3: Check for date in small text or span near the link
                        if not date_val:
                            try:
                                date_elements = driver.find_elements(By.XPATH, 
                                    "//small[contains(text(), '/') or contains(text(), 'Jan')] | " +
                                    "//span[contains(text(), '/') or contains(text(), 'Jan')]")
                                
                                link_pos = link.location
                                closest_date = None
                                min_distance = float('inf')
                                
                                for date_elem in date_elements:
                                    try:
                                        date_pos = date_elem.location
                                        # Calculate vertical distance
                                        distance = abs(date_pos['y'] - link_pos['y'])
                                        if distance < min_distance and distance < 100:  # Within 100px vertically
                                            min_distance = distance
                                            date_text = clean_text(date_elem.text)
                                            closest_date = extract_date(date_text)
                                    except:
                                        continue
                                
                                if closest_date:
                                    date_val = closest_date
                            except:
                                pass
                        
                        # If we have a valid URL, title, and date, add to our list
                        if url and title and date_val:
                            # Check if this is a duplicate before adding
                            is_duplicate = False
                            for item in news_items:
                                if item['link'] == url:
                                    is_duplicate = True
                                    break
                            
                            if not is_duplicate:
                                news_items.append({
                                    'title': title,
                                    'date': date_val,
                                    'link': url,
                                    'source': 'div'
                                })
                    except:
                        continue
            except:
                continue
        
        print(f"Found {len(news_items)} total news items after div search")
    
    # ========== APPROACH 3: Direct search for all links with release IDs ==========
    if len(news_items) < 10:  # If we still don't have enough items
        print("\nATTEMPT 3: Direct search for release links...")
        
        # Look specifically for links that contain releaseId
        release_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'releaseId') or contains(@href, 'release.aspx')]")
        print(f"Found {len(release_links)} direct release links")
        
        # Process only links not already in our list
        existing_urls = {item['link'] for item in news_items}
        
        for link in release_links:
            try:
                url = link.get_attribute("href")
                title = clean_text(link.text)
                
                # Skip already processed links
                if url in existing_urls or not title or len(title) < 10:
                    continue
                
                # For direct approach, we'll use the whole page's date context
                date_val = None
                
                # Find nearby date elements
                try:
                    # Get link position
                    link_pos = link.location
                    
                    # Find all elements that might contain dates
                    date_elements = driver.find_elements(By.XPATH, 
                        "//*[contains(text(), '/') or contains(text(), 'Jan') or " +
                        "contains(text(), 'Feb') or contains(text(), 'Mar')]")
                    
                    min_distance = float('inf')
                    for date_elem in date_elements:
                        try:
                            date_pos = date_elem.location
                            distance = abs(date_pos['y'] - link_pos['y'])
                            
                            if distance < min_distance and distance < 150:  # More flexible distance
                                date_text = clean_text(date_elem.text)
                                extracted_date = extract_date(date_text)
                                if extracted_date:
                                    min_distance = distance
                                    date_val = extracted_date
                        except:
                            continue
                except:
                    pass
                
                # If we have a valid date, add the item
                if date_val:
                    news_items.append({
                        'title': title,
                        'date': date_val,
                        'link': url,
                        'source': 'direct'
                    })
                    existing_urls.add(url)
            except:
                continue
                
        print(f"Found {len(news_items)} total news items after direct link search")
    
    # Process and standardize dates
    for item in news_items:
        date_obj = parse_date(item['date'])
        if date_obj:
            item['date'] = format_date(date_obj)
        else:
            item['date'] = "Unknown"
    
    # Sort news items by date (most recent first)
    def get_date_for_sorting(item):
        date_str = item.get('date', 'Unknown')
        if date_str == "Unknown":
            return datetime(1900, 1, 1)  # Default old date for unknown
        
        date_obj = parse_date(date_str)
        return date_obj if date_obj else datetime(1900, 1, 1)
    
    news_items = sorted(news_items, key=get_date_for_sorting, reverse=True)
    
    # Remove duplicate links (keep the first occurrence)
    unique_links = set()
    unique_news_items = []
    for item in news_items:
        if item['link'] not in unique_links:
            unique_links.add(item['link'])
            # Remove the metadata field before saving
            if 'source' in item:
                del item['source']
            unique_news_items.append(item)
    
    # Print found items for review
    print("\nFound news items:")
    for i, item in enumerate(unique_news_items):
        print(f"{i+1}. {item['title'][:50]}... ({item['date']})")
    
    # Save to data.json
    output_file = 'data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_news_items, f, ensure_ascii=False, indent=4)
    
    print(f"\nSaved {len(unique_news_items)} unique news items to {os.path.abspath(output_file)}")
    
    if len(unique_news_items) == 0:
        print("\nNo news items found. Possible reasons:")
        print("1. There might be no news for the selected filters")
        print("2. The website structure may have changed")
        print("3. The wait time after applying filters might need to be increased")
    
except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Always close the driver
    print("Closing browser...")
    driver.quit()