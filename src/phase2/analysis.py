# src/phase2/analysis.py
# Author: Manak Chand Choudhary
# Date: 21 September 2025
# Description: This module contains the core statistical analysis functions for the Insight Engine.
#              Each function is now configured to generate a larger volume of insights
#              to meet the project's "100+" requirement.

import pandas as pd
import numpy as np
from collections import Counter

def analyze_success_factors(df: pd.DataFrame) -> list:
    """
    Performs statistical analysis to find key drivers of app success.
    """
    print("Analyzing data to identify key success factors...")
    insights = []
    
    # This analysis remains focused on high-level correlations, so its output is naturally small.
    correlation_columns = ['Rating', 'Reviews', 'Installs', 'Sentiment_Polarity']
    valid_cols = [col for col in correlation_columns if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]
    if 'Installs' not in valid_cols:
        return []

    correlation_matrix = df[valid_cols].corr()
    
    if 'Installs' in correlation_matrix:
        correlations_with_installs = correlation_matrix['Installs'].drop('Installs', errors='ignore')
        if not correlations_with_installs.empty:
            strongest_correlation = correlations_with_installs.idxmax()
            correlation_value = correlations_with_installs[strongest_correlation]

            if pd.notna(correlation_value):
                insights.append({
                    'type': 'correlation',
                    'primary_metric': 'Installs',
                    'secondary_metric': strongest_correlation,
                    'correlation_value': correlation_value,
                    'sample_size': len(df)
                })

    high_rating_threshold = 4.5
    high_rated_apps = df[df['Rating'] >= high_rating_threshold]
    low_rated_apps = df[df['Rating'] < high_rating_threshold]

    if not high_rated_apps.empty and not low_rated_apps.empty:
        avg_installs_high_rated = high_rated_apps['Installs'].mean()
        avg_installs_low_rated = low_rated_apps['Installs'].mean()
        
        if avg_installs_low_rated > 0:
            install_multiple = avg_installs_high_rated / avg_installs_low_rated
            insights.append({
                'type': 'rating_impact',
                'threshold': high_rating_threshold,
                'avg_installs_high': avg_installs_high_rated,
                'avg_installs_low': avg_installs_low_rated,
                'install_multiple': install_multiple,
                'sample_size': len(df)
            })

    print(f"Generated {len(insights)} raw insights from success factor analysis.")
    return insights


def analyze_pricing_strategies(df: pd.DataFrame) -> list:
    """
    Analyzes pricing data across ALL valid categories to generate a large number of insights.
    """
    print("Analyzing data for pricing strategy optimization...")
    insights = []
    
    paid_apps = df[(df['Type'] == 'Paid') & (df['Price'] > 0) & (df['Installs'] > 1000)].copy()

    if paid_apps.empty:
        print("No sufficient data on paid apps to analyze pricing strategies.")
        return []

    price_bins = [0, 1.99, 4.99, 9.99, 29.99, np.inf]
    price_labels = ['$0.01-$1.99', '$2.00-$4.99', '$5.00-$9.99', '$10.00-$29.99', '$30.00+']
    paid_apps['Price_Bin'] = pd.cut(paid_apps['Price'], bins=price_bins, labels=price_labels, right=True)

    # EXPANSION: Instead of top 5, get all categories that have at least 10 paid apps.
    category_counts = paid_apps['Category'].value_counts()
    valid_categories = category_counts[category_counts >= 10].index

    for category in valid_categories:
        category_apps = paid_apps[paid_apps['Category'] == category]
        
        revenue_analysis = category_apps.groupby('Price_Bin', observed=False)['Rating'].mean().reset_index()
        
        if not revenue_analysis.empty and revenue_analysis['Rating'].notna().any():
            optimal_bin = revenue_analysis.loc[revenue_analysis['Rating'].idxmax()]
            
            insights.append({
                'type': 'pricing_optimization',
                'category': category,
                'optimal_price_range': optimal_bin['Price_Bin'],
                'avg_rating_in_range': optimal_bin['Rating'],
                'sample_size': len(category_apps)
            })

    print(f"Generated {len(insights)} raw insights from pricing analysis.")
    return insights

def analyze_market_opportunities(df: pd.DataFrame) -> list:
    """
    Identifies untapped or underserved market categories by analyzing ALL valid categories.
    """
    print("Analyzing data for market opportunities...")
    insights = []
    
    market_analysis = df.groupby('Category').agg(
        supply=('App', 'count'),
        demand_proxy=('Installs', 'mean')
    ).reset_index()

    # Define a minimum threshold for the number of apps in a category to be considered.
    market_analysis = market_analysis[market_analysis['supply'] > 20]

    if market_analysis.empty:
        return []

    market_analysis['opportunity_score'] = market_analysis['demand_proxy'] / market_analysis['supply']
    
    # EXPANSION: Analyze ALL categories that meet the threshold, not just the top 15.
    # We will sort by score to still prioritize the most interesting ones for the LLM.
    potential_opportunities = market_analysis.sort_values(by='opportunity_score', ascending=False)
    
    for _, opportunity in potential_opportunities.iterrows():
        insights.append({
            'type': 'market_opportunity',
            'category': opportunity['Category'],
            'avg_installs': opportunity['demand_proxy'],
            'app_count': opportunity['supply'],
            'opportunity_score': opportunity['opportunity_score']
        })
    
    print(f"Generated {len(insights)} raw insights from market opportunity analysis.")
    return insights

def analyze_feature_recommendations(df: pd.DataFrame) -> list:
    """
    Recommends top 3 features for ALL categories with sufficient data.
    """
    print("Analyzing data for feature and category recommendations...")
    insights = []
    df_cleaned = df.dropna(subset=['Genres', 'Category', 'Installs']).copy()

    # EXPANSION: Analyze all categories with a significant number of apps (e.g., > 50).
    category_counts = df_cleaned['Category'].value_counts()
    valid_categories = category_counts[category_counts > 50].index

    for category in valid_categories:
        category_apps = df_cleaned[df_cleaned['Category'] == category]
        top_quartile_threshold = category_apps['Installs'].quantile(0.75)
        successful_apps = category_apps[category_apps['Installs'] >= top_quartile_threshold]

        if successful_apps.empty:
            continue
            
        all_genres = successful_apps['Genres'].str.split(';').explode()
        genre_counts = Counter(all_genres)
        
        # Clean the main category name from the genre list
        category_name_cleaned = category.upper().replace('_', ' ')
        for genre_key in list(genre_counts.keys()):
            if genre_key.upper() == category_name_cleaned:
                del genre_counts[genre_key]
        
        if not genre_counts:
            continue
            
        # EXPANSION: Get the top 3 most common genres/features.
        for feature, frequency in genre_counts.most_common(3):
            insights.append({
                'type': 'feature_recommendation',
                'category': category,
                'recommended_feature': feature,
                'feature_frequency': frequency,
                'successful_app_sample_size': len(successful_apps)
            })

    print(f"Generated {len(insights)} raw insights from feature recommendations.")
    return insights

