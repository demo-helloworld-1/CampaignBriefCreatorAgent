# src/tools/retrieve_data.py

import os
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
import traceback # Import traceback

# Use the initialized retriever instance from src/rag
from src.rag import retriever

print("--- Defining retrieve_data tool ---")

# --- Pydantic Schema for Tool Arguments (Copied from app copy.py) ---
# This matches the definition in app copy.py
class RetrieveDataInput(BaseModel):
    query: str = Field(description="The specific query or topic to search for relevant information in indexed data (e.g., past campaign data, company logo metadata).")

# --- Core Python Function (Copied from app copy.py) ---
# Strictly copied the function logic as it was working
def retrieve_data_tool_func(query: str) -> str:
    """
    Searches the indexed data vector store for chunks relevant to the query
    and returns their concatenated text content. Useful for retrieving
    relevant campaign history or specific metadata like image paths.
    """
    print(f"\n--- Running retrieve_data_tool_func ---")
    print(f"Retrieving data for query: '{query}'")

    # Check if retriever was successfully initialized in src.rag
    if retriever is None:
        error_msg = "Error: RAG retriever is not initialized. Cannot perform retrieval."
        print(error_msg)
        # Return a specific error message indicating RAG is not available
        return f"Retrieval Failed: {error_msg}"


    try:
        # Use the initialized retriever instance
        # Invoke the retriever with the query string
        relevant_docs = retriever.invoke(query)

        if not relevant_docs:
            print("No relevant documents found for this query.")
            # Return a message indicating no relevant info found
            return "No relevant information found in past campaign data for the query."

        print(f"Retrieved {len(relevant_docs)} relevant document chunks.")
        # Concatenate the page content of the retrieved documents, separated for clarity
        retrieved_context = "\n\n---\n\n".join([doc.page_content for doc in relevant_docs])
        print("Returning concatenated relevant context.")
        # print("DEBUG: Retrieved context preview:", retrieved_context[:500] + "...") # Optional: preview

        return retrieved_context

    except Exception as e:
        error_msg = f"An error occurred during data retrieval for query '{query}': {e}"
        print(error_msg)
        traceback.print_exc() # Print retrieval error traceback
        # Return an error message indicating retrieval failed
        return f"Retrieval Failed: {error_msg}"


# --- Create the LangChain StructuredTool (Copied from app copy.py) ---
retrieve_data_tool = StructuredTool.from_function(
    func=retrieve_data_tool_func,
    name="retrieve_relevant_campaign_data",
    description="Useful for retrieving relevant text excerpts from indexed past campaign data or specific metadata (like file paths) based on a specific query.",
    args_schema=RetrieveDataInput,
    return_direct=False
)

print(f"Tool defined: {retrieve_data_tool.name}")