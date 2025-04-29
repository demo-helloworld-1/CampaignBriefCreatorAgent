from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
import os
# Import the retriever from our rag module
import sys
sys.path.append('../')

import traceback
import config # Import config for checking vector store path if needed
import rag # Import config for checking vector store path if needed
class RetrieveDataInput(BaseModel):
    """Input schema for the retrieve_relevant_campaign_data tool."""
    query: str = Field(description="The specific query or topic to search for relevant information in indexed past campaign data or metadata.")

def retrieve_data_tool_func(query: str) -> str:
    """
    Searches the indexed campaign data vector store for chunks relevant to the query
    and returns their concatenated text content. Handles cases where the retriever
    was not initialized successfully.
    """
    print(f"\n--- Running retrieve_data_tool_func ---")
    print(f"Received query: '{query}'")

    # Check if the retriever was successfully initialized in rag.py
    if rag.retriever is None:
        error_msg = "Error: RAG retriever is not initialized. Vector store may be missing or embedding LLM failed to load."
        print(error_msg)
        # Provide more context if the vector store directory is missing
        if not os.path.exists(config.PERSIST_DIRECTORY):
            error_msg += f" Vector store directory not found at '{config.PERSIST_DIRECTORY}'."
        return error_msg # Return an error message indicating the failure

    try:
        # Use the initialized retriever
        relevant_docs = rag.retriever.invoke(query)

        if not relevant_docs:
            print("No relevant documents found.")
            return "No relevant information found for the query in the indexed data."

        print(f"Retrieved {len(relevant_docs)} relevant document chunks.")
        # Concatenate the content of the retrieved documents
        retrieved_context = "\n\n---\\n\\n".join([doc.page_content for doc in relevant_docs])
        print("Returning concatenated relevant context.")
        # print(f"DEBUG Retrieved Context:\n{retrieved_context[:500]}...") # Print start for debug
        return retrieved_context

    except Exception as e:
        print(f"An error occurred during retrieval: {e}")
        

        traceback.print_exc()
        return f"An error occurred while retrieving data: {e}"


# Create the LangChain StructuredTool
retrieve_data_tool = StructuredTool.from_function(
    func=retrieve_data_tool_func,
    name="retrieve_relevant_campaign_data",
    description="Useful for retrieving relevant text excerpts from indexed past campaign data or metadata based on a specific query. Input is 'query'. Returns concatenated relevant text.",
    args_schema=RetrieveDataInput,
    return_direct=False
)

print(f"Defined tool: {retrieve_data_tool.name}")

# Optionally add the tool to __all__ for easier import in tools/__init__.py
__all__ = ["retrieve_data_tool"]