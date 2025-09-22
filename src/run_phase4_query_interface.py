# src/run_phase4_query_interface.py
# Author: Manak Chand Choudhary
# Date: 21 September 2025
# Description: This is the main script to run the Phase 4 Intelligent Query System.
#              It provides a command-line interface (CLI) for users to ask natural
#              language questions about the insights generated in Phase 2.

import os
import sys

# --- Path Correction ---
# Add the 'src' directory to the Python path to allow for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from phase4.query_engine import QueryEngine

def main():
    """Main function to run the command-line query interface."""
    print("\n====== Welcome to the AI-Powered App Market Intelligence Query System ======")
    
    # Initialize the query engine, which loads the insights into memory
    engine = QueryEngine()
    if not engine.is_ready():
        print("Could not initialize the query engine. Exiting.")
        return

    print("Type your questions below. For example: 'What are the top success factors for gaming apps?'")
    print("Type 'exit' or 'quit' to end the session.")
    print("-------------------------------------------------------------------------")

    while True:
        try:
            # Get user input
            query = input("Ask a question: ").strip()

            if query.lower() in ['exit', 'quit']:
                print("\nThank you for using the Intelligence Query System. Goodbye!")
                break
            
            if not query:
                continue

            # Get the AI-powered answer
            print("\nThinking...")
            answer = engine.answer_query(query)
            
            print("\n---------- Answer ----------")
            print(answer)
            print("--------------------------\n")

        except KeyboardInterrupt:
            print("\nSession ended by user. Goodbye!")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

if __name__ == '__main__':
    main()
