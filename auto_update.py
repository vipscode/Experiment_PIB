import os
import subprocess
import logging

# Set up logging to a file
logging.basicConfig(filename='auto_update.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

try:
    # Get the current directory where the script is located
    script_dir = os.path.dirname(os.path.realpath(__file__))
    
    # Path to news_extract.py relative to the current script
    news_extract_path = os.path.join(script_dir, 'news__extract.py')

    # Step 1: Run the PIB scraper to fetch articles
    logging.info("Running the PIB scraper...")
    scraper_process = subprocess.run(["python", "pib_scraper.py"], check=True)

    # Step 2: Run the categorization process only after successful scraping
    logging.info("Running the categorization process...")
    categorization_process = subprocess.run(["python", news_extract_path], check=True)

    logging.info("Scraping and categorization completed successfully.")

except subprocess.CalledProcessError as e:
    logging.error(f"Error: {e}")
    print(f"An error occurred. Check 'auto_update.log' for details.")
