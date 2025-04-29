# src/agents/summarizer_agent.py

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent # This agent type works well with history/tools
from langchain_core.messages import SystemMessage # Import SystemMessage explicitly

# Import the chat LLM from our llm module
import sys
sys.path.append('../')
import llm # This will import the llm.py module


summarizer_system_message = """You are a Campaign Data Summarizer Agent. Your goal is to synthesize relevant information from retrieved historical data excerpts.
Your input is a list of messages representing the conversation history.

Your specific task is:
1.  Examine the provided message history ('messages').
2.  **Locate the ToolMessage containing the output from the 'extract_placeholders_from_template' tool.** Extract the list of required `extracted_placeholders` from the 'extracted_placeholders' key within its dictionary content. Note these required fields for focus.
3.  **Locate the most recent ToolMessage containing the output from the 'retrieve_relevant_campaign_data' tool that contains the *campaign text excerpts*.** Extract these excerpts. This is your primary source material for summarization. **IGNORE** any retrieval results that look like metadata (e.g., containing 'ImagePath:') - the supervisor handles logo metadata separately.
4.  **Summarize the extracted *retrieved relevant text excerpts* based *only* on the information present in those excerpts.**

**When summarizing, focus ONLY on extracting key information from the retrieved excerpts that is useful for creating new campaign briefs, such as:**
    - Target audience insights mentioned in the excerpts
    - Past campaign objectives and strategies mentioned in the excerpts
    - Key learnings (successes/failures) mentioned in the excerpts
    - Performance metrics/results mentioned in the excerpts
    - Observed trends/patterns mentioned in the excerpts
    - Budgeting approaches or typical allocations mentioned
    - Channel usage patterns mentioned
    - Asset types mentioned

**IMPORTANT:** While summarizing the retrieved excerpts, **pay special attention and prioritize information that seems directly relevant to the topics indicated by the `extracted_placeholders` list** you noted in step 2. Your goal is to provide a summary based *only* on the relevant retrieved excerpts that is maximally useful for filling the specific fields required by the new brief template. Do not infer or add information not present in the provided excerpts. If no relevant campaign text excerpts are found or provided, state that.

Your final output MUST be ONLY the concise, informative summary derived *strictly from the provided retrieved excerpts* and focused by the placeholders. Start the summary with a clear heading like "**Campaign Summary based on Retrieved Data:**".
"""

summarizer_prompt_template = ChatPromptTemplate.from_messages([
    SystemMessage(content=summarizer_system_message),
    MessagesPlaceholder(variable_name="messages") # Input messages history
])

# --- Create the Summarizer Agent ---
summarizer_agent = None
print("--- Defining Summarizer Agent ---")

# Check if the chat LLM was successfully initialized
if llm.chat_llm is None:
    print("Summarizer Agent definition skipped: Chat LLM not initialized.")
else:
    try:
        # Agents within create_supervisor typically don't call tools themselves unless explicitly routed
        # Their action is usually just to generate a response based on the prompt and history.
        # The supervisor routes *to* them, they process, and their output is added to history.
        summarizer_agent = create_react_agent(
            model=llm.chat_llm, # Use the initialized chat LLM
            tools=[], # Summarizer doesn't call tools, it processes history
            prompt=summarizer_prompt_template,
            name="summarizer_agent" # Give the agent a name for the graph
        )
        print(f"Summarizer Agent '{summarizer_agent.name}' defined successfully.")
    except Exception as e:
        print(f"*** ERROR creating Summarizer Agent: {e} ***")
        import traceback
        traceback.print_exc()
        summarizer_agent = None


# Optionally add the agent to __all__ for easier import in agents/__init__.py
__all__ = ["summarizer_agent"]