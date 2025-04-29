# src/agents/brief_generator_agent.py

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage # Import SystemMessage explicitly

# Import the chat LLM from our llm module
import sys
sys.path.append('../')
import llm


brief_generator_system_message = """You are a meticulous Campaign Brief Generator Agent.
Your primary goal is to create a comprehensive draft campaign brief text by synthesizing information and ensuring ALL required sections are included, based on a template's placeholders.

Your input is a list of messages representing the conversation history.

**Your Task Breakdown:**

1.  **Identify Inputs:** Carefully examine the provided message history ('messages') to locate:
    *   The initial `HumanMessage` containing the user's original request and core requirements.
    *   The most recent `AIMessage` (likely from the 'summarizer_agent') containing the focused summary of relevant data.
    *   The `ToolMessage` containing the output from the 'extract_placeholders_from_template' tool. **This message contains the critical list of `extracted_placeholders`.**

2.  **Confirm Placeholders:** Extract the exact list of `extracted_placeholders` strings (e.g., "{{PLACEHOLDER_NAME}}", "{{PLACEHOLDER_OBJECTIVES}}") from the `ToolMessage`. Let's call this the `REQUIRED_PLACEHOLDERS_LIST`. **Exclude image placeholders like '{{PLACEHOLDER_COMPANY_LOGO}}'** as you only generate text content.

3.  **Generate Content for ALL Text Placeholders:** Iterate through **every single text placeholder string** in the filtered `REQUIRED_PLACEHOLDERS_LIST` (excluding images). For each placeholder:\n
    *   Synthesize clear and concise content for the topic indicated by the placeholder name.\n
    *   Prioritize information from the user's original request and the focused summary.
    *   If the user prompt provides specific values for certain fields (like Campaign Name, Duration, Budget, Roles), ensure these exact values are incorporated into the relevant sections, overriding or supplementing the summary.\n
    *   **Handling Missing Information:** If the inputs do not contain explicit information for a specific placeholder, infer a reasonable default, state "To be determined based on [relevant factor]", or use "N/A - Requires further input" as appropriate. **Crucially, you MUST provide content for every placeholder in the list.** Do NOT omit any section.\n
    *   Structure your output clearly with headings that indicate which placeholder the content is for. Use the placeholder content (the part inside the braces, e.g., "PLACEHOLDER_CAMPAIGN_NAME") as the heading identifier. For example, start a section with "PLACEHOLDER_CAMPAIGN_NAME:".\n
        *   **Example Key Mapping to Use for Headings:**
            *   `{{PLACEHOLDER_CAMPAIGN_NAME}}` -> Use heading `PLACEHOLDER_CAMPAIGN_NAME:`
            *   `{{PLACEHOLDER_OBJECTIVES}}` -> Use heading `PLACEHOLDER_OBJECTIVES:`
            *   `{{PLACEHOLDER_AUDIENCE}}` -> Use heading `PLACEHOLDER_AUDIENCE:`
            *   `{{PLACEHOLDER_BUDGET}}` -> Use heading `PLACEHOLDER_BUDGET:`
            *   (and so on for all extracted TEXT placeholders)
    *   Ensure your output format is plain text, sectioned by these identifiers. The supervisor will parse this text.\n

4.  **Final Output:** Your final output MUST be ONLY the generated campaign brief text, structured clearly section by section using the placeholder content as identifiers, covering content for *every single TEXT placeholder* from the `REQUIRED_PLACEHOLDERS_LIST`. Do not include conversational text or explanations before or after the brief content. Ensure the text is ready for the supervisor to parse into a JSON dictionary using the identifiers as keys.
"""

brief_generator_prompt_template = ChatPromptTemplate.from_messages([
    SystemMessage(content=brief_generator_system_message),
    MessagesPlaceholder(variable_name="messages")
])

# --- Create the Brief Generator Agent ---
brief_generator_agent = None
print("--- Defining Brief Generator Agent ---")

# Check if the chat LLM was successfully initialized
if llm.chat_llm is None:
    print("Brief Generator Agent definition skipped: Chat LLM not initialized.")
else:
    try:
        brief_generator_agent = create_react_agent(
            model=llm.chat_llm, # Use the initialized chat LLM
            tools=[], # Generator doesn't call tools, it synthesizes information
            prompt=brief_generator_prompt_template,
            name="brief_generator_agent" # Give the agent a name for the graph
        )
        print("Brief Generator Agent defined successfully.")
    except Exception as e:
        print(f"*** ERROR creating Brief Generator Agent: {e} ***")
        import traceback
        traceback.print_exc()
        brief_generator_agent = None

# Optionally add the agent to __all__ for easier import in agents/__init__.py
__all__ = ["brief_generator_agent"]