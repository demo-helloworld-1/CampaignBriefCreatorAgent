# src/agents/summarizer_agent.py

# Import the LLM instance from src.llm
from src.llm import llm

# Import necessary components for creating agent and prompt
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
import traceback # Import traceback

print("--- Defining Summarizer Agent ---")

# --- Define Summarizer Prompt (COPIED EXACTLY from app copy.py) ---
# I am strictly using the prompt text from your original app copy.py
summarizer_system_message = """You are a Campaign Data Summarizer Agent. Your goal is to synthesize relevant information from retrieved historical data excerpts.
Your input is a list of messages representing the conversation history.

Your specific task is:
1.  Examine the provided message history ('messages').
2.  **Locate the ToolMessage containing the output from the 'extract_placeholders_from_template' tool.** Extract the list of required `extracted_placeholders` from the 'extracted_placeholders' key within its dictionary content. Note these required fields for focus.
3.  **Locate the most recent ToolMessage containing the output from the 'retrieve_relevant_campaign_data' tool.** Extract the *retrieved relevant text excerpts* from its content. This is your primary source material.
4.  **Summarize the extracted *retrieved relevant text excerpts* based *only* on the information present in those excerpts.**

**When summarizing, focus ONLY on extracting key information from the retrieved excerpts that is useful for creating new campaign briefs, such as:**
    - Target audience insights mentioned in the excerpts
    - Past campaign objectives and strategies mentioned in the excerpts
    - Key learnings (successes/failures) mentioned in the excerpts
    - Performance metrics/results mentioned in the excerpts
    - Observed trends/patterns mentioned in the excerpts

**IMPORTANT:** While summarizing the retrieved excerpts, **pay special attention and prioritize information that seems directly relevant to the topics indicated by the `extracted_placeholders` list** you noted in step 2. Your goal is to provide a summary based *only* on the relevant retrieved excerpts that is maximally useful for filling the specific fields required by the new brief template. Do not infer or add information not present in the provided excerpts.

Your final output MUST be ONLY the concise, informative summary derived *strictly from the provided retrieved excerpts*.
"""

# Create the ChatPromptTemplate using MessagesPlaceholder
summarizer_prompt_template = ChatPromptTemplate.from_messages([
    SystemMessage(content=summarizer_system_message),
    MessagesPlaceholder(variable_name="messages") # Input messages history
])

# --- Create the Summarizer Agent (Copied from app copy.py) ---
# Use the initialized LLM from src.llm
summarizer_agent = None # Initialize to None

if llm is None:
    print("*** WARNING: LLM not initialized. Cannot create Summarizer Agent. ***")
else:
    try:
        # create_react_agent can be used for agents that don't call tools themselves
        # They still operate within a message history context provided by the graph
        summarizer_agent = create_react_agent(
            model=llm,
            tools=[], # Summarizer doesn't call tools, it processes history
            prompt=summarizer_prompt_template,
            name="summarizer_agent" # Define the agent name for the supervisor to use
        )
        print(f"Summarizer Agent '{summarizer_agent.name}' defined successfully.")
    except Exception as e:
        print(f"\n*** ERROR creating Summarizer Agent: {e} ***")
        traceback.print_exc()
        summarizer_agent = None


if summarizer_agent is None:
   print("Summarizer Agent creation failed.")
   # Handle criticality if needed