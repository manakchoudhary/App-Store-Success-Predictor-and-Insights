# src/2_scrape_and_combine.py
# Author: Manak Chand Choudhary
# Date: 21 September 2025
# Description: This script scrapes real-time data for a sample of top apps from the
#              Apple App Store using the SerpApi service, saves the latest results to a main file,
#              and archives a copy with a timestamp.

import pandas as pd
import os
import requests
import time
from dotenv import load_dotenv
import re
from datetime import datetime

# --- Configuration ---
load_dotenv()  # Load environment variables from a .env file

OUTPUT_DIR = 'generated_files'
ARCHIVE_DIR = os.path.join(OUTPUT_DIR, 'archive') # Directory for historical scrapes

# Input file (output from the first script)
KAGGLE_CLEANED_INPUT = os.path.join(OUTPUT_DIR, 'kaggle_cleaned_data.csv')

# Main output file (updated each run)
REALTIME_OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'realtime_scraped_data.csv')

# SerpApi Configuration
SERPAPI_KEY = os.getenv('SERPAPI_KEY')
SERPAPI_URL = 'https://serpapi.com/search.json'


def fetch_realtime_data(app_name: str) -> dict | str | None:
    """
    Fetches real-time app data from the Apple App Store using SerpApi.
    Returns a dictionary on success, a specific error string on fatal errors, or None on other failures.
    """
    if not SERPAPI_KEY:
        return None

    params = {
        "api_key": SERPAPI_KEY,
        "engine": "apple_app_store",
        "store": "apps",
        "term": app_name,  # Changed 'q' to 'term' for clarity
        "hl": "en",
        "gl": "us"
    }

    try:
        response = requests.get(SERPAPI_URL, params=params, timeout=20)
        response.raise_for_status()
        
        data = response.json()

        # Check if the API returned any results
        if data and data.get('organic_results'):
            # Assume the first result is the most relevant one
            app_info = data['organic_results'][0]
            
            # --- Safely parse the new, nested JSON structure ---
            realtime_rating = None
            realtime_reviews = None
            # The 'rating' key now contains a list of dictionaries
            if app_info.get('rating') and isinstance(app_info['rating'], list) and len(app_info['rating']) > 0:
                rating_info = app_info['rating'][0]
                realtime_rating = rating_info.get('rating')
                realtime_reviews = rating_info.get('count')

            # The 'price' key is now a dictionary
            price = 0.0
            if app_info.get('price') and isinstance(app_info['price'], dict):
                price = float(app_info['price'].get('amount', 0.0))

            return {
                'App': app_name,
                'Realtime_Rating': realtime_rating,
                'Realtime_Reviews': realtime_reviews,
                'Realtime_Price': price
            }
        else:
            print(f"    - No results found in API response for: {app_name}")
            return None

    except requests.exceptions.HTTPError as e:
        # SerpApi uses 401 for bad API key
        if e.response.status_code in [401, 403]:
            print(f"    - FATAL ERROR: {e.response.status_code} Unauthorized/Forbidden.")
            print("    - Please check that your SERPAPI_KEY in the .env file is correct and valid.")
            return 'FORBIDDEN'
        # SerpApi uses 429 for rate limit
        if e.response.status_code == 429:
            print(f"    - FATAL ERROR: 429 Too Many Requests for {app_name}.")
            print("    - You have exceeded your SerpApi plan's limit.")
            return 'RATE_LIMITED'
        print(f"    - API request failed for {app_name}: {e}")
    except requests.exceptions.RequestException as e:
        print(f"    - A network-related error occurred for {app_name}: {e}")
    except (KeyError, IndexError):
        print(f"    - Could not parse the API response for: {app_name}")
    return None


def run_scrape_pipeline():
    """Main function to scrape real-time data and save it to a file."""
    print("\n====== Running Step 2: Scrape Real-time Data via SerpApi (Apple App Store) ======")
    
    # Create the archive directory if it doesn't exist
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    if not SERPAPI_KEY:
        print("Skipping scraping: SERPAPI_KEY not found in .env file.")
        return

    try:
        main_df = pd.read_csv(KAGGLE_CLEANED_INPUT)
    except FileNotFoundError:
        print(f"Error: Cannot find {KAGGLE_CLEANED_INPUT}.")
        print("Please run the '1_process_local_data.py' script first.")
        return

    # Select a mix of top free and paid apps for scraping
    top_free_apps = main_df[main_df['Price'] == 0].nlargest(50, 'Installs')['App'].tolist()
    top_paid_apps = main_df[main_df['Price'] > 0].nlargest(50, 'Installs')['App'].tolist()
    
    sample_apps = top_free_apps + top_paid_apps
    # Remove duplicates in case an app exists in both somehow, preserving order
    sample_apps = list(dict.fromkeys(sample_apps))

    print(f"Scraping real-time data for a sample of {len(sample_apps)} top apps (including paid ones)...")
    
    realtime_results = []
    stop_scraping = False
    for app_name in sample_apps:
        print(f"  - Fetching: {app_name}")
        data = fetch_realtime_data(app_name)
        
        if data in ('FORBIDDEN', 'RATE_LIMITED'):
            stop_scraping = True
            break

        if data:
            realtime_results.append(data)
        
        time.sleep(1.2) # Add a delay to be respectful to the API

    if stop_scraping:
        print("\nScraping process halted due to a critical API error.")
        return

    if not realtime_results:
        print("No real-time data was successfully scraped. Halting process.")
        return

    realtime_df = pd.DataFrame(realtime_results)
    
    # Save to the main file (this is updated on each run)
    realtime_df.to_csv(REALTIME_OUTPUT_FILE, index=False)
    print(f"\nSuccessfully updated latest scrape data in: {REALTIME_OUTPUT_FILE}")

    # Save to a new, timestamped archive file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_filename = f"realtime_scraped_data_{timestamp}.csv"
    archive_filepath = os.path.join(ARCHIVE_DIR, archive_filename)
    realtime_df.to_csv(archive_filepath, index=False)
    print(f"Saved an archive copy to: {archive_filepath}")

    print("====== Step 2 Complete ======")


if __name__ == '__main__':
    run_scrape_pipeline()

