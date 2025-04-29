# src/tools/__init__.py

# Import all tools defined in this package
from .extract_placeholders import extract_placeholders_tool
from .populate_word import populate_word_tool
from .retrieve_data import retrieve_data_tool

# Define which tools are exposed when importing * from this package
__all__ = [
    "extract_placeholders_tool",
    "populate_word_tool",
    "retrieve_data_tool"
]

# You can also create a list of all tools here for convenience
all_tools = [
    extract_placeholders_tool,
    populate_word_tool,
    retrieve_data_tool
]

print(f"Initialized tools package. Available tools: {[tool.name for tool in all_tools]}")