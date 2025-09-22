🚀 AI-Powered App Store Success Predictor
This repository contains the complete source code for an end-to-end AI-powered market intelligence system. The project leverages data analytics, web scraping, and Large Language Models (LLMs) to analyze the mobile app market, generate strategic business insights, and provide an interactive query interface for decision-making.

✨ Features
This project is built in four distinct, modular phases:

Phase 1: Multi-Source Data Pipeline

Ingests and cleans app metadata and user reviews from local datasets.

Enriches the data by scraping real-time app information using the SerpApi service.

Creates a final, unified master dataset ready for analysis.

Phase 2: AI-Powered Insight Generation

Performs a comprehensive statistical analysis on the master dataset to find drivers of app success, optimal pricing strategies, market opportunities, and feature recommendations.

Integrates with the Gemini LLM to transform raw statistical findings into nuanced, human-like insights with actionable recommendations.

Generates a structured database of over 100+ insights in a JSON format.

Phase 3: Automated Report Generation

Reads the generated insights from Phase 2.

Uses a Retrieval-Augmented Generation (RAG) pipeline to create a high-level, AI-powered executive summary.

Automatically assembles a complete, professional intelligence report in Markdown format.

Phase 4: Intelligent Query System & Web Dashboard

Implements an advanced RAG pipeline using semantic search (Sentence Transformers + FAISS) to allow users to ask questions in natural language.

Provides a beautiful and intuitive web dashboard built with Streamlit to display the executive report and host the interactive chat interface.

🛠️ Tech Stack
Backend: Python

Data Manipulation: Pandas, NumPy

Web Scraping: Requests, SerpApi (google-search-results)

AI & Machine Learning:

LLM: Google Gemini

Semantic Search: sentence-transformers, faiss-cpu

Sentiment Analysis: textblob

Web Dashboard: Streamlit

⚙️ Setup and Installation Guide
Follow these steps to set up and run the project on your local machine.

1. Prerequisites
Git: You must have Git installed to clone the repository.

Python: Python 3.10 or newer is recommended.

2. Clone the Repository
Open your terminal and clone the repository to your local machine:

git clone [https://github.com/YourUsername/YourRepositoryName.git](https://github.com/YourUsername/YourRepositoryName.git)
cd YourRepositoryName

3. Set Up a Virtual Environment
It is highly recommended to use a virtual environment to manage project dependencies.

# Create a virtual environment named '.venv'
python -m venv .venv

# Activate the virtual environment
# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

4. Install Required Libraries
Install all the necessary Python packages using the provided requirements.txt file.

pip install -r requirements.txt

The script will also download a sentence transformer model on its first run, which may take a few minutes.

5. Configure API Keys
The project requires API keys for SerpApi (for data scraping) and Google Gemini (for AI insights).

Create a new file named .env in the root directory of the project.

Add your API keys to this file in the following format:

SERPAPI_KEY="your_serpapi_api_key_here"
GEMINI_API_KEY="your_google_gemini_api_key_here"

🚀 How to Run the Full Pipeline
Run the following scripts from the project's root directory in order.

Step 1: Run the Data Pipeline (Phase 1)
These two scripts will generate the final_master_app_data.csv file.

# Process local Kaggle files
python src/1_process_local_data.py

# Scrape real-time data and combine
python src/3_combine_datasets.py

Step 2: Run the Insight Engine (Phase 2)
This script uses the data from Step 1 to generate the generated_insights.json file.

python src/run_phase2_engine.py

Step 3: Generate the Executive Report (Phase 3)
This script uses the insights from Step 2 to create the final Markdown report.

python src/run_phase3_report_generator.py

Step 4: Launch the Web Dashboard
This command will start the Streamlit web server and open the interactive dashboard in your browser.

streamlit run src/app_dashboard.py

You can now interact with the dashboard to view the report and ask questions to the AI-powered query system!
