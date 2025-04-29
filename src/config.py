# src/config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Azure OpenAI Configuration (Separate for Chat and Embeddings) ---
# Use os.getenv with default values or raise errors if required variables are missing

# General Config (might be same for both accounts, but can be overridden)
OPENAI_API_TYPE = os.getenv("OPENAI_API_TYPE", "azure")
# API version is usually tied to the service endpoint version,
# but we'll allow separate vars if needed, defaulting to a common one
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION", "2024-02-01")
OPENAI_API_VERSION_CHAT = os.getenv("OPENAI_API_VERSION_CHAT", OPENAI_API_VERSION) # Override if different
OPENAI_API_VERSION_EMBEDDING = os.getenv("OPENAI_API_VERSION_EMBEDDING", OPENAI_API_VERSION) # Override if different


# Chat Model Configuration
AZURE_OPENAI_CHAT_ENDPOINT = os.getenv("AZURE_OPENAI_CHAT_ENDPOINT")
OPENAI_API_KEY_CHAT = os.getenv("OPENAI_API_KEY_CHAT")
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME") # e.g., "gpt-4o-mini" or your deployment name

# Embedding Model Configuration
AZURE_OPENAI_EMBEDDING_ENDPOINT = os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT")
OPENAI_API_KEY_EMBEDDING = os.getenv("OPENAI_API_KEY_EMBEDDING")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME") # e.g., "text-embedding-ada-002" or your deployment name


# --- Application Paths and Constants ---
# Define paths relative to the project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

DATA_DIR = os.path.join(PROJECT_ROOT, "Data")
METADATA_DIR = os.path.join(PROJECT_ROOT, "metadata")
LOGOS_DIR = os.path.join(PROJECT_ROOT, ".logos") # Use the hidden dir name
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
PERSIST_DIRECTORY = os.path.join(PROJECT_ROOT, "vector_store_db") # For Chroma DB

TEMPLATE_FILENAME = "CampaignBriefCreationTemplate.docx"
OUTPUT_FILENAME = "Final_Campaign_Brief.docx"

TEMPLATE_PATH = os.path.join(DATA_DIR, TEMPLATE_FILENAME)
OUTPUT_PATH = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)


# --- Ensure directories exist ---
# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
# Note: PERSIST_DIRECTORY is typically created by the build_vector_store.py script.
# os.makedirs(PERSIST_DIRECTORY, exist_ok=True) # Don't create here, let build script handle


# --- Validation (Optional but Recommended) ---
# Add checks to ensure critical variables are set
required_chat_vars = [
    "AZURE_OPENAI_CHAT_ENDPOINT",
    "OPENAI_API_KEY_CHAT",
    "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"
]
required_embedding_vars = [
    "AZURE_OPENAI_EMBEDDING_ENDPOINT",
    "OPENAI_API_KEY_EMBEDDING",
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"
]

missing_vars = []
for var in required_chat_vars:
    if not os.getenv(var):
        missing_vars.append(var)
for var in required_embedding_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print(f"Warning: The following required environment variables are not set: {', '.join(missing_vars)}")
    # In a production app, you might want to raise an error here
    # raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")


print("Configuration loaded.")
# print specific endpoint details for clarity
print(f"Chat Endpoint: {AZURE_OPENAI_CHAT_ENDPOINT} (Deployment: {AZURE_OPENAI_CHAT_DEPLOYMENT_NAME})")
print(f"Embedding Endpoint: {AZURE_OPENAI_EMBEDDING_ENDPOINT} (Deployment: {AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME})")
print(f"Template Path: {TEMPLATE_PATH}")
print(f"Output Path: {OUTPUT_PATH}")
print(f"Vector Store Path: {PERSIST_DIRECTORY}")