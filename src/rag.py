# src/rag.py

import os
from langchain_community.vectorstores import Chroma
# Use the initialized embeddings object from src/llm
from src.llm import embeddings
# Import configuration variables for path and search kwargs
from src.config import PERSIST_DIRECTORY, RAG_SEARCH_KWARGS # Use PERSIST_DIRECTORY from config

vector_store = None
retriever = None

print("Setting up RAG components (Chroma vector store and Retriever)...")

if embeddings is None:
    print("*** ERROR: Embeddings not initialized in src/llm.py. Cannot set up RAG retriever. ***")
else:
    # Check if the vector store directory exists *before* attempting to load
    if not os.path.exists(PERSIST_DIRECTORY):
        # The build_vector_store.py script must create this directory and populate it.
        print(f"\n*** WARNING: Vector store directory not found at '{PERSIST_DIRECTORY}'. Run build_vector_store.py first. RAG will not function. ***\n")
    else:
        try:
            # Attempt to load the existing vector store
            print(f"Attempting to load Chroma vector store from: {PERSIST_DIRECTORY}")
            vector_store = Chroma(
                persist_directory=PERSIST_DIRECTORY,
                embedding_function=embeddings # Use the initialized embeddings object
            )
            print("Chroma vector store loaded.")

            # Create the retriever instance
            # Use search kwargs from config
            retriever = vector_store.as_retriever(
                search_type="similarity", # Common search type
                search_kwargs=RAG_SEARCH_KWARGS
            )
            print(f"Retriever initialized with search kwargs: {RAG_SEARCH_KWARGS}")

            # Optional: Basic check if the store has content (requires chromadb installed)
            try:
                # Accessing internal _client might change, but is needed to check collections
                # Check if vector_store is not None before accessing _client
                if vector_store and hasattr(vector_store, '_client'):
                    collection_names = [c.name for c in vector_store._client.list_collections()]
                    if not collection_names:
                          print(f"*** WARNING: Vector store directory '{PERSIST_DIRECTORY}' found, but appears empty (no collections). Run build_vector_store.py. ***")
                    else:
                        print(f"Vector store appears to contain collections: {collection_names}.")
                else:
                    print("Note: Vector store client not available for detailed check.")

            except Exception as e:
                print(f"Note: Could not perform detailed check on vector store collections: {e}")


        except Exception as e:
            print(f"\n*** ERROR initializing Chroma vector store or retriever: {e} ***")
            import traceback
            traceback.print_exc()
            vector_store = None
            retriever = None

if retriever is None:
    print("\n*** WARNING: RAG Retriever failed to initialize. The 'retrieve_relevant_campaign_data' tool will not function. ***")
else:
    print("RAG components initialized.")