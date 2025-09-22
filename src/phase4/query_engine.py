# src/phase4/query_engine.py
# Author: Gemini
# Date: 21 September 2025
# Description: This module contains the core logic for the intelligent query system.
#              It implements an ADVANCED RAG (Retrieval-Augmented Generation) pipeline:
#              1. Loads the insight database and creates vector embeddings.
#              2. Retrieves relevant insights using semantic search with a FAISS index.
#              3. Augments a prompt with the retrieved context.
#              4. Generates a final, grounded answer using an LLM.

import json
import os
import re
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Import the LLM handler from Phase 2
from phase2.llm_handler import query_llm

# --- Configuration ---
OUTPUT_DIR = 'generated_files'
INSIGHTS_FILE = os.path.join(OUTPUT_DIR, 'generated_insights.json')
EMBEDDING_MODEL = 'all-MiniLM-L6-v2' # A popular, lightweight model for embeddings

class QueryEngine:
    def __init__(self):
        """Initializes the engine by loading insights, creating embeddings, and building a search index."""
        self.insights = self._load_insights()
        if self.insights:
            print("Initializing semantic search engine...")
            self.model = SentenceTransformer(EMBEDDING_MODEL)
            self.index, self.insight_embeddings = self._build_faiss_index()
            print("Semantic search engine is ready.")

    def _load_insights(self) -> list:
        """Loads the insights from the JSON file."""
        try:
            with open(INSIGHTS_FILE, 'r') as f:
                data = json.load(f)
            print(f"Successfully loaded {len(data.get('insights', []))} insights into the knowledge base.")
            return data.get('insights', [])
        except FileNotFoundError:
            print(f"Error: Knowledge base file not found at {INSIGHTS_FILE}.")
            print("Please run the Phase 2 Insight Engine first.")
            return []
        except json.JSONDecodeError:
            print(f"Error: Could not decode the JSON from {INSIGHTS_FILE}.")
            return []
    
    def _build_faiss_index(self):
        """Creates vector embeddings for all insights and builds a FAISS index for fast search."""
        # Create a combined text for each insight to be embedded
        insight_texts = [f"{i.get('insight_text', '')} {' '.join(i.get('tags', []))}" for i in self.insights]
        
        # Generate embeddings for all insight texts
        embeddings = self.model.encode(insight_texts, convert_to_tensor=False)
        
        # Normalize embeddings for cosine similarity search
        faiss.normalize_L2(embeddings)
        
        # Build the FAISS index
        embedding_dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(embedding_dimension) # IP (Inner Product) is equivalent to cosine similarity on normalized vectors
        index.add(embeddings)
        
        return index, embeddings

    def is_ready(self) -> bool:
        """Checks if the engine has successfully loaded insights and the index."""
        return bool(self.insights) and hasattr(self, 'index')

    def _retrieve_relevant_insights(self, query: str, top_k: int = 5) -> list:
        """
        Retrieves the most relevant insights using semantic search.
        This is the upgraded 'Retrieval' step in RAG.
        """
        # Create an embedding for the user's query
        query_embedding = self.model.encode([query], convert_to_tensor=False)
        faiss.normalize_L2(query_embedding)

        # Search the FAISS index for the most similar insights
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Return the original insight dictionaries for the top results
        return [self.insights[i] for i in indices[0]]

    def answer_query(self, query: str) -> str:
        """
        Answers a user's query using the advanced RAG pipeline.
        """
        # 1. Retrieve relevant context using semantic search
        relevant_insights = self._retrieve_relevant_insights(query)
        
        if not relevant_insights:
            return "I could not find any specific insights related to your query. Please try rephrasing your question."

        # 2. Augment the prompt with the retrieved context
        context = ""
        for insight in relevant_insights:
            context += f"- Insight: {insight['insight_text']}\n"
            if insight.get('recommendations'):
                context += f"  - Recommendations: {' '.join(insight['recommendations'])}\n\n"

        prompt = f"""
        You are an AI assistant for a mobile app market intelligence platform.
        Your task is to answer the user's question based *only* on the context provided below.
        Do not use any external knowledge. If the context does not contain the answer, say so.

        Context from the knowledge base:
        ---
        {context}
        ---

        User's Question: "{query}"

        Based on the provided context, what is the answer?
        """
        
        # 3. Generate the final answer
        answer = query_llm(prompt)
        
        if not answer:
            return "There was an issue generating an AI response. Please check your API key and try again."
            
        return answer

