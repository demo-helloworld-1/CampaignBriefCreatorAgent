# src/llm.py

from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
import config # Import our configuration module

# --- Initialize the Chat LLM for agents/supervisor ---
chat_llm = None
# Check if all required chat config variables are set
if config.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME and config.AZURE_OPENAI_CHAT_ENDPOINT and config.OPENAI_API_KEY_CHAT:
    try:
        chat_llm = AzureChatOpenAI(
            model=config.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME, # Use deployment name from config
            api_version=config.OPENAI_API_VERSION_CHAT, # Use chat-specific version
            azure_endpoint=config.AZURE_OPENAI_CHAT_ENDPOINT, # Use chat-specific endpoint
            api_key=config.OPENAI_API_KEY_CHAT, # Use chat-specific key
            # temperature=0 # Consider setting temperature for more deterministic output in agents
        )
        print("AzureChatOpenAI LLM initialized successfully.")
    except Exception as e:
        print(f"*** ERROR initializing AzureChatOpenAI LLM: {e} ***")
        import traceback
        traceback.print_exc()
        chat_llm = None # Ensure it's None on failure
else:
    print("Warning: Required AzureChatOpenAI configuration missing. Chat LLM not initialized.")


# --- Initialize the Embedding LLM for RAG ---
embedding_llm = None
# Check if all required embedding config variables are set
if config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME and config.AZURE_OPENAI_EMBEDDING_ENDPOINT and config.OPENAI_API_KEY_EMBEDDING:
    try:
        embedding_llm = AzureOpenAIEmbeddings(
            model=config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME, # Use deployment name from config
            openai_api_version=config.OPENAI_API_VERSION_EMBEDDING, # Use embedding-specific version
            azure_endpoint=config.AZURE_OPENAI_EMBEDDING_ENDPOINT, # Use embedding-specific endpoint
            api_key=config.OPENAI_API_KEY_EMBEDDING, # Use embedding-specific key
            chunk_size=1 # This chunk_size is for batching embeddings, not text splitting
        )
        print("AzureOpenAIEmbeddings LLM initialized successfully.")
    except Exception as e:
        print(f"*** ERROR initializing AzureOpenAIEmbeddings LLM: {e} ***")
        import traceback
        traceback.print_exc()
        embedding_llm = None # Ensure it's None on failure
else:
    print("Warning: Required AzureOpenAIEmbeddings configuration missing. Embedding LLM not initialized.")


# Export the initialized LLM objects
# If initialization failed, they will be None.
__all__ = ['chat_llm', 'embedding_llm']