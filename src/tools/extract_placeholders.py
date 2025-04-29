# src/tools/extract_placeholders.py

import re
import os
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
import docx # Requires: pip install python-docx

# Import constants from config if needed, though template_path is an arg here
# from src import config

class ExtractPlaceholdersArgs(BaseModel):
    """Input schema for the ExtractPlaceholdersTool."""
    template_path: str = Field(description="Path to the Word template (.docx) file containing placeholders like {{PLACEHOLDER_NAME}}.")

def extract_placeholders_func(template_path: str) -> Dict[str, Any]:
    """
    Extracts placeholders (like {{PLACEHOLDER_NAME}}) from a Word document template.
    Returns a dictionary with 'extracted_placeholders': list and 'status': str.
    """
    print(f"\n--- Running extract_placeholders_func ---")
    print(f"Attempting to extract placeholders from template '{template_path}'...")
    absolute_template_path = os.path.abspath(template_path)
    print(f"DEBUG: Absolute Template Path: {absolute_template_path}")

    if not os.path.exists(template_path):
        error_msg = f"Error: Template file not found at '{template_path}'"
        print(error_msg)
        return {"extracted_placeholders": [], "status": error_msg}

    try:
        doc = docx.Document(template_path)
        # Regex to find {{...}} allowing whitespace inside braces
        placeholder_regex = re.compile(r"\\{\\{\\s*(.*?)\\s*\\}\\}")
        found_placeholders = set()

        def find_in_runs(runs):
            # Concatenate run text to search across runs if needed (though regex works on combined)
            full_text = "".join(run.text for run in runs)
            matches = placeholder_regex.findall(full_text)
            for match_content in matches:
                # Store the full placeholder string as found in the template
                original_placeholder = f"{{{{{match_content.strip()}}}}}\"" # strip whitespace from content
                found_placeholders.add(original_placeholder)
                print(f"  Found '{original_placeholder}'") # Debug print

        # Search in regular paragraphs
        print("Checking regular paragraphs...")
        for paragraph in doc.paragraphs:
            if '{{' in paragraph.text and '}}' in paragraph.text: # Quick check before deep dive
                find_in_runs(paragraph.runs)

        # Search within tables
        print("Checking tables...")
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        if '{{' in paragraph.text and '}}' in paragraph.text: # Quick check
                            find_in_runs(paragraph.runs)

        if not found_placeholders:
            status_msg = f"No placeholders like {{...}} found in '{template_path}'."
            print(status_msg)
            return {"extracted_placeholders": [], "status": status_msg}
        else:
            sorted_placeholders = sorted(list(found_placeholders))
            status_msg = f"Successfully extracted {len(sorted_placeholders)} unique placeholders from '{template_path}'."
            print(status_msg)
            # print(f"Placeholders found: {sorted_placeholders}") # Avoid excessive logging
            return {"extracted_placeholders": sorted_placeholders, "status": status_msg}

    except Exception as e:
        error_msg = f"Error during placeholder extraction from '{template_path}': {e}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return {"extracted_placeholders": [], "status": error_msg}

# Create the LangChain StructuredTool
extract_placeholders_tool = StructuredTool.from_function(
    func=extract_placeholders_func,
    name="extract_placeholders_from_template",
    description="Reads a Word document (.docx) template, extracts all unique placeholders like {{PLACEHOLDER_NAME}} found within it (in paragraphs and tables), and returns them as a list exactly as they appear in the template. Input is 'template_path'.",
    args_schema=ExtractPlaceholdersArgs,
    return_direct=False # Means the output goes back to the agent/supervisor, not directly to the user
)

print(f"Defined tool: {extract_placeholders_tool.name}")

# Optionally add the tool to __all__ for easier import in tools/__init__.py
__all__ = ["extract_placeholders_tool"]