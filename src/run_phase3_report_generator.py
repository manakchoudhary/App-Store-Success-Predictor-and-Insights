# src/run_phase3_report_generator.py
# Author: Manak Chand Choudhary
# Date: 21 September 2025
# Description: This is the main script to run the Phase 3 Automated Report Generator.
#              It loads the insights from Phase 2 and orchestrates the creation
#              of a final, AI-powered executive report.

import json
import os
from datetime import datetime
import sys

# --- Path Correction ---
# Add the 'src' directory to the Python path to allow for absolute imports from 'src'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the new report generator module
from phase3.report_generator import generate_executive_report

# --- Configuration ---
OUTPUT_DIR = 'generated_files'
REPORTS_SUBDIR = 'reports' # A new subdirectory for our final reports

# Input file from Phase 2
INSIGHTS_INPUT_FILE = os.path.join(OUTPUT_DIR, 'generated_insights.json')

# Output file for this script
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT_OUTPUT_FILE = os.path.join(OUTPUT_DIR, REPORTS_SUBDIR, f'App_Success_Report_{TIMESTAMP}.md')


def run_report_generator():
    """Main function to run the report generation pipeline."""
    print("\n====== Running Phase 3: Automated Report Generator ======")
    
    # Create the reports directory if it doesn't exist
    os.makedirs(os.path.join(OUTPUT_DIR, REPORTS_SUBDIR), exist_ok=True)

    # --- Load Data ---
    try:
        with open(INSIGHTS_INPUT_FILE, 'r') as f:
            insights_data = json.load(f)
        print(f"Successfully loaded {len(insights_data.get('insights', []))} insights.")
    except FileNotFoundError:
        print(f"Error: Insights file not found at {INSIGHTS_INPUT_FILE}.")
        print("Please ensure you have successfully run the Phase 2 Insight Engine first.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode the JSON from {INSIGHTS_INPUT_FILE}.")
        return

    # --- Generate Report ---
    print("Generating executive intelligence report...")
    # Pass the raw insights to the generator module
    executive_report = generate_executive_report(insights_data['insights'])

    # --- Save Report ---
    if executive_report:
        with open(REPORT_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(executive_report)
        print(f"\nSuccessfully generated and saved the report.")
        print(f"Output file located at: {REPORT_OUTPUT_FILE}")
    else:
        print("Failed to generate the executive report.")

    print("====== Phase 3 Complete ======")


if __name__ == '__main__':
    # Create the phase3 directory if it doesn't exist, to allow imports
    if not os.path.exists('src/phase3'):
        os.makedirs('src/phase3')
    # Create an __init__.py to make it a package
    with open('src/phase3/__init__.py', 'w') as f:
        pass
        
    run_report_generator()

