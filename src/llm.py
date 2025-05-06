# src/llm.py

import os
# Assuming the primary LLM class used in app copy.py was AzureChatOpenAI from langchain_openai
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
# Import config for environment variables
from src.config import (
    AZURE_OPENAI_CHAT_ENDPOINT,
    OPENAI_API_KEY_CHAT,
    AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,
    OPENAI_API_VERSION_CHAT,
    AZURE_OPENAI_EMBEDDING_ENDPOINT,
    OPENAI_API_KEY_EMBEDDING,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME,
    OPENAI_API_VERSION_EMBEDDING # Use the versions from config
)

print("Initializing Azure OpenAI LLM and Embeddings...")

# --- Initialize Azure OpenAI Chat Model ---
llm = None # Initialize to None
try:
    # Check config variables
    if not all([AZURE_OPENAI_CHAT_ENDPOINT, OPENAI_API_KEY_CHAT, AZURE_OPENAI_CHAT_DEPLOYMENT_NAME]):
         print("Warning: Chat model configuration is incomplete in config. Skipping chat model initialization.")
    else:
        # Initialize using config variables
        llm = AzureChatOpenAI(
            azure_endpoint=AZURE_OPENAI_CHAT_ENDPOINT,
            api_key=OPENAI_API_KEY_CHAT,
            model=AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,
            api_version=OPENAI_API_VERSION_CHAT, # Use API version from config
            # deployment_name=AZURE_OPENAI_CHAT_DEPLOYMENT_NAME # Can add if needed
        )
        print(f"AzureChatOpenAI initialized successfully with deployment/model: {AZURE_OPENAI_CHAT_DEPLOYMENT_NAME}.")

except Exception as e:
    print(f"\n*** ERROR initializing AzureChatOpenAI: {e} ***")
    import traceback
    traceback.print_exc()
    llm = None # Ensure it's None if initialization fails


# --- Initialize Azure OpenAI Embeddings Model ---
embeddings = None # Initialize to None
try:
    # Check config variables
    if not all([AZURE_OPENAI_EMBEDDING_ENDPOINT, OPENAI_API_KEY_EMBEDDING, AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME]):
         print("Warning: Embedding model configuration is incomplete in config. Skipping embeddings initialization.")
    else:
        # Initialize using config variables
        embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=AZURE_OPENAI_EMBEDDING_ENDPOINT,
            api_key=OPENAI_API_KEY_EMBEDDING,
            model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME,
            api_version=OPENAI_API_VERSION_EMBEDDING, # Use API version from config
            chunk_size=1 # Keep chunk_size as in original/config
            # deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME # Can add if needed
        )
        print(f"AzureOpenAIEmbeddings initialized successfully with deployment/model: {AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME}.")

except Exception as e:
     print(f"\n*** ERROR initializing AzureOpenAIEmbeddings: {e} ***")
     import traceback
     traceback.print_exc()
     embeddings = None # Ensure it's None if initialization fails


# Optional: Final check and print status
if llm is None:
    print("\n*** WARNING: AzureChatOpenAI was NOT initialized. Agent functionality will be limited. ***")
if embeddings is None:
    print("\n*** WARNING: AzureOpenAIEmbeddings was NOT initialized. RAG functionality will be impacted. ***")
# Add check if both failed - might be a critical issue
if llm is None and embeddings is None:
    print("\n*** CRITICAL WARNING: Neither LLM nor Embeddings initialized. Most functionality will fail. ***")


print("src.llm initialization attempted.")