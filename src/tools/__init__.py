# src/tools/__init__.py

# Import the tools so they can be easily accessed from 'from src.tools import ...'
# Ensure the names match the variables defined in the tool files
from .extract_placeholders import extract_placeholders_tool
from .populate_word import populate_word_tool
from .retrieve_data import retrieve_data_tool

# You can also define __all__ if you want to be explicit about what's public
__all__ = [
    "extract_placeholders_tool",
    "populate_word_tool",
    "retrieve_data_tool",
]

print("src.tools package initialized.")