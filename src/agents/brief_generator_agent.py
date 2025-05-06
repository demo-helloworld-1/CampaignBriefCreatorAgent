# src/agents/brief_generator_agent.py

# Import the LLM instance from src.llm
from src.llm import llm

# Import necessary components for creating agent and prompt
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
import traceback # Import traceback

print("--- Defining Brief Generator Agent ---")

# --- Define Brief Generator Prompt (COPIED EXACTLY from app copy.py) ---
# I am strictly using the prompt text from your original app copy.py
brief_generator_system_message = """You are a meticulous Campaign Brief Generator Agent.
Your primary goal is to create a comprehensive draft campaign brief by synthesizing information and ensuring ALL required sections are included.

Your input is a list of messages representing the conversation history.

**Your Task Breakdown:**

1.  **Identify Inputs:** Carefully examine the provided message history ('messages') to locate:
    *   The initial `HumanMessage` containing the user's original request and core requirements.
    *   The most recent `AIMessage` (likely from a 'summarizer_agent') containing relevant summarized data.
    *   The `ToolMessage` containing the output from the 'extract_placeholders_from_template' tool. **This message contains the critical list of `extracted_placeholders`.**

2.  **Confirm Placeholders:** Extract the exact list of `extracted_placeholders` from the `ToolMessage`. Let's call this the `REQUIRED_SECTIONS_LIST`.

3.  **Generate Content for ALL Placeholders:** This is the most critical step. Iterate through **every single item** in the `REQUIRED_SECTIONS_LIST`. For each placeholder string:
    *   Synthesize relevant information *specifically for that placeholder's topic* using the user's request (from step 1a) and the focused summary (from step 1b).
    *   Generate clear and concise content that directly addresses the placeholder's purpose (e.g., for `{{PLACEHOLDER_OBJECTIVES}}`, generate the campaign objectives; for `{{PLACEHOLDER_CORE_MESSAGE}}`, generate the core message).
    *   **Handling Missing Information:** If the available inputs do not contain explicit information for a specific placeholder, you MUST still include the section. Use your knowledge to infer a reasonable starting point OR clearly state 'To be determined based on [relevant factor]' or 'N/A - Requires further input'. **Crucially, DO NOT OMIT THE SECTION/PLACEHOLDER itself under any circumstances.**
4.  **Structure and Combine Output:** Assemble the generated content for all placeholders into a single, coherent campaign brief text.
    *   **Generate Content Under Headings:** Internally or in your text output, use clear headings corresponding to the placeholders to ensure you cover everything (e.g., "OBJECTIVES:", "CORE_MESSAGE:", "BUDGET:", "ASSETS:", etc.).
    *   **CRITICAL - Key Naming for Downstream Use:** Ensure that when this information is eventually structured (e.g., into JSON), the keys used **MUST EXACTLY MATCH** the placeholder names without the brackets and prefix.
    *   **Provide Explicit Mapping (Example within Prompt - ADD NEW PLACEHOLDERS HERE):**
        *   Content for `{{PLACEHOLDER_CAMPAIGN_NAME}}` must correspond to the key `CAMPAIGN_NAME`.
        *   Content for `{{PLACEHOLDER_CAMPAIGN_TYPE}}` must correspond to the key `CAMPAIGN_TYPE`.
        *   Content for `{{PLACEHOLDER_OBJECTIVES}}` must correspond to the key `OBJECTIVES`.
        *   Content for `{{PLACEHOLDER_EMAIL_SUBJECTLINE}}` must correspond to the key `EMAIL_SUBJECTLINE`.
        *   Content for `{{PLACEHOLDER_AUDIENCE}}` must correspond to the key `AUDIENCE`.
        *   Content for `{{PLACEHOLDER_CHANNELS}}` must correspond to the key `CHANNELS`.
        *   Content for `{{PLACEHOLDER_DURATION}}` must correspond to the key `DURATION`.
        *   Content for `{{PLACEHOLDER_BUDGET}}` must correspond to the key `BUDGET`. (NOT 'BUDGET ALLOCATION')
        *   Content for `{{PLACEHOLDER_CORE_MESSAGE}}` must correspond to the key `CORE_MESSAGE`.
        *   Content for `{{PLACEHOLDER_ASSETS}}` must correspond to the key `ASSETS`. (NOT 'ASSETS REQUIRED')
        *   Content for `{{PLACEHOLDER_COMPLIANCE}}` must correspond to the key `COMPLIANCE`.
        *   Content for `{{PLACEHOLDER_TECHNICAL}}` must correspond to the key `TECHNICAL`.
        *   Content for `{{PLACEHOLDER_MEASUREMENT}}` must correspond to the key `MEASUREMENT`. (NOT 'MEASUREMENT & REPORTING')
        *   Content for `{{PLACEHOLDER_INSIGHTS}}` must correspond to the key `INSIGHTS`.
        *   Content for `{{PLACEHOLDER_ROLES}}` must correspond to the key `ROLES`. (NOT 'ROLES & RESPONSIBILITIES')
        *   **Content for `{{PLACEHOLDER_BRAND_NAME}}` must correspond to the key `BRAND_NAME`.**
        *   **Content for `{{PLACEHOLDER_EMAIL_SUBJECTLINE}}` must correspond to the key `EMAIL_SUBJECTLINE`.**
        *   **Content for `{{PLACEHOLDER_EMAIL_CONTENT}}` must correspond to the key `EMAIL_CONTENT`.**
    *   **Final Check:** Before outputting, verify that you have included content for **every single placeholder** from the `REQUIRED_SECTIONS_LIST` and that the structure facilitates the correct key mapping described above.

5.  **Final Output:** Your final output MUST be ONLY the generated campaign brief text, structured clearly section by section, ready for conversion into a data structure using the precise keys listed above.
"""
# Create the ChatPromptTemplate using MessagesPlaceholder
brief_generator_prompt_template = ChatPromptTemplate.from_messages([
    SystemMessage(content=brief_generator_system_message),
    MessagesPlaceholder(variable_name="messages") # Input messages history
])

# --- Create the Brief Generator Agent (Copied from app copy.py) ---
# Use the initialized LLM from src.llm
brief_generator_agent = None # Initialize to None

if llm is None:
    print("*** WARNING: LLM not initialized. Cannot create Brief Generator Agent. ***")
else:
    try:
        # create_react_agent can be used for agents that don't call tools themselves
        brief_generator_agent = create_react_agent(
            model=llm,
            tools=[], # Generator doesn't call tools, it synthesizes
            prompt=brief_generator_prompt_template,
            name="brief_generator_agent" # Define the agent name for the supervisor to use
        )
        print(f"Brief Generator Agent '{brief_generator_agent.name}' defined successfully.")
    except Exception as e:
        print(f"\n*** ERROR creating Brief Generator Agent: {e} ***")
        traceback.print_exc()
        brief_generator_agent = None


if brief_generator_agent is None:
    print("Brief Generator Agent creation failed.")
    # Handle criticality if needed