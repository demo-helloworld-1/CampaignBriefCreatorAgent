# src/workflows/brief_generation_workflow.py

# --- Import necessary components from the src package ---

# Import LLM (used by supervisor itself)
from src.llm import llm

# Import Agents (used by supervisor for delegation)
from src.agents import summarizer_agent, brief_generator_agent

# Import Tools (used by supervisor for tool calls)
# Assuming src.tools.__init__.py imports these and makes them available
from src.tools import extract_placeholders_tool, populate_word_tool, retrieve_data_tool

# Import Config (needed for paths in the supervisor prompt)
from src.config import TEMPLATE_PATH, OUTPUT_PATH # Use paths from config


# --- IMPORT THE ORIGINAL create_supervisor UTILITY ---
# This relies on the 'langgraph_supervisor' module being available in your environment.
try:
    # *** THIS IS CRITICAL - USE THE ORIGINAL IMPORT ***
    from langgraph_supervisor import create_supervisor
    print("Imported create_supervisor from langgraph_supervisor.")
    # We will NOT use src/utils/custom_supervisor.py
    create_supervisor_utility = create_supervisor # Alias for clarity

except ImportError:
    print("\n*** CRITICAL: Could not import 'create_supervisor' from 'langgraph_supervisor'.")
    print("This module is required by the original workflow logic.")
    print("Please ensure 'langgraph_supervisor' is installed or available in your environment.")
    print("Workflow compilation will FAIL.")
    create_supervisor_utility = None # Set to None if import fails


import traceback # For error handling

print("--- Defining Brief Generation Workflow (Supervisor) ---")

# --- Collect all tools the supervisor might call ---
# This list matches the one defined in app copy.py
tools_for_supervisor = [
    extract_placeholders_tool,
    populate_word_tool,
    retrieve_data_tool
]

# Filter out any tools that failed to initialize
# This check is important as initialization might fail if dependencies/config are missing
initialized_tools_for_supervisor = [tool for tool in tools_for_supervisor if tool is not None]

if len(initialized_tools_for_supervisor) < len(tools_for_supervisor):
    print(f"WARNING: Some tools failed to initialize ({len(tools_for_supervisor) - len(initialized_tools_for_supervisor)} missing). Supervisor will only have access to: {[tool.name for tool in initialized_tools_for_supervisor]}")
    if not initialized_tools_for_supervisor:
         print("*** CRITICAL: No tools initialized for supervisor. Workflow may not function. ***")


# --- Collect all agents the supervisor might delegate to ---
# This list matches the agents used in the create_supervisor call in app copy.py
agents_for_supervisor = [
    summarizer_agent,
    brief_generator_agent
]

# Filter out any agents that failed to initialize
initialized_agents_for_supervisor = [agent for agent in agents_for_supervisor if agent is not None]

if len(initialized_agents_for_supervisor) < len(agents_for_supervisor):
    print(f"WARNING: Some agents failed to initialize ({len(agents_for_supervisor) - len(initialized_agents_for_supervisor)} missing). Supervisor will only be able to delegate to: {[agent.name for agent in initialized_agents_for_supervisor if hasattr(agent, 'name')]}")
    if not initialized_agents_for_supervisor:
         print("*** CRITICAL: No agents initialized for supervisor. Workflow may not function. ***")


# --- Supervisor Prompt (COPIED EXACTLY from app copy.py) ---
# I am strictly using the prompt text from your original app copy.py
# Inject the paths from config as f-string variables
supervisor_prompt = ("""You are a Campaign Brief Supervisor Agent. Your job is to manage agents and tools to generate a brief WITH a company logo.
Workflow:
1. Extract text placeholders from template.
2. **Query retriever for relevant campaign text data** based on user request.
3. **Query retriever AGAIN for company logo metadata** based on brand mentioned in user request.
4. Summarize the retrieved campaign text data, focusing on placeholders.
5. Generate the new brief text using user request, placeholders, and the focused summary.
6. **Parse retrieved logo metadata to get the image file path.**
7. Construct JSON for text data AND a dictionary for image placeholders.
8. Populate the Word template using both text JSON and image placeholder dictionary.

Available Tools:
1. `extract_placeholders_from_template`: Extracts placeholders from template. Returns dict {'extracted_placeholders': list, 'status': str}. Requires 'template_path'.
2. `retrieve_relevant_campaign_data`: Searches indexed data (campaign text OR logo metadata). Requires 'query'. Returns relevant text excerpts string.
3. `populate_word_from_json`: Populates a Word (.docx) template with text and images. Requires 'json_data' (dict for text placeholders like {{PLACEHOLDER_KEY}}), 'template_path', 'output_path', and optionally 'image_placeholders' (dict mapping placeholder content like 'PLACEHOLDER_COMPANY_LOGO' to image file paths). Returns status string.

Available Agents (via message history):
1. `summarizer_agent`: Summarizes retrieved relevant *campaign text excerpts*.
2. `brief_generator_agent`: Generates new brief text.

Your workflow MUST be executed in the following precise steps:

Step 1: Extract Placeholders. **Call `extract_placeholders_from_template`** with `template_path` set to `""" + TEMPLATE_PATH + """`. Remember the `extracted_placeholders` list. Check if '{{PLACEHOLDER_COMPANY_LOGO}}' (or similar) is present.

Step 2: Retrieve Relevant Campaign Data.
    a. Formulate a `campaign_query` based on the user request's topic (e.g., "EcoSmart Thermos Fall/Winter promotion").
    b. **Call `retrieve_relevant_campaign_data`** with `campaign_query`. Remember `retrieved_campaign_context`.

Step 3: **Retrieve Logo Metadata.**
    a. **Identify Brand:** Determine the primary brand name mentioned in the user's initial request (e.g., "Nike", "EcoSmart").
    b. **Formulate Logo Query:** Create a specific `logo_query` like "[Brand Name] company logo\" (e.g., \"Nike company logo\").
    c. **Call `retrieve_relevant_campaign_data`** with the `logo_query`. Remember the `retrieved_logo_metadata` string output.

Step 4: Summarize Campaign Data. **Delegate to `summarizer_agent`**. Provide the `extracted_placeholders` list and the `retrieved_campaign_context` (from Step 2b) from the message history for the agent to use.

Step 5: Generate New Campaign Brief. **Delegate to `brief_generator_agent`**. Provide the `extracted_placeholders` list, the user request, and the summary from Step 4 from the message history for the agent to use.

Step 6: Extract Generated Brief Text. Get text from `brief_generator_agent`'s last message.

Step 7: **Prepare Data for Word Template (Text & Image).** This step involves processing information from the message history.
    a. **Parse Logo Metadata:** Examine the `retrieved_logo_metadata` string (from Step 3c). Find the line starting with 'ImagePath:' and extract the file path (e.g., './logos/nike.png'). Let's call this `logo_file_path`. Handle cases where the path isn't found.
    b. **Construct Image Dictionary:** If `logo_file_path` was found and the placeholder `{{PLACEHOLDER_COMPANY_LOGO}}` exists (from Step 1), create a dictionary: `image_placeholders_dict = {'PLACEHOLDER_COMPANY_LOGO': logo_file_path}`. Otherwise, use an empty dictionary or None.
    c. **Construct Text JSON:** Using the `extracted_placeholders` list from Step 1, systematically parse the Generated Brief text (Step 6). For EACH text placeholder content in that list (e.g., `PLACEHOLDER_CAMPAIGN_NAME`, `EMAIL_SUBJECTLINE` - content *inside* the braces), find its corresponding content in the generated text and add an entry to the `text_json_data` dictionary. The keys in this dictionary MUST be the content inside the braces (e.g., 'PLACEPAOLDER_CAMPAIGN_NAME', 'EMAIL_SUBJECTLINE'). Ensure EVERY placeholder from the extracted list (except image ones handled in 7b) has a corresponding key in the `text_json_data` dictionary, even if the content is empty.
    d. **Check for Missing Placeholders:** If any placeholders from the `extracted_placeholders` list are missing in the `text_json_data`, then fill the placeholder with a related content.
    e. **Validate** both `text_json_data` and `image_placeholders_dict`.

Step 8: Save to Word Document. **Call `populate_word_from_json`**. Provide arguments EXACTLY:
    - `json_data`: The `text_json_data` dictionary from Step 7d.
    - `image_placeholders`: The `image_placeholders_dict` from Step 7b.
    - `template_path`: `""" + TEMPLATE_PATH + """` # Use the actual path from config
    - `output_path`: `""" + OUTPUT_PATH + """` # Use the actual path from config

Step 9: Final Confirmation. Output confirmation message from `populate_word_from_json`. The workflow should then route to END.

Begin by outputting a tool call to `extract_placeholders_from_template` with the correct `template_path`.
""")


# --- Create the Supervisor Workflow (Copied from app copy.py logic) ---
compiled_supervisor_workflow = None # Initialize to None

# Check if critical components and the create_supervisor utility are available
if llm is None:
    print("\n*** CRITICAL: LLM not initialized. Cannot build or compile workflow. ***")
elif create_supervisor_utility is None:
    print("\n*** CRITICAL: create_supervisor utility not available. Cannot build or compile workflow. ***")
elif not initialized_tools_for_supervisor:
    print("\n*** CRITICAL: No tools initialized. Workflow requires tools. Cannot build or compile. ***")
elif not initialized_agents_for_supervisor:
    print("\n*** CRITICAL: No agents initialized. Workflow requires agents. Cannot build or compile. ***")
else:
    try:
        print("\nAttempting to create supervisor workflow using create_supervisor utility...")
        # *** THIS CALL USES THE ORIGINAL UTILITY ***
        supervisor_workflow = create_supervisor_utility(
            agents=initialized_agents_for_supervisor, # Pass the list of initialized agents
            model=llm, # Pass the initialized LLM
            tools=initialized_tools_for_supervisor, # Pass the list of initialized tools
            prompt=supervisor_prompt # Pass the supervisor's complex instruction prompt
        )

        if supervisor_workflow is None:
             print("\n*** CRITICAL: create_supervisor utility returned None. Workflow building failed. ***")
        else:
            print("Supervisor workflow graph created successfully using create_supervisor.")

            # --- Compile the Graph ---
            # This prepares the graph for efficient execution
            print("Attempting to compile supervisor workflow...")
            compiled_supervisor_workflow = supervisor_workflow.compile()
            print("Supervisor workflow compiled successfully.")

    except Exception as e:
        print(f"\n*** ERROR setting up or compiling the supervisor workflow: {e} ***")
        traceback.print_exc()
        compiled_supervisor_workflow = None # Ensure it's None if compilation fails

if compiled_supervisor_workflow is None:
    print("\n*** CRITICAL: Workflow compilation failed. The Flask app will not be able to process requests. ***")
else:
    print("\nWorkflow setup complete. Ready to accept requests.")