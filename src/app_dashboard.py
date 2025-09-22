# src/app_dashboard.py
# Author: Manak Chand Choudhary
# Date: 21 September 2025
# Description: This script creates a user-friendly web dashboard for the App Market
#              Intelligence System using Streamlit. It displays the executive report
#              and provides an interactive chat interface to the query engine.

import streamlit as st
import os
import sys
import glob
import time

# --- Path Correction ---
# Add the 'src' directory to the Python path to allow for absolute imports
# This must be done before importing from our custom packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from phase4.query_engine import QueryEngine

# --- Configuration ---
REPORTS_DIR = os.path.join('generated_files', 'reports')

# --- Caching ---
# Cache the QueryEngine to prevent reloading the model on every interaction
@st.cache_resource
def load_engine():
    """Loads the QueryEngine and caches it."""
    engine = QueryEngine()
    if not engine.is_ready():
        st.error("Could not initialize the Query Engine. Please ensure the insight files from Phase 2 exist.")
        return None
    return engine

# --- UI Helper Functions ---
def response_generator(text: str, speed: int = 50):
    """Yields words from a text to simulate a streaming response for st.write_stream."""
    tokens = text.split()
    for token in tokens:
        yield token + " "
        time.sleep(1 / speed)

# --- Main Application ---

# Set page title and layout
st.set_page_config(
    page_title="App Market Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar ---
with st.sidebar:
    st.image("https://www.gstatic.com/mobilesdk/160503_mobilesdk/logo/2x/firebase_28.png", width=70)
    st.title("App Success Predictor")
    st.info("This dashboard is the final product of an end-to-end AI-powered market intelligence system. It provides strategic insights and a conversational AI to explore the app market.")
    st.markdown("---")
    st.header("Project Phases")
    st.markdown("""
    - **Phase 1:** Data Collection & Integration
    - **Phase 2:** AI-Powered Insight Generation
    - **Phase 3:** Automated Report Generation
    - **Phase 4:** Intelligent Query System
    """)
    st.markdown("---")
    
    # --- Temporary Debugging ---
    # This section checks if the Streamlit secret is loaded correctly.
    st.subheader("🛠️ Debug Info")
    api_key_from_secrets = os.getenv("GEMINI_API_KEY")
    if api_key_from_secrets:
        st.success("GEMINI_API_KEY found in secrets!")
        st.code(f"Key Preview: ...{api_key_from_secrets[-4:]}")
    else:
        st.error("GEMINI_API_KEY not found in secrets.")
    # --- End of Debugging Section ---

    st.markdown("---")
    st.write("Built with Gemini & Streamlit.")

# Title for the dashboard
st.title("🚀 AI-Powered App Market Intelligence Dashboard")
st.markdown("Welcome! This dashboard provides AI-driven insights and an interactive query system to help you navigate the mobile app market.")

# Load the query engine
engine = load_engine()

if engine:
    # Create tabs for different sections
    tab1, tab2 = st.tabs(["📊 Executive Intelligence Report", "💬 Interactive Query System"])

    # --- Tab 1: Executive Report ---
    with tab1:
        st.header("Latest Executive Report")
        
        try:
            report_files = glob.glob(os.path.join(REPORTS_DIR, '*.md'))
            if not report_files:
                st.warning("No executive reports found. Please run the Phase 3 report generator first.", icon="⚠️")
            else:
                latest_report = max(report_files, key=os.path.getctime)
                st.info(f"Displaying the latest report: **{os.path.basename(latest_report)}**", icon="📄")
                
                with open(latest_report, 'r', encoding='utf-8') as f:
                    report_content = f.read()
                
                with st.expander("Click to view the full report", expanded=True):
                    st.markdown(report_content)
        except Exception as e:
            st.error(f"An error occurred while trying to load the report: {e}", icon="🔥")

    # --- Tab 2: Interactive Query System ---
    with tab2:
        st.header("Ask a Question About the App Market")
        st.markdown("Interact with our AI to get specific answers based on the generated market insights. Here are some examples to get you started:")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("What's the best price for a game?"):
                st.session_state.user_query = "What's the best price for a game?"
        with col2:
            if st.button("Which app category is underserved?"):
                st.session_state.user_query = "Which app category has the highest opportunity?"
        with col3:
            if st.button("How do I get more installs?"):
                st.session_state.user_query = "How do I get more installs?"
        
        # New section for all sample queries
        with st.expander("See a full list of sample queries for testing"):
            st.subheader("Success Factor Queries")
            st.code("""
- What is the connection between user reviews and downloads?
- Do high ratings actually matter for getting more installs?
- Give me the most important factor for app success.
- Summarize the impact of user sentiment on app performance.
- How can I improve my app's visibility?
            """, language=None)

            st.subheader("Pricing Strategy Queries")
            st.code("""
- What is the best price for a game?
- How much should I charge for a medical app?
- Are family apps more successful if they are expensive?
- Show me pricing recommendations for productivity or tools.
- Which app category makes the most money at a low price point?
            """, language=None)

            st.subheader("Market Opportunity Queries")
            st.code("""
- Which app categories have the highest potential?
- Show me an untapped market.
- Is the 'News and Magazines' category a good opportunity?
- Where is the competition low but the demand high?
- Generate a market entry strategy for an underserved category.
            """, language=None)

            st.subheader("Feature Recommendation Queries")
            st.code("""
- What kind of features should I add to a new game?
- I'm building a family app. What features are popular?
- How can I make my lifestyle app more engaging?
- What is the most common secondary genre for successful games?
            """, language=None)
            
            st.subheader("Advanced & Combined Queries")
            st.code("""
- Generate a complete launch strategy for a new fitness app.
- Summarize the key differences in strategy between a game and a medical app.
- What are the top 3 things I should focus on to make my new app successful?
- Give me a 30-day action plan for a new app in the 'TOOLS' category.
- Based on the data, what is the biggest risk I should be aware of when launching a new app?
            """, language=None)

        st.markdown("---")

        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you with your app market strategy today?"}]

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
                st.markdown(message["content"])

        # Process user input from chat or buttons
        if prompt := st.chat_input("What would you like to know?") or st.session_state.get("user_query"):
            st.session_state.user_query = None # Reset button query
            
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)

            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Analyzing insights..."):
                    response = engine.answer_query(prompt)
                    st.write_stream(response_generator(response, speed=50))
            
            st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.error("Dashboard could not be loaded. Please check the console for errors related to the Query Engine initialization.", icon="🚨")

