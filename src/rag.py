# src/rag.py

import os
from typing import Optional

from langchain_community.vectorstores import Chroma
# We will import the initialized embedding LLM from our llm module
from langchain_core.vectorstores import VectorStoreRetriever # Standard retriever type hint

import config # Import configuration
import llm # Import LLM initializations

# --- Initialize the Retriever ---
retriever: Optional[VectorStoreRetriever] = None # Use Optional for type hinting
vector_store = None

print("--- Initializing Retriever Components ---")

# First, check if the embedding LLM was successfully initialized
if llm.embedding_llm is None:
    print("Retriever initialization skipped: Embedding LLM not initialized.")
elif not os.path.exists(config.PERSIST_DIRECTORY):
    # IMPORTANT: This directory must be created by running build_vector_store.py first.
    print(f"*** ERROR: Vector store directory not found at '{config.PERSIST_DIRECTORY}'. ***")
    print("Please run the 'build_vector_store.py' script to create the vector store before starting the server.")
    # Retriever remains None
else:
    try:
        print(f"Loading vector store from: {config.PERSIST_DIRECTORY}")
        # Initialize the Chroma vector store using the path and the embedding function
        # Note: LangChainDeprecationWarning might show up, the new way is langchain-chroma
        # but this depends on your installed version. Using the community import for now.
        vector_store = Chroma(
            persist_directory=config.PERSIST_DIRECTORY,
            embedding_function=llm.embedding_llm # Use the initialized embedding LLM
        )
        print("Vector store loaded.")

        # Create a retriever instance from the vector store
        # You can configure search type and k here (e.g., k=5 for top 5 results)
        retriever = vector_store.as_retriever(
            search_type="similarity", # or "mmr"
            search_kwargs={"k": 5}    # Number of documents to retrieve
        )
        print(f"Retriever initialized with k={retriever.search_kwargs.get('k', 'N/A')}.")

    except Exception as e:
        print(f"*** ERROR initializing Chroma or Retriever: {e} ***")
        import traceback
        traceback.print_exc()
        retriever = None # Ensure retriever is None on failure
        vector_store = None


# Export the retriever instance for other modules to use
# It will be None if initialization failed.
__all__ = ['retriever']