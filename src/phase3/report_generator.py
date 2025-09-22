# src/phase3/report_generator.py
# Author: Manak Chand Choudhary
# Date: 21 September 2025
# Description: This module contains the core logic for generating the final,
#              AI-powered executive intelligence report from the Phase 2 insights.

import json
from datetime import datetime

# CORRECTED: Changed to an absolute import from the project's 'src' root
from phase2.llm_handler import query_llm 

def _get_top_insights(insights: list, category: str, n: int = 5) -> list:
    """Helper function to filter and get the top N insights of a specific category."""
    filtered = [i for i in insights if i.get('category') == category]
    return sorted(filtered, key=lambda x: x.get('confidence_score', 0), reverse=True)[:n]

def _generate_executive_summary(insights: list) -> str:
    """Generates the AI-powered executive summary using the top 10 insights."""
    print("  - Generating AI-powered executive summary...")
    # Retrieve the top 10 most confident insights to use as context (RAG)
    top_insights = sorted(insights, key=lambda x: x.get('confidence_score', 0), reverse=True)[:10]
    
    insights_summary = ""
    for insight in top_insights:
        insights_summary += f"- {insight.get('insight_text', '')}\n"
        
    prompt = f"""
    As a senior market analyst, write a concise, professional executive summary based on the following key findings from an analysis of the mobile app market.
    The summary should be strategic, highlighting the most critical success factors and market opportunities.

    Key Findings:
    {insights_summary}

    Synthesize these points into a brief, high-level summary for a busy executive.
    """
    
    summary = query_llm(prompt)
    if not summary:
        return "*(AI summary generation failed. Please check API key. This is a placeholder.)*\n\nThe analysis has identified several key drivers of app success, including the strong correlation between user reviews and downloads. Strategic pricing and identifying underserved market categories are also highlighted as significant opportunities."
    return summary

def _create_success_factors_section(insights: list) -> str:
    """Creates the 'Success Factor Rankings' section of the report."""
    print("  - Creating success factors section...")
    success_factors = _get_top_insights(insights, 'success_factors', n=2)
    if not success_factors:
        return ""
        
    section_content = "### Success Factor Rankings\n"
    for i, insight in enumerate(success_factors):
        impact_score = int(insight.get('confidence_score', 0.8) * 10)
        
        # CORRECTED: Added a check to prevent an IndexError if there are not enough tags.
        tags = insight.get('tags', [])
        title = tags[1].replace('_', ' ').title() if len(tags) > 1 else "Key Finding"
        
        section_content += f"{i+1}. **{title}** - Impact Score: {impact_score}/10\n"
        section_content += f"> {insight.get('insight_text', 'N/A')}\n\n"
    return section_content

def _create_category_performance_table(insights: list) -> str:
    """Creates the 'Category Performance Analysis' markdown table."""
    print("  - Creating category performance table...")
    
    # Extract data for top categories
    market_opps = {i['app_category']: i for i in _get_top_insights(insights, 'market_opportunity_assessment', n=5)}
    pricing_insights = {i['app_category']: i for i in _get_top_insights(insights, 'pricing_strategy_optimization', n=20)}
    feature_insights = {i['app_category']: i for i in _get_top_insights(insights, 'feature_and_category_recommendations', n=20)}

    all_categories = set(market_opps.keys()) | set(pricing_insights.keys()) | set(feature_insights.keys())
    
    table = "| Category | Opportunity Score | Optimal Price | Top Feature Recommendation |\n"
    table += "|----------|-------------------|---------------|----------------------------|\n"
    
    for category in sorted(list(all_categories))[:5]: # Limit to top 5 for brevity
        opp_score = f"{market_opps[category]['supporting_data']['opportunity_score']:.0f}" if category in market_opps else "N/A"
        price = pricing_insights[category]['supporting_data']['optimal_price_range'] if category in pricing_insights else "N/A (Free focus)"
        feature = feature_insights[category]['supporting_data']['recommended_feature'] if category in feature_insights else "N/A"
        table += f"| {category} | {opp_score} | {price} | {feature} |\n"
        
    return "### Category Performance Analysis\n" + table

def _create_pricing_strategy_section(insights: list) -> str:
    """Creates the 'Pricing Strategy Recommendations' section."""
    print("  - Creating pricing strategy section...")
    pricing_insights = _get_top_insights(insights, 'pricing_strategy_optimization', n=5)
    if not pricing_insights:
        return ""

    section_content = "### Optimal Pricing by Category\n"
    for insight in pricing_insights:
        category = insight.get('app_category', 'N/A')
        price_range = insight['supporting_data'].get('optimal_price_range', 'N/A')
        section_content += f"- **{category}**: The data suggests an optimal price point in the **{price_range}** range, which correlates with the highest user satisfaction.\n"
    
    return section_content

def _create_action_plan(insights: list) -> str:
    """Uses the LLM to generate a final, prioritized action plan."""
    print("  - Generating AI-powered action plan...")
    all_recommendations = []
    for insight in insights:
        all_recommendations.extend(insight.get('recommendations', []))
        
    # De-duplicate recommendations
    unique_recommendations = "\n".join(list(set(all_recommendations)))
    
    prompt = f"""
    As a chief strategist, analyze the following list of raw recommendations from a market analysis.
    Your task is to synthesize and categorize them into a clear, prioritized action plan with three sections:
    1. Immediate Actions (Next 30 Days)
    2. Short-term Strategy (Next 3 Months)
    3. Long-term Vision (6+ Months)

    Convert the raw recommendations into a strategic to-do list in markdown format.

    Raw Recommendations:
    {unique_recommendations}
    """
    
    action_plan = query_llm(prompt)
    if not action_plan:
        return "*(AI action plan generation failed. Please check API key.)*"
    return action_plan

def generate_executive_report(insights: list) -> str:
    """
    Main function to construct the full executive report from insights.
    """
    if not insights:
        return "No insights were provided to generate a report."

    # --- 1. Generate AI Summary ---
    summary = _generate_executive_summary(insights)

    # --- 2. Build Report Sections ---
    success_factors = _create_success_factors_section(insights)
    category_performance = _create_category_performance_table(insights)
    pricing_strategy = _create_pricing_strategy_section(insights)
    action_plan = _create_action_plan(insights)

    # --- 3. Assemble the Final Report ---
    report = f"""# App Store Success Intelligence Report

**Generated on:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Analysis Coverage:** Approx. {insights[0]['supporting_data'].get('sample_size', 'N/A')} apps across Google Play Store
---
## 🎯 Executive Summary
{summary}

## 📈 Key Market Insights
{success_factors}
{category_performance}

## 💰 Pricing Strategy Recommendations
{pricing_strategy}

## 🚀 Action Plan
{action_plan}

---
*Report generated by AI-Powered App Market Intelligence System*
"""
    return report

