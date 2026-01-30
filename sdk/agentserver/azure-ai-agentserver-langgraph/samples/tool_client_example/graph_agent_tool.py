import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.graph import (
    END,
    START,
    MessagesState,
    StateGraph,
)
from typing_extensions import Literal
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from azure.ai.agentserver.langgraph import from_langgraph
from azure.ai.agentserver.langgraph.tools import use_foundry_tools

load_dotenv()

deployment_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o")
credential = DefaultAzureCredential()
token_provider = get_bearer_token_provider(
    credential, "https://cognitiveservices.azure.com/.default"
)
llm = init_chat_model(
    f"azure_openai:{deployment_name}",
    azure_ad_token_provider=token_provider,
)
llm_with_foundry_tools = use_foundry_tools(llm, [
    {
        # use the python tool to calculate what is 4 * 3.82. and then find its square root and then find the square root of that result
        "type": "code_interpreter"
    },
    {
        # Give me the Azure CLI commands to create an Azure Container App with a managed identity. search Microsoft Learn
        "type": "mcp",
        "project_connection_id": "MicrosoftLearn"
    },
    # {
    #     "type": "mcp",
    #     "project_connection_id": "FoundryMCPServerpreview"
    # }
])


# Nodes
async def llm_call(state: MessagesState, config: RunnableConfig):
    """LLM decides whether to call a tool or not"""

    return {
        "messages": [
            await llm_with_foundry_tools.ainvoke(
                [
                    SystemMessage(
                        content="You are a helpful assistant tasked with performing arithmetic on a set of inputs."
                    )
                ]
                + state["messages"],
                config=config,
            )
        ]
    }


# Conditional edge function to route to the tool node or end based upon whether the LLM made a tool call
def should_continue(state: MessagesState) -> Literal["environment", END]:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]
    # If the LLM makes a tool call, then perform an action
    if last_message.tool_calls:
        return "Action"
    # Otherwise, we stop (reply to the user)
    return END


# Build workflow
agent_builder = StateGraph(MessagesState)

# Add nodes
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("environment", llm_with_foundry_tools.tool_node)

# Add edges to connect nodes
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    {
        "Action": "environment",
        END: END,
    },
)
agent_builder.add_edge("environment", "llm_call")

# Compile the agent
agent = agent_builder.compile()

if __name__ == "__main__":
    adapter = from_langgraph(agent)
    adapter.run()
