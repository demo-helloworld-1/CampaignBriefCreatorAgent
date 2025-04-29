# src/__init__.py

# This file marks the 'src' directory as a Python package.
# It can also be used to initialize package-level settings or import key components
# to make them easily accessible.

print("Initializing src package...")

# Import key modules to trigger their initialization logic
# The order is important due to dependencies: config -> llm -> rag
try:
    from . import config
    print("src.config loaded.")
except Exception as e:
    print(f"*** ERROR loading src.config: {e} ***")
    # Depending on severity, you might want to exit here or later

try:
    from . import llm
    print("src.llm initialized (LLMs created).")
except Exception as e:
    print(f"*** ERROR initializing src.llm: {e} ***")
    # LLM initialization errors are critical, subsequent steps will likely fail
    # Continue, but know that llm.chat_llm and llm.embedding_llm might be None

try:
    from . import rag
    print("src.rag initialized (Retriever created/loaded).")
except Exception as e:
    print(f"*** ERROR initializing src.rag: {e} ***")
    # RAG initialization errors mean retrieval tool will fail
    # Continue, but know that rag.retriever might be None


# Import the tools and agents sub-packages.
# This makes their contents (like all_tools list, agent objects) available under src.tools and src.agents
try:
    from . import tools
    print("src.tools package imported.")
except Exception as e:
    print(f"*** ERROR importing src.tools: {e} ***")
    # Tools won't be available

try:
    from . import agents
    print("src.agents package imported.")
except Exception as e:
    print(f"*** ERROR importing src.agents: {e} ***")
    # Agents won't be available


# You can define what gets imported when someone does 'from src import *'
# Often it's better to use specific imports like 'from src.llm import chat_llm'
# But for demonstration, we can expose some top-level components or packages:
__all__ = [
    'config',  # Contains all configuration constants
    'llm',     # Contains chat_llm and embedding_llm
    'rag',     # Contains retriever
    'tools',   # Contains all individual tool objects and the all_tools list
    'agents'   # Contains all individual agent objects
]

print("src package initialization complete.")