import os
import logging
import datetime

# Basic setup for logging to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Simple test function to verify GitHub Actions environment."""
    logger.info("Starting test script")
    
    # Print environment information
    print(f"Current working directory: {os.getcwd()}")
    print(f"Directory contents: {os.listdir('.')}")
    
    # Create test directories
    print("Creating test directories...")
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    # Create a test file in each directory
    with open('data/raw/test_file.txt', 'w') as f:
        f.write(f"Test file created at {datetime.datetime.now()}")
    
    with open('data/processed/test_file.txt', 'w') as f:
        f.write(f"Test file created at {datetime.datetime.now()}")
    
    # Create a test log file
    with open('pib_scraper.log', 'w') as f:
        f.write(f"Test log file created at {datetime.datetime.now()}")
    
    # List all files to verify
    print("Files created:")
    for root, dirs, files in os.walk('.'):
        for file in files:
            print(os.path.join(root, file))
    
    logger.info("Test completed successfully")

if __name__ == "__main__":
    main()
