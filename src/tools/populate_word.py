# src/tools/populate_word.py

import os
import json
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
import docx
from docx.shared import Inches, Pt # Import Inches for image size

# Import config for constants like OUTPUT_DIR if needed, though paths are args
# from src import config

class PopulateWordArgs(BaseModel):
    """Input schema for the PopulateWordFromJSONTool."""
    json_data: Dict[str, Any] = Field(description="JSON data (Python dictionary) for text placeholders. Keys should match placeholder content (e.g., 'PLACEHOLDER_KEY' or 'KEY').")
    image_placeholders: Optional[Dict[str, str]] = Field(default=None, description="Optional dictionary mapping image placeholder content (e.g., 'PLACEHOLDER_COMPANY_LOGO') to the local image file path (e.g., './logos/nike.png').")
    template_path: str = Field(description="Path to the Word template (.docx) file containing text and/or image placeholders.")
    output_path: str = Field(description="Path where the populated Word document will be saved.")

def populate_word_from_json_func(
    json_data: Dict[str, Any],
    template_path: str,
    output_path: str,
    image_placeholders: Optional[Dict[str, str]] = None
    ) -> str:
    """
    (Text & Images) Populates a Word document template with text data from json_data
    and image data from image_placeholders.

    Text Placeholders: {{PLACEHOLDER_KEY}} or {{KEY}}. Keys in json_data match 'PLACEHOLDER_KEY' or 'KEY'.
    Image Placeholders: {{PLACEHOLDER_IMAGE_KEY}}. Keys in image_placeholders map placeholder content to image file paths.

    Args:
        json_data: Dictionary containing the text data (keys are placeholder content).
        template_path: Path to the .docx template file.
        output_path: Path to save the populated .docx file.
        image_placeholders: Dictionary mapping image placeholder content to image file paths.

    Returns:
        A success or error message string.
    """
    print(f"\n--- Running populate_word_from_json_func (Text & Images) ---")
    print(f"Attempting to populate template '{template_path}' and save to '{output_path}'...")

    # --- Input Validation ---
    if not isinstance(json_data, dict):
        msg = f"ERROR: Input 'json_data' is not a dictionary (received type: {type(json_data)})."
        print(msg)
        return msg
    if image_placeholders is not None and not isinstance(image_placeholders, dict):
        msg = f"ERROR: Input 'image_placeholders' must be a dictionary or None (received type: {type(image_placeholders)})."
        print(msg)
        return msg
    image_placeholders = image_placeholders or {} # Ensure it's a dict for iteration

    print(f"DEBUG: Received json_data keys: {list(json_data.keys())}")
    print(f"DEBUG: Received image_placeholders keys: {list(image_placeholders.keys())}")

    # --- Path handling ---
    absolute_template_path = os.path.abspath(template_path)
    absolute_output_path = os.path.abspath(output_path)
    print(f"DEBUG: Absolute Template Path: {absolute_template_path}")
    print(f"DEBUG: Absolute Output Path: {absolute_output_path}")

    try:
        if not os.path.exists(template_path):
            return f"Error: Template file not found at '{template_path}'"

        doc = docx.Document(template_path)
        text_keys_successfully_replaced = set()
        image_keys_successfully_replaced = set()

        # --- Helper Function to find and replace TEXT ---
        def find_and_replace_text(paragraph, current_json_data):
            nonlocal text_keys_successfully_replaced
            # Iterate through keys provided in the json_data
            for key_from_json, text_to_insert in current_json_data.items():
                # Construct the placeholder strings to search for based on the key
                # The key is expected to be the CONTENT inside the braces (e.g., "PLACEHOLDER_NAME")
                placeholder_to_find = f"{{{{{key_from_json}}}}}\""

                # Check if this placeholder string exists in the paragraph text
                if placeholder_to_find in paragraph.text:
                    print(f"  Found TEXT placeholder '{placeholder_to_find}'. Attempting replacement...")
                    text_to_insert = str(text_to_insert or "") # Ensure it's a string, handle None

                    # Simple replace logic in runs - may need improvement for complex cases
                    inline = paragraph.runs
                    replaced_in_runs = False
                    for run in inline:
                        if placeholder_to_find in run.text:
                            run.text = run.text.replace(placeholder_to_find, text_to_insert)
                            replaced_in_runs = True
                            # Could potentially break here if only replacing first instance

                    if replaced_in_runs:
                        print(f"  Replaced TEXT '{placeholder_to_find}' with content for key '{key_from_json}'")
                        text_keys_successfully_replaced.add(key_from_json)
                    else:
                        print(f"  WARNING: Could not replace text '{placeholder_to_find}' within individual runs for key '{key_from_json}'. Placeholder may span runs.")


        # --- Helper Function to find and replace IMAGES ---
        def find_and_replace_image(paragraph, current_image_placeholders):
            nonlocal image_keys_successfully_replaced
            # Iterate through image placeholders provided (key = placeholder content, value = image path)
            for img_placeholder_content, img_path in current_image_placeholders.items():
                # Construct the full placeholder string to search for
                placeholder_to_find = f"{{{{{img_placeholder_content}}}}}\""

                # Check if placeholder exists in the paragraph text
                if placeholder_to_find in paragraph.text:
                    print(f"  Found IMAGE placeholder '{placeholder_to_find}'. Attempting insertion from path '{img_path}'...")
                    # Verify the image file exists
                    if not os.path.exists(img_path):
                        print(f"  WARNING: Image file not found at path: '{img_path}' for placeholder '{placeholder_to_find}'. Skipping.")
                        continue # Skip to next image key

                    # Attempt replacement - clear placeholder text and add picture
                    inline = paragraph.runs
                    found_run = None
                    for i, run in enumerate(inline):
                        if placeholder_to_find in run.text:
                            found_run = run
                            break # Found the run

                    if found_run:
                        # Clear the placeholder text from the found run
                        # This simple replace assumes the placeholder is the only or main text in the run
                        found_run.text = found_run.text.replace(placeholder_to_find, '')
                        try:
                            # Add the picture to that specific run
                            # Adjust width/height as needed - using a fixed width here
                            found_run.add_picture(img_path, width=Inches(1.5)) # Example fixed width
                            print(f"  Inserted IMAGE '{img_path}' for placeholder '{img_placeholder_content}'.")
                            image_keys_successfully_replaced.add(img_placeholder_content)
                            # Assuming one image placeholder per key is sufficient
                        except Exception as img_e:
                            print(f"  ERROR: Failed to insert image '{img_path}': {img_e}")
                            import traceback
                            traceback.print_exc()
                    else:
                        print(f"  WARNING: Could not find a run containing the image placeholder '{placeholder_to_find}'. Image not inserted.")


        # --- Main Processing Loop ---
        print("Checking paragraphs and tables for text and images...")
        all_paragraphs = list(doc.paragraphs) # Convert to list to avoid issues during modification
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    # Convert cell paragraphs to list as well
                    all_paragraphs.extend(list(cell.paragraphs))

        for paragraph in all_paragraphs:
            # Process text first
            find_and_replace_text(paragraph, json_data)
            # Then process images in the same paragraph
            if image_placeholders:
                find_and_replace_image(paragraph, image_placeholders)


        # --- Reporting ---
        print("\n--- Replacement Summary ---")
        # Text reporting
        text_placeholders_replaced_count = len(text_keys_successfully_replaced)
        text_keys_not_found = [k for k in json_data.keys() if k not in text_keys_successfully_replaced]
        if text_keys_not_found:
            print(f"WARNING: Text values provided for keys not found in template: {text_keys_not_found}")
        print(f"Text placeholders replaced: {text_placeholders_replaced_count} out of {len(json_data)} provided text keys.")

        # Image reporting
        image_placeholders_replaced_count = len(image_keys_successfully_replaced)
        image_keys_not_found = [k for k in image_placeholders.keys() if k not in image_keys_successfully_replaced]
        if image_keys_not_found:
            print(f"WARNING: Image paths provided for keys not found in template: {image_keys_not_found}")
        print(f"Image placeholders replaced: {image_placeholders_replaced_count} out of {len(image_placeholders)} provided image keys.")


        # --- Directory creation and saving logic ---
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                print(f"Created output directory: {output_dir}")
            except OSError as dir_e:
                # This case should ideally be handled by src/config.py ensuring output_dir exists
                return f"Error creating output directory '{output_dir}': {dir_e}"

        print(f"\nAttempting to save populated document to: '{output_path}'...")
        try:
            doc.save(output_path)
            print(f"Successfully called doc.save() for: {output_path}")
            # Optional: Add a check here that the file actually exists and is non-empty
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                return f"Error: File saving failed or resulted in an empty file for {output_path}"
            else:
                print(f"File confirmed to exist at '{output_path}' after saving.")
                return f"Successfully populated template (Text & Images) and saved to '{output_path}'"
        except Exception as e_save:
            print(f"ERROR during doc.save(): {e_save}")
            import traceback
            traceback.print_exc()
            return f"Error during file save operation: {e_save}"

    except FileNotFoundError:
        # This specific error might be caught by the initial check, but keep for safety
        return f"Error: Template file not found at '{template_path}' during processing."
    except Exception as e:
        print(f"An unexpected error occurred during Word processing: {e}")
        import traceback
        traceback.print_exc()
        return f"Error populating Word template: {e}"


# Create the LangChain StructuredTool
populate_word_tool = StructuredTool.from_function(
    func=populate_word_from_json_func,
    name="populate_word_from_json",
    description="Populates a Word (.docx) template with text and images. Requires 'json_data' (dict for text placeholders like {{PLACEHOLDER_KEY}}), 'template_path', 'output_path', and optionally 'image_placeholders' (dict mapping placeholder content like 'PLACEHOLDER_COMPANY_LOGO' to image file path). Text keys in json_data match content inside braces (e.g., 'PLACEHOLDER_KEY' or 'KEY'). Image keys in image_placeholders match image placeholder content (e.g., 'PLACEHOLDER_COMPANY_LOGO'). Returns a status message.",
    args_schema=PopulateWordArgs,
    return_direct=False
)

print(f"Defined tool: {populate_word_tool.name}")

# Optionally add the tool to __all__ for easier import in tools/__init__.py
__all__ = ["populate_word_tool"]