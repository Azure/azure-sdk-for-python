"""
Human-in-the-Loop Agent Example

This sample demonstrates how to create a LangGraph agent that can interrupt 
execution to ask for human input when needed. The agent uses Azure OpenAI 
and includes a custom tool for asking human questions.
"""

import os

from dotenv import load_dotenv
from pydantic import BaseModel

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain.chat_models import init_chat_model
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import interrupt

from azure.ai.agentserver.langgraph import from_langgraph

# Load environment variables
load_dotenv()


# =============================================================================
# Configuration
# =============================================================================

DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o")
API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")


# =============================================================================
# Model Initialization
# =============================================================================

def initialize_llm():
    """Initialize the language model with Azure OpenAI credentials."""
    if API_KEY:
        return init_chat_model(f"azure_openai:{DEPLOYMENT_NAME}")
    else:
        credential = DefaultAzureCredential()
        token_provider = get_bearer_token_provider(
            credential, "https://cognitiveservices.azure.com/.default"
        )
        return init_chat_model(
            f"azure_openai:{DEPLOYMENT_NAME}",
            azure_ad_token_provider=token_provider,
        )


llm = initialize_llm()

# =============================================================================
# Tools and Models
# =============================================================================

@tool
def search(query: str) -> str:
    """
    Call to search the web for information.
    
    Args:
        query: The search query string
        
    Returns:
        Search results as a string
    """
    # This is a placeholder for the actual implementation
    return f"I looked up: {query}. Result: It's sunny in San Francisco."


class AskHuman(BaseModel):
    """Schema for asking the human a question."""
    question: str


# Initialize tools and bind to model
tools = [search]
tool_node = ToolNode(tools)
model = llm.bind_tools(tools + [AskHuman])


# =============================================================================
# Graph Nodes
# =============================================================================

def call_model(state: MessagesState) -> dict:
    """
    Call the language model with the current conversation state.
    
    Args:
        state: The current messages state
        
    Returns:
        Dictionary with the model's response message
    """
    messages = state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}


def ask_human(state: MessagesState) -> dict:
    """
    Interrupt execution to ask the human for input.
    
    Args:
        state: The current messages state
        
    Returns:
        Dictionary with the human's response as a tool message
    """
    last_message = state["messages"][-1]
    tool_call_id = last_message.tool_calls[0]["id"]
    ask = AskHuman.model_validate(last_message.tool_calls[0]["args"])
    
    # Interrupt and wait for human input
    location = interrupt(ask.question)
    
    tool_message = ToolMessage(tool_call_id=tool_call_id, content=location)
    return {"messages": [tool_message]}


# =============================================================================
# Graph Logic
# =============================================================================

def should_continue(state: MessagesState) -> str:
    """
    Determine the next step in the graph based on the last message.
    
    Args:
        state: The current messages state
        
    Returns:
        The name of the next node to execute, or END to finish
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    # If there's no function call, we're done
    if not last_message.tool_calls:
        return END
    
    # If asking for human input, route to ask_human node
    if last_message.tool_calls[0]["name"] == "AskHuman":
        return "ask_human"
    
    # Otherwise, execute the tool call
    return "action"


# =============================================================================
# Graph Construction
# =============================================================================

def build_graph() -> StateGraph:
    """
    Build and compile the LangGraph workflow.
    
    Returns:
        Compiled StateGraph with checkpointing enabled
    """
    workflow = StateGraph(MessagesState)
    
    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("action", tool_node)
    workflow.add_node("ask_human", ask_human)
    
    # Set entry point
    workflow.add_edge(START, "agent")
    
    # Add conditional routing from agent
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        path_map=["ask_human", "action", END],
    )
    
    # Add edges back to agent
    workflow.add_edge("action", "agent")
    workflow.add_edge("ask_human", "agent")
    
    # Compile with memory checkpointer
    memory = InMemorySaver()
    return workflow.compile(checkpointer=memory)


app = build_graph()


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    adapter = from_langgraph(app)
    adapter.run()

