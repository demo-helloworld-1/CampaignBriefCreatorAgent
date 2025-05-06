# src/app.py

# --- Flask Specific Imports ---
from flask import Flask, request, jsonify

# --- Import necessary components from the src package ---
from src.workflows.brief_generation_workflow import compiled_supervisor_workflow
# Import config for paths and log config
from src.config import OUTPUT_PATH, WORKFLOW_LOG_DIR, WORKFLOW_LOG_BASE_FILENAME

# Import Langchain Core components potentially needed for message types or processing results
from langchain_core.messages import ToolCall, AIMessage, HumanMessage, SystemMessage, ToolMessage
import traceback # Import traceback for better error logging
import datetime # For timestamp in log filename
import uuid # For unique ID in log filename
import os # For path joining

print("Initializing Flask app...")

# --- Initialize Flask App ---
app = Flask(__name__)

print("Flask app initialized.")

# --- Define Flask Route ---
@app.route('/create-brief', methods=['POST'])
def handle_create_brief():
    """
    Flask endpoint to receive campaign brief requirements and trigger the workflow.
    Expects JSON payload: {"brief_details": "Your campaign requirements here..."}

    Returns JSON payload including the generated brief text data and image data.
    """
    # Check if the workflow is ready before processing the request
    if compiled_supervisor_workflow is None:
        error_msg = "Workflow components failed to initialize during server startup. Cannot process request."
        print(f"ERROR: {error_msg}")
        return jsonify({"status": "error", "message": error_msg}), 500

    # --- Parse Request ---
    data = request.get_json()
    if not data or 'brief_details' not in data:
        return jsonify({"status": "error", "message": "Invalid request: JSON payload required with 'brief_details' key."}), 400

    # Use .get with default and strip whitespace for safety
    new_brief_prompt = data.get('brief_details', '').strip()

    if not new_brief_prompt:
        return jsonify({"status": "error", "message": "Brief details cannot be empty."}), 400

    # Construct the initial message for the workflow state
    initial_user_message_content = f"User's New Campaign Brief Prompt: {new_brief_prompt}"
    # The initial state expects a list of messages
    initial_messages = [HumanMessage(content=initial_user_message_content)]
    # The initial state dictionary expected by invoke
    initial_state = {"messages": initial_messages}


    print("\n--- Received Request via Flask. Invoking Workflow ---")
    print(f"User Prompt: {new_brief_prompt}")

    # --- Generate unique filename for workflow log ---
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:6] # Use first 6 chars of a UUID
    workflow_log_filename = f"{WORKFLOW_LOG_BASE_FILENAME}_{timestamp}_{unique_id}.log"
    workflow_log_filepath = os.path.join(WORKFLOW_LOG_DIR, workflow_log_filename)
    print(f"Workflow message history will be saved to: {workflow_log_filepath}")


    try:
        # --- Invoke the compiled LangGraph app ---
        # Pass the initial state dictionary
        # Use a reasonable recursion limit as in original code
        result = compiled_supervisor_workflow.invoke(
            initial_state, # Pass the state dictionary
            {"recursion_limit": 150} # Set a reasonable recursion limit to prevent infinite loops
        )

        # --- Process and Return Final Results from Workflow History ---
        print("\n--- Workflow Completed. Preparing Response ---")

        # Initialize variables to hold the extracted data from the final ToolCall args
        brief_text_json_data = None
        image_placeholders_data = None
        # Initial status message based on the workflow finishing
        final_status_message = "Workflow completed, attempting to find save status." # Default initial status

        # Find the final status message from the populate_word_from_json tool's output (ToolMessage)
        # And find the ToolCall that invoked it to get the arguments (json_data, image_placeholders)
        final_populate_output_message = None
        populate_tool_call_args = None # Dictionary to hold the args from the ToolCall

        # Get the messages list from the result state, default to empty list if missing
        messages_history = list(result.get('messages', []))

        print(f"DEBUG: Reviewing {len(messages_history)} messages in workflow history for final output.")

        # Search history in reverse for the populate tool output and call
        for msg_index in range(len(messages_history) - 1, -1, -1):
            msg = messages_history[msg_index]

            # 1. Look for the ToolMessage which is the *output* of the populate tool
            # Use getattr for safety when checking name
            if isinstance(msg, ToolMessage) and getattr(msg, 'name', None) == 'populate_word_from_json':
                final_populate_output_message = msg # Keep the whole message object
                print(f"DEBUG: Found populate_word_from_json ToolMessage (Output) at index {msg_index}.")

                # 2. Now, look backwards *just before* this message to find the preceding AIMessage with the ToolCall
                for prev_msg_index in range(msg_index - 1, -1, -1):
                    prev_msg = messages_history[prev_msg_index]

                    if isinstance(prev_msg, AIMessage):
                        tool_calls = getattr(prev_msg, 'tool_calls', None)
                        if tool_calls:
                            for tool_call in tool_calls:
                                tool_call_name = tool_call.get('name') if isinstance(tool_call, dict) else getattr(tool_call, 'name', None)
                                if tool_call_name == 'populate_word_from_json':
                                    populate_tool_call_args = tool_call.get('args') if isinstance(tool_call, dict) else getattr(tool_call, 'args', None)
                                    if populate_tool_call_args:
                                        if isinstance(populate_tool_call_args, dict):
                                            brief_text_json_data = populate_tool_call_args.get('json_data')
                                            image_placeholders_data = populate_tool_call_args.get('image_placeholders')
                                        else:
                                            print(f"DEBUG: populate_word_from_json args were not a dict: {type(populate_tool_call_args)}")

                                        print(f"DEBUG: Found populate_word_from_json ToolCall (Input Args) at index {prev_msg_index}.")
                                    else:
                                        print(f"DEBUG: Found populate_word_from_json ToolCall at index {prev_msg_index}, but could not extract args.")

                                    break # Exit inner tool_calls loop
                            if populate_tool_call_args is not None:
                                break # Exit outer prev_msg loop
                break # Found the ToolMessage output, stop searching the history


        # Determine the final status message to return in the response
        if final_populate_output_message is not None:
            final_status_message = getattr(final_populate_output_message, 'content', 'Tool execution message has no content.')
            final_status_message = str(final_status_message)
            print(f"DEBUG: Using status message from populate_word_from_json ToolMessage: '{final_status_message[:100]}...'")
        else:
            last_message = messages_history[-1] if messages_history else None
            if last_message:
                final_status_message = getattr(last_message, 'content', 'Last message has no content.')
                final_status_message = str(final_status_message)
                print(f"DEBUG: Using status message from last message in history: '{final_status_message[:100]}...'")
            else:
                final_status_message = "Workflow finished, no messages found in history."
                print("DEBUG: No messages found in workflow history.")


        # --- Save Workflow History to Log File ---
        print("\n--- Saving Workflow Message History to File ---")
        try:
            with open(workflow_log_filepath, 'w', encoding='utf-8') as log_file:
                log_file.write(f"--- Workflow Message History for Request {timestamp}_{unique_id} ---\n")
                log_file.write(f"User Prompt: {new_brief_prompt}\n")
                log_file.write("-" * 30 + "\n\n")

                if messages_history:
                    for i, m in enumerate(messages_history):
                        log_file.write(f"--- Message {i+1} ({type(m).__name__}, role: {getattr(m, 'type', 'N/A')}) ---\n")
                        # Use pretty_print if available, otherwise write string representation
                        if hasattr(m, 'pretty_print'):
                            # Capture pretty_print output by temporarily redirecting stdout
                            import io, sys
                            old_stdout = sys.stdout
                            redirected_output = io.StringIO()
                            sys.stdout = redirected_output
                            try:
                                m.pretty_print()
                                pretty_output = redirected_output.getvalue()
                                log_file.write(pretty_output)
                            except Exception as pp_e:
                                log_file.write(f"Error pretty printing message {i+1}: {pp_e}\n")
                                log_file.write(str(m) + "\n") # Fallback to standard print
                            finally:
                                sys.stdout = old_stdout # Restore stdout
                        else:
                            log_file.write(str(m) + "\n") # Write string representation

                        log_file.write("\n" + "="*20 + "\n\n") # Separator between messages

                else:
                    log_file.write("No messages in workflow history to display.")
                log_file.write(f"\n--- End Workflow Message History for Request {timestamp}_{unique_id} ---\n")
            print(f"Workflow message history saved to {workflow_log_filepath}")

        except Exception as log_e:
            print(f"\n*** ERROR saving workflow message history to file {workflow_log_filepath}: {log_e} ***")
            traceback.print_exc()
            # Decide if failure to log should make the request fail - usually not.


        # Prepare the JSON response payload
        overall_status = "success" if "Successfully populated template" in final_status_message else "workflow_completed_with_issues"

        response_payload = {
            "status": overall_status,
            "message": final_status_message, # Status from the populate tool or fallback message
            "output_file": OUTPUT_PATH, # Path to the saved file from config
            "workflow_log_file": workflow_log_filepath, # Add path to the log file
            "brief_data_json": brief_text_json_data,
            "image_placeholders_data": image_placeholders_data
        }

        print("Sending JSON response.")
        return jsonify(response_payload), 200

    except Exception as e:
        print(f"\n*** UNEXPECTED ERROR during workflow execution or result processing: {e} ***")
        traceback.print_exc()
        # If an error occurred during workflow execution, the status should reflect that
        # Attempt to save history up to the point of error
        error_messages_history = list(result.get('messages', [])) if 'result' in locals() and result and isinstance(result, dict) else []
        # Add the exception details to the history that will be saved
        error_messages_history.append(SystemMessage(content=f"Workflow terminated unexpectedly due to error: {str(e)}\nTraceback: {traceback.format_exc()}"))

        # Generate a log filename for the error case
        error_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        error_unique_id = uuid.uuid4().hex[:6]
        error_workflow_log_filename = f"{WORKFLOW_LOG_BASE_FILENAME}_{error_timestamp}_{error_unique_id}_ERROR.log"
        error_workflow_log_filepath = os.path.join(WORKFLOW_LOG_DIR, error_workflow_log_filename)

        try:
            print(f"\n--- Saving Workflow Message History (Error Case) to File ---")
            with open(error_workflow_log_filepath, 'w', encoding='utf-8') as log_file:
                log_file.write(f"--- Workflow Message History (ERROR) for Request {error_timestamp}_{error_unique_id} ---\n")
                log_file.write(f"User Prompt: {new_brief_prompt}\n")
                log_file.write("-" * 30 + "\n\n")
                # Use the potentially incomplete history including the error message
                if error_messages_history:
                    for i, m in enumerate(error_messages_history):
                        log_file.write(f"--- Message {i+1} ({type(m).__name__}, role: {getattr(m, 'type', 'N/A')}) ---\n")
                        import io, sys
                        old_stdout = sys.stdout
                        redirected_output = io.StringIO()
                        sys.stdout = redirected_output
                        try:
                            if hasattr(m, 'pretty_print'): m.pretty_print()
                            else: print(m)
                            log_file.write(redirected_output.getvalue())
                        except:
                            log_file.write(str(m) + "\n")
                        finally:
                            sys.stdout = old_stdout
                        log_file.write("\n" + "="*20 + "\n\n")
                log_file.write(f"\n--- End Workflow Message History (ERROR) for Request {error_timestamp}_{error_unique_id} ---\n")
            print(f"Workflow message history (error case) saved to {error_workflow_log_filepath}")
            log_file_info_for_response = error_workflow_log_filepath
        except Exception as log_e:
            print(f"\n*** ERROR saving workflow message history to file in error handler {error_workflow_log_filepath}: {log_e} ***")
            traceback.print_exc()
            log_file_info_for_response = "Failed to save workflow log in error handler."


        # Return error response
        return jsonify({
            "status": "workflow_failed",
            "message": f"An unexpected error occurred during workflow execution: {str(e)}",
            "workflow_log_file": log_file_info_for_response, # Include path to error log
            "brief_data_json": None, # Data likely incomplete on error
            "image_placeholders_data": None # Data likely incomplete on error
        }), 500

# Note: The Flask app instance 'app' is defined here.
# Running the Flask app (app.run) will be handled by the root app.py file.