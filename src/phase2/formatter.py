# src/phase2/formatter.py
# Author: Manak Chand Choudhary
# Date: 21 September 2025
# Description: This module formats raw analytical findings into the structured JSON schema.
#              It now integrates with an LLM for dynamic text generation, with a fallback
#              to static templates if the LLM call fails.

from datetime import datetime
from .llm_handler import generate_llm_insight # Import the new LLM handler

def format_insight(raw_insight: dict, insight_index: int) -> dict:
    """
    Formats a raw analytical finding, using an LLM for text and falling back to templates.
    """
    insight_id = f"INSIGHT_{str(insight_index).zfill(3)}"
    timestamp = datetime.now().isoformat()
    
    # --- LLM Integration ---
    # Attempt to generate the insight text and recommendations using the LLM
    llm_generated_content = generate_llm_insight(raw_insight)
    
    # Dispatch to the correct formatting template based on the insight type
    if raw_insight['type'] == 'correlation':
        formatted_insight = _format_correlation_insight(raw_insight, llm_generated_content)
    elif raw_insight['type'] == 'rating_impact':
        formatted_insight = _format_rating_impact_insight(raw_insight, llm_generated_content)
    elif raw_insight['type'] == 'pricing_optimization':
        formatted_insight = _format_pricing_insight(raw_insight, llm_generated_content)
    elif raw_insight['type'] == 'market_opportunity':
        formatted_insight = _format_market_opportunity_insight(raw_insight, llm_generated_content)
    elif raw_insight['type'] == 'feature_recommendation':
        formatted_insight = _format_feature_recommendation_insight(raw_insight, llm_generated_content)
    else:
        return {}

    # Add common fields to the formatted insight
    formatted_insight["insight_id"] = insight_id
    formatted_insight["timestamp"] = timestamp
    
    return formatted_insight

# --- Formatting Templates (Now with LLM integration and fallbacks) ---

def _format_correlation_insight(raw_insight: dict, llm_content: dict | None) -> dict:
    """Template for correlation insights."""
    insight_text = (llm_content['insight_text'] if llm_content else
                    f"There is a strong positive correlation between an app's {raw_insight['secondary_metric']} and its total number of {raw_insight['primary_metric']}.")
    recommendations = (llm_content['recommendations'] if llm_content else
                       [f"Focus on strategies to improve {raw_insight['secondary_metric']} to drive more installs.", "Monitor these metrics closely post-launch."])

    return {
        "category": "success_factors",
        "insight_text": insight_text,
        "supporting_data": {
            "sample_size": int(raw_insight['sample_size']),
            "correlation_strength": round(float(raw_insight['correlation_value']), 2),
            "statistical_significance": "N/A (pending deeper analysis)"
        },
        "confidence_score": 0.95 if llm_content else 0.85,
        "business_impact": "high",
        "actionability": "immediate",
        "recommendations": recommendations,
        "tags": ["success_factors", "correlation", raw_insight['secondary_metric'].lower()]
    }
    
def _format_rating_impact_insight(raw_insight: dict, llm_content: dict | None) -> dict:
    """Template for rating impact insights."""
    multiple = round(float(raw_insight['install_multiple']), 1)
    insight_text = (llm_content['insight_text'] if llm_content else
                    f"Apps with a user rating of {raw_insight['threshold']} or higher have, on average, {multiple}x more installs than lower-rated apps.")
    recommendations = (llm_content['recommendations'] if llm_content else
                       [f"Prioritize user feedback and app quality to maintain a rating above {raw_insight['threshold']}.", "Implement a proactive review management strategy."])
    
    return {
        "category": "success_factors",
        "insight_text": insight_text,
        "supporting_data": {
            "sample_size": int(raw_insight['sample_size']),
            "comparison": f"Avg installs for >= {raw_insight['threshold']} apps: {int(raw_insight['avg_installs_high']):,}",
            "comparison_base": f"Avg installs for < {raw_insight['threshold']} apps: {int(raw_insight['avg_installs_low']):,}"
        },
        "confidence_score": 0.98 if llm_content else 0.90,
        "business_impact": "high",
        "actionability": "immediate",
        "recommendations": recommendations,
        "tags": ["success_factors", "rating_impact", "user_sentiment"]
    }

def _format_pricing_insight(raw_insight: dict, llm_content: dict | None) -> dict:
    """Template for pricing optimization insights."""
    insight_text = (llm_content['insight_text'] if llm_content else
                    f"For the '{raw_insight['category']}' category, the price range of {raw_insight['optimal_price_range']} correlates with the highest average user ratings, suggesting a strong value proposition at this price point.")
    recommendations = (llm_content['recommendations'] if llm_content else
                       [f"Consider pricing new '{raw_insight['category']}' apps within the {raw_insight['optimal_price_range']} range to maximize perceived value.", "Analyze competitor pricing within this specific tier."])

    return {
        "category": "pricing_strategy_optimization",
        "app_category": raw_insight['category'],
        "insight_text": insight_text,
        "supporting_data": {
            "sample_size": int(raw_insight['sample_size']),
            "optimal_price_range": raw_insight['optimal_price_range'],
            "avg_rating_in_range": round(float(raw_insight['avg_rating_in_range']), 2)
        },
        "confidence_score": 0.92 if llm_content else 0.82,
        "business_impact": "medium",
        "actionability": "strategic",
        "recommendations": recommendations,
        "tags": ["pricing", "optimization", raw_insight['category'].lower()]
    }

def _format_market_opportunity_insight(raw_insight: dict, llm_content: dict | None) -> dict:
    """Template for market opportunity insights."""
    insight_text = (llm_content['insight_text'] if llm_content else
                    f"The '{raw_insight['category']}' category shows a high ratio of average installs to the number of competing apps, indicating a potential market opportunity.")
    recommendations = (llm_content['recommendations'] if llm_content else
                       [f"Conduct deeper market research into the '{raw_insight['category']}' category.", f"Identify feature gaps not being met by the {int(raw_insight['app_count'])} existing apps."])

    return {
        "category": "market_opportunity_assessment",
        "app_category": raw_insight['category'],
        "insight_text": insight_text,
        "supporting_data": {
            "app_count_in_category": int(raw_insight['app_count']),
            "avg_installs_in_category": f"{int(raw_insight['avg_installs']):,}",
            "opportunity_score": round(float(raw_insight['opportunity_score']), 2)
        },
        "confidence_score": 0.88 if llm_content else 0.78,
        "business_impact": "high",
        "actionability": "strategic",
        "recommendations": recommendations,
        "tags": ["market_opportunity", "untapped_market", raw_insight['category'].lower()]
    }

def _format_feature_recommendation_insight(raw_insight: dict, llm_content: dict | None) -> dict:
    """Template for feature recommendation insights."""
    insight_text = (llm_content['insight_text'] if llm_content else
                    f"Within the '{raw_insight['category']}' category, top apps commonly feature '{raw_insight['recommended_feature']}'.")
    recommendations = (llm_content['recommendations'] if llm_content else
                       [f"Consider adding features related to '{raw_insight['recommended_feature']}' to '{raw_insight['category']}' apps.", "Analyze how competitors implement these features."])
    
    return {
        "category": "feature_and_category_recommendations",
        "app_category": raw_insight['category'],
        "insight_text": insight_text,
        "supporting_data": {
            "successful_app_sample_size": int(raw_insight['successful_app_sample_size']),
            "recommended_feature": raw_insight['recommended_feature'],
            "feature_frequency_in_top_apps": int(raw_insight['feature_frequency']),
        },
        "confidence_score": 0.85 if llm_content else 0.75,
        "business_impact": "medium",
        "actionability": "strategic",
        "recommendations": recommendations,
        "tags": ["feature_recommendation", "product_development", raw_insight['category'].lower(), raw_insight['recommended_feature'].lower().replace(' & ', '_and_')]
    }

