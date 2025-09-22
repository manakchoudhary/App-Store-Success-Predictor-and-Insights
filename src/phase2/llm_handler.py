# src/phase2/llm_handler.py
# Author: Manak Chand Choudhary
# Date: 21 September 2025
# Description: This module handles all interactions with the Google Gemini LLM.
#              It contains specialized functions for generating structured insights (Phase 2)
#              and a general-purpose query function for summarization (Phase 3).

import os
import requests
import json
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
# UPDATED: Changed the model endpoint URL as requested.
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"


def query_llm(prompt: str) -> str | None:
    """
    General-purpose function to send a prompt to the Gemini LLM.
    Used for tasks like generating the executive summary in Phase 3.
    """
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY not found. LLM queries will be skipped.")
        return None

    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        if 'candidates' in result and result['candidates']:
            first_candidate = result['candidates'][0]
            if 'content' in first_candidate and 'parts' in first_candidate['content'] and first_candidate['content']['parts']:
                return first_candidate['content']['parts'][0]['text'].strip()

    except requests.exceptions.HTTPError as e:
        print(f"Error: LLM API request failed with status code {e.response.status_code}")
        print(f"Response: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error: A network-related error occurred while querying the LLM: {e}")
    except (KeyError, IndexError, TypeError) as e:
        print(f"Error: Could not parse the LLM response. Error: {e}")
        
    return None


def generate_llm_insight(raw_insight: dict) -> dict | None:
    """
    Generates a structured insight (text + recommendations) using an LLM.
    Used specifically for formatting the detailed insights in Phase 2.
    """
    if not GEMINI_API_KEY:
        return None
        
    prompt = _create_prompt(raw_insight)
    if not prompt:
        return None

    try:
        response_text = query_llm(prompt) # Re-use the core query function
        if not response_text:
            return None

        cleaned_content = response_text.strip().replace('```json', '').replace('```', '')
        llm_data = json.loads(cleaned_content)
        
        if 'insight_text' in llm_data and 'recommendations' in llm_data:
            return llm_data
        else:
            print("LLM response was missing required keys.")
            return None
            
    except json.JSONDecodeError as e:
        print(f"Error parsing LLM response: {e}")
        print(f"Raw response content: {response_text}")
        return None

def _create_prompt(raw_insight: dict) -> str | None:
    """Dispatcher function to create a specific prompt for each insight type."""
    prompt_generators = {
        'correlation': _prompt_for_correlation,
        'rating_impact': _prompt_for_rating_impact,
        'pricing_optimization': _prompt_for_pricing,
        'market_opportunity': _prompt_for_market_opportunity,
        'feature_recommendation': _prompt_for_feature_recommendation
    }
    
    generator = prompt_generators.get(raw_insight['type'])
    if generator:
        return generator(raw_insight)
    return None

# --- Specific Prompt Generation Functions for Phase 2 Insights ---

def _prompt_for_correlation(data: dict) -> str:
    return f"""
    As an expert mobile app market analyst, analyze the following data:
    - Data: A correlation of {data['correlation_value']:.2f} was found between an app's '{data['secondary_metric']}' and its '{data['primary_metric']}'.
    - Sample Size: {data['sample_size']} apps.
    
    Generate a professional insight and 2-3 actionable business recommendations.
    Return your response as a JSON object with keys "insight_text" (string) and "recommendations" (list of strings).
    """

def _prompt_for_rating_impact(data: dict) -> str:
    return f"""
    As an expert mobile app market analyst, analyze the following data:
    - Data: Apps with a rating >= {data['threshold']} have {data['install_multiple']:.1f}x more installs than lower-rated apps.
    - High-rated apps average installs: {int(data['avg_installs_high']):,}
    - Low-rated apps average installs: {int(data['avg_installs_low']):,}
    - Sample Size: {data['sample_size']} apps.

    Generate a professional insight and 2-3 actionable business recommendations.
    Return your response as a JSON object with keys "insight_text" (string) and "recommendations" (list of strings).
    """

def _prompt_for_pricing(data: dict) -> str:
    return f"""
    As an expert mobile app market analyst, analyze the following data for the '{data['category']}' app category:
    - Data: The price range of '{data['optimal_price_range']}' has the highest average user rating of {data['avg_rating_in_range']:.2f}.
    - Sample Size: {data['sample_size']} paid apps in this category.

    Generate a professional insight about value perception and 2-3 actionable pricing recommendations.
    Return your response as a JSON object with keys "insight_text" (string) and "recommendations" (list of strings).
    """
    
def _prompt_for_market_opportunity(data: dict) -> str:
    return f"""
    As an expert mobile app market analyst, analyze the following data to find market gaps:
    - Category: '{data['category']}'
    - Average Installs: {int(data['avg_installs']):,} per app.
    - Number of Apps (Supply): {data['app_count']} apps.
    - Insight: This category has a very high demand-to-supply ratio.

    Generate a professional insight about this potential market opportunity and 2-3 strategic recommendations.
    Return your response as a JSON object with keys "insight_text" (string) and "recommendations" (list of strings).
    """
    
def _prompt_for_feature_recommendation(data: dict) -> str:
    return f"""
    As an expert mobile app market analyst, analyze the following feature data for the '{data['category']}' category:
    - Data: Among the top-performing apps, the most common secondary feature/genre is '{data['recommended_feature']}'.
    - Frequency: This feature appeared in {data['feature_frequency']} of the {data['successful_app_sample_size']} successful apps analyzed.
    
    Generate a professional insight about product development and 2-3 actionable feature recommendations.
    Return your response as a JSON object with keys "insight_text" (string) and "recommendations" (list of strings).
    """

