# src/3_combine_datasets.py
# Author: Manak Chand Choudhary
# Date: 21 September 2025
# Description: This is the final step of the Phase 1 pipeline. It combines the cleaned
#              Kaggle dataset (Google Play Store data) with the freshly scraped
#              Apple App Store data into a single, unified master dataset for analysis.

import pandas as pd
import os

# --- Configuration ---
OUTPUT_DIR = 'generated_files'

# Input files
KAGGLE_INPUT = os.path.join(OUTPUT_DIR, 'kaggle_cleaned_data.csv')
REALTIME_INPUT = os.path.join(OUTPUT_DIR, 'realtime_scraped_data.csv')

# Final master output file
MASTER_OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'final_master_app_data.csv')


def run_final_merge():
    """
    Merges the cleaned Kaggle data with the scraped real-time data to produce
    a master dataset with comparative columns.
    """
    print("\n====== Running Step 3: Combine All Datasets ======")

    # --- Load Datasets ---
    try:
        kaggle_df = pd.read_csv(KAGGLE_INPUT)
        realtime_df = pd.read_csv(REALTIME_INPUT)
        print("Successfully loaded both Kaggle and real-time datasets.")
    except FileNotFoundError as e:
        print(f"Error: A required input file was not found: {e.filename}")
        print("Please ensure you have successfully run both '1_process_local_data.py' and '2_scrape_and_combine.py' first.")
        return

    # --- Prepare for Merging ---
    # Rename columns in the real-time data to be specific and avoid conflicts.
    # This clarifies that these metrics are from the Apple App Store.
    realtime_df.rename(columns={
        'Realtime_Rating': 'Apple_Store_Rating',
        'Realtime_Reviews': 'Apple_Store_Reviews',
        'Realtime_Price': 'Apple_Store_Price'
    }, inplace=True)
    
    print("Renamed real-time data columns for clarity (e.g., 'Apple_Store_Rating').")

    # --- Merge the Datasets ---
    # Perform a 'left' merge to keep all the original apps from the Kaggle dataset.
    # The scraped Apple App Store data will be added where the app names match.
    master_df = pd.merge(kaggle_df, realtime_df, on='App', how='left')
    print("Successfully merged the two datasets.")
    
    # --- Save Final Output ---
    master_df.to_csv(MASTER_OUTPUT_FILE, index=False)
    print(f"\nFinal master dataset created with {len(master_df)} rows and {len(master_df.columns)} columns.")
    print(f"Saved to: {MASTER_OUTPUT_FILE}")
    print("====== Step 3 Complete ======")


if __name__ == '__main__':
    run_final_merge()
