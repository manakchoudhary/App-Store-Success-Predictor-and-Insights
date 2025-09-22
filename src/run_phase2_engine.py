# src/run_phase2_engine.py
# Author: Manak Chand Choudhary
# Date: 21 September 2025
# Description: This is the main script to run the Phase 2 Insight Generation Engine.
#              It orchestrates the process by loading data, calling the analysis module,
#              formatting the results, and saving the final insights.

import pandas as pd
import json
import os

# Import the modularized functions
from phase2.analysis import (
    analyze_success_factors, 
    analyze_pricing_strategies, 
    analyze_market_opportunities,
    analyze_feature_recommendations
)
from phase2.formatter import format_insight

# --- Configuration ---
OUTPUT_DIR = 'generated_files'

# Input file from Phase 1
MASTER_DATA_INPUT = os.path.join(OUTPUT_DIR, 'final_master_app_data.csv')

# Output file for this script
INSIGHTS_OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'generated_insights.json')


def run_analysis_engine():
    """Main function to run the insight generation pipeline."""
    print("\n====== Running Phase 2: AI-Powered Insight Engine (Modular) ======")
    
    # --- Load Data ---
    try:
        master_df = pd.read_csv(MASTER_DATA_INPUT)
        print(f"Successfully loaded master dataset with {len(master_df)} records.")
    except FileNotFoundError:
        print(f"Error: Master data file not found at {MASTER_DATA_INPUT}.")
        print("Please ensure you have successfully run the entire Phase 1 pipeline.")
        return

    # --- Run Analysis ---
    # Call all available analysis functions and combine their raw results.
    success_insights = analyze_success_factors(master_df)
    pricing_insights = analyze_pricing_strategies(master_df)
    market_insights = analyze_market_opportunities(master_df)
    feature_insights = analyze_feature_recommendations(master_df)
    
    raw_insights = success_insights + pricing_insights + market_insights + feature_insights
    
    # --- Format Insights ---
    formatted_insights = [format_insight(r, i+1) for i, r in enumerate(raw_insights) if r]

    if not formatted_insights:
        print("Could not generate any formatted insights from the analysis.")
        return
        
    final_output = {"insights": formatted_insights}

    # --- Save Results ---
    with open(INSIGHTS_OUTPUT_FILE, 'w') as f:
        json.dump(final_output, f, indent=4)
        
    print(f"\nSuccessfully generated and saved {len(formatted_insights)} insights.")
    print(f"Output file located at: {INSIGHTS_OUTPUT_FILE}")
    print("====== Phase 2 (All Analyses) Complete ======")


if __name__ == '__main__':
    # Create the phase2 directory if it doesn't exist, to allow imports
    if not os.path.exists('src/phase2'):
        os.makedirs('src/phase2')
    # Create an __init__.py to make it a package
    with open('src/phase2/__init__.py', 'w') as f:
        pass
        
    run_analysis_engine()

