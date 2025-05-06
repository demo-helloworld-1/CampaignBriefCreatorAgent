# build_vector_store.py
# This script builds the Chroma vector store from source documents.

import os
import sys
import shutil # To remove directory if needed
import traceback # For detailed error info

# Add the src directory to the Python path so we can import from it
# This is necessary because this script is at the project root, not in src.
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'src'))

# --- Import necessary components from src ---
# Import config for paths and Azure details
from src.config import (
    PERSIST_DIRECTORY,
    DATA_DIR,
    METADATA_DIR,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME,
    AZURE_OPENAI_EMBEDDING_ENDPOINT,
    OPENAI_API_KEY_EMBEDDING,
    OPENAI_API_VERSION_EMBEDDING
)
# Import embeddings directly from src.llm or initialize here using config
# Option 1: Import initialized embeddings (requires src.llm to init on import)
# from src.llm import embeddings
# Option 2: Initialize embeddings specifically for this script using config (safer if src.llm has other side effects)
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader, DirectoryLoader  # Add more loaders if needed
from langchain.text_splitter import RecursiveCharacterTextSplitter

print("--- Starting Vector Store Build Script ---")

# --- Initialize Embeddings for this script ---
# It's often safer to initialize dependencies needed by a script within the script
# rather than relying on side effects of importing application modules.
embeddings = None
try:
    if not all([AZURE_OPENAI_EMBEDDING_ENDPOINT, OPENAI_API_KEY_EMBEDDING, AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME]):
        print("Error: Embedding model configuration is incomplete. Cannot build vector store.")
    else:
        embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=AZURE_OPENAI_EMBEDDING_ENDPOINT,
            api_key=OPENAI_API_KEY_EMBEDDING,
            model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME,
            api_version=OPENAI_API_VERSION_EMBEDDING,
            chunk_size=1 # Match chunk size used in src/llm.py or adjust as needed
        )
        print("AzureOpenAIEmbeddings initialized for building.")
except Exception as e:
    print(f"\n*** ERROR initializing AzureOpenAIEmbeddings for build script: {e} ***")
    traceback.print_exc()
    sys.exit("Embeddings initialization failed. Cannot build vector store.") # Exit if embeddings fail

if embeddings is None:
    sys.exit("Embeddings initialization failed. Cannot build vector store.")


# --- Define Data Loading and Processing ---

def load_documents(data_dir: str, metadata_dir: str) -> list:
    """Loads documents from the specified directories."""
    print(f"\nLoading documents from '{data_dir}' and '{metadata_dir}'...")
    documents = []

    # Load text files from Data directory
    if os.path.exists(data_dir):
        print(f"Loading text files from {data_dir}...")
        # Specify encoding='utf-8' when initializing TextLoader
        text_loader = DirectoryLoader(data_dir, glob="**/*.txt", loader_cls=TextLoader, loader_kwargs={'encoding': 'utf-8'}) # <--- Modified line
        try:
            documents.extend(text_loader.load())
            print(f"Loaded {len(documents)} text documents from {data_dir}.")
        except Exception as e:
            print(f"Error loading documents from {data_dir}: {e}")
            traceback.print_exc()
    else:
        print(f"Warning: Data directory not found at '{data_dir}'. No text documents loaded.")


    # Load metadata files from Metadata directory
    if os.path.exists(metadata_dir):
        print(f"Loading metadata files from {metadata_dir}...")
        # Specify encoding='utf-8' when initializing TextLoader for metadata too
        metadata_loader = DirectoryLoader(metadata_dir, glob="**/*.txt", loader_cls=TextLoader, loader_kwargs={'encoding': 'utf-8'}) # <--- Modified line
        try:
            metadata_docs = metadata_loader.load()
            documents.extend(metadata_docs)
            print(f"Loaded {len(metadata_docs)} metadata documents from {metadata_dir}.")
        except Exception as e:
            print(f"Error loading documents from {metadata_dir}: {e}")
            traceback.print_exc()
    else:
        print(f"Warning: Metadata directory not found at '{metadata_dir}'. No metadata documents loaded.")

    if not documents:
        print("No documents were loaded from either directory.")

    return documents

def split_documents(documents: list) -> list:
    """Splits documents into chunks."""
    print("\nSplitting documents into chunks...")
    # Configure the text splitter - adjust chunk_size and chunk_overlap as needed
    # based on your embeddings model and the nature of your data.
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")
    return chunks

def build_vector_store(chunks: list, embeddings: AzureOpenAIEmbeddings, persist_directory: str):
    """Builds and persists the Chroma vector store."""
    if not chunks:
        print("No chunks to process. Skipping vector store creation.")
        return

    print(f"\nBuilding and persisting vector store to '{persist_directory}'...")

    # Clean up existing vector store directory if it exists
    if os.path.exists(persist_directory):
        print(f"Existing vector store found at '{persist_directory}'. Removing...")
        try:
            shutil.rmtree(persist_directory)
            print("Existing vector store removed.")
        except OSError as e:
            print(f"Error removing existing vector store directory {persist_directory}: {e}")
            traceback.print_exc()
            sys.exit("Failed to clear existing vector store. Aborting build.")

    try:
        # Create the vector store from the document chunks and embeddings
        # Chroma will create the directory if it doesn't exist
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=persist_directory
        )
        # persist() is called implicitly by from_documents with persist_directory
        print("Chroma vector store built and persisted successfully.")
        print(f"Vector store saved to: {os.path.abspath(persist_directory)}")

    except Exception as e:
        print(f"\n*** ERROR building or persisting Chroma vector store: {e} ***")
        traceback.print_exc()
        sys.exit("Vector store build failed.")


# --- Main Execution ---
if __name__ == "__main__":
    print("Starting vector store build process...")

    # Check if embeddings were successfully initialized
    if embeddings is None:
        sys.exit("Embeddings not available. Aborting build.")

    # 1. Load documents
    all_documents = load_documents(DATA_DIR, METADATA_DIR) 

    # 2. Split documents into chunks
    if all_documents:
        all_chunks = split_documents(all_documents)
    else:
        all_chunks = []
        print("No documents loaded, no chunks created.")

    # 3. Build and persist the vector store
    build_vector_store(all_chunks, embeddings, PERSIST_DIRECTORY)

    print("\nVector Store Build Script Finished.")
    if os.path.exists(PERSIST_DIRECTORY):
        print("Vector store directory exists. Build likely successful.")
    else:
        print("Vector store directory was NOT created. Build failed.")