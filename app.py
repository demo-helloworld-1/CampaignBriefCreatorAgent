# app.py
# This is the entry point script to run the Flask server.

import os
import sys
import traceback # Import traceback for startup errors

# Add the src directory to the Python path so we can import from it
# This is necessary when running the script directly from the project root
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'src'))

# Import the Flask app instance from src.app
# This will also trigger the initialization of modules imported by src.app
# (config, llm, rag, tools, agents, workflows)
try:
    from src.app import app
    # Import config for paths needed in startup checks
    from src.config import OUTPUT_DIR, PERSIST_DIRECTORY
    print("Successfully imported Flask app from src.app.")
except Exception as e:
    print(f"\n*** CRITICAL ERROR: Failed to import Flask app from src.app: {e} ***")
    traceback.print_exc()
    print("\nExiting due to critical startup failure.")
    # Exit if the app cannot even be imported
    sys.exit(1) # Use sys.exit with a non-zero code to indicate error


# --- Startup Checks ---
# Ensure output directory exists (config.py already tries, but double check or log)
if not os.path.exists(OUTPUT_DIR):
    print(f"WARNING: Output directory '{OUTPUT_DIR}' does not exist at startup.")
    # config.py already attempts to create it with exist_ok=True,
    # so we just log here if it's still somehow missing.


# Ensure vector store exists. The src.rag module logs a warning if it doesn't exist when loading.
if not os.path.exists(PERSIST_DIRECTORY):
    print(f"\n*** WARNING: Vector store directory '{PERSIST_DIRECTORY}' not found at startup.")
    print("Please ensure you run 'python build_vector_store.py' successfully before starting the server.")
else:
    # Optional: Add a basic check for vector store validity here if needed
    # (Caution: might add startup time)
    print(f"Vector store directory '{PERSIST_DIRECTORY}' found.")


print("\n--- Starting Flask Server ---")

# --- Run the Flask App ---
if __name__ == '__main__':
    # Use debug=True for development (auto-reloads on code changes)
    # Set debug=False for production
    # Host '0.0.0.0' makes the server externally accessible (use with caution)
    # Default is '127.0.0.1' (localhost)
    try:
        app.run(debug=True, port=5000) # Or use config.FLASK_PORT if you add it to config
    except Exception as e:
        print(f"\n*** CRITICAL ERROR: Flask server failed to start: {e} ***")
        traceback.print_exc()
        sys.exit(1) # Exit with error code