# src/1_process_local_data.py
# Author: Manak Chand Choudhary
# Date: 21 September 2025
# Description: This script processes and combines local Kaggle datasets (app metadata + reviews)
#              and saves the result as an intermediate file, ready for scraping.

import pandas as pd
import os
from textblob import TextBlob

# --- Configuration ---
DATA_DIR = 'data'
OUTPUT_DIR = 'generated_files'

# Input files
KAGGLE_APPS_FILE = os.path.join(DATA_DIR, 'googleplaystore.csv')
KAGGLE_REVIEWS_FILE = os.path.join(DATA_DIR, 'google_play_store_user_reviews.csv')

# Output file for this script
KAGGLE_CLEANED_OUTPUT = os.path.join(OUTPUT_DIR, 'kaggle_cleaned_data.csv')


def clean_app_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans and preprocesses the main Google Play Store app metadata."""
    print("Cleaning app metadata...")
    df.dropna(subset=['Rating', 'Type', 'Content Rating', 'Android Ver'], inplace=True)
    df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce')
    df['Size'] = df['Size'].apply(lambda x: str(x).replace('M', ''))
    df['Size'] = df['Size'].apply(lambda x: str(x).replace('k', ''))
    df['Size'] = df['Size'].replace('Varies with device', pd.NA)
    df['Size'] = pd.to_numeric(df['Size'], errors='coerce')
    df['Installs'] = df['Installs'].astype(str).apply(lambda x: x.replace('+', '').replace(',', ''))
    df['Installs'] = pd.to_numeric(df['Installs'], errors='coerce')
    df['Price'] = df['Price'].astype(str).apply(lambda x: x.replace('$', ''))
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    df['Last Updated'] = pd.to_datetime(df['Last Updated'], errors='coerce')
    df.dropna(inplace=True)
    df['Reviews'] = df['Reviews'].astype(int)
    df['Installs'] = df['Installs'].astype(int)
    df['Price'] = df['Price'].astype(float)
    df['Rating'] = df['Rating'].astype(float)
    return df


def process_user_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """Analyzes sentiment in reviews and aggregates scores for each app."""
    print("Processing user reviews for sentiment...")
    df.dropna(subset=['Translated_Review'], inplace=True)
    def get_sentiment(review):
        try:
            return TextBlob(review).sentiment.polarity
        except:
            return 0.0
    df['Sentiment_Polarity'] = df['Translated_Review'].apply(get_sentiment)
    sentiment_scores = df.groupby('App')['Sentiment_Polarity'].mean().reset_index()
    return sentiment_scores


def run_local_data_pipeline():
    """Main function to orchestrate the processing of local Kaggle files."""
    print("\n====== Running Step 1: Process Local Kaggle Datasets ======")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        apps_df = pd.read_csv(KAGGLE_APPS_FILE)
        reviews_df = pd.read_csv(KAGGLE_REVIEWS_FILE)
    except FileNotFoundError as e:
        print(f"Error: Could not find a required data file: {e}")
        return

    cleaned_apps_df = clean_app_metadata(apps_df)
    sentiment_scores = process_user_reviews(reviews_df)
    
    merged_df = pd.merge(cleaned_apps_df, sentiment_scores, on='App', how='left')
    merged_df['Sentiment_Polarity'].fillna(0.0, inplace=True)
    
    merged_df.to_csv(KAGGLE_CLEANED_OUTPUT, index=False)
    print(f"\nSuccessfully processed Kaggle data and saved to {KAGGLE_CLEANED_OUTPUT}")
    print("====== Step 1 Complete ======")


if __name__ == '__main__':
    try:
        TextBlob("test")
    except Exception as e:
        print("Error: TextBlob NLTK corpora not found.")
        print("Please run the command: python -m textblob.download_corpora")
    else:
        run_local_data_pipeline()
