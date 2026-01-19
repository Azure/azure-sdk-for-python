# Copyright (c) Microsoft. All rights reserved.
"""Enhanced MCP example using ToolClient with AzureAIToolClient.

This sample demonstrates how to use the ToolClient to integrate Azure AI
Tool Client (which supports both MCP tools and Azure AI Tools API) with
LangGraph's create_react_agent.
"""

import asyncio
import os

from dotenv import load_dotenv
from importlib.metadata import version
from langchain_openai import AzureChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

from azure.ai.agentserver.core.tools import FoundryToolClient
from azure.ai.agentserver.langgraph import ToolClient, from_langgraph
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


def create_agent(model, tools, checkpointer):
    """Create a LangGraph agent based on available imports."""
    try:
        from langgraph.prebuilt import create_react_agent
        return create_react_agent(model, tools, checkpointer=checkpointer)
    except ImportError:
        from langchain.agents import create_agent
        return create_agent(model, tools, checkpointer=checkpointer)


async def quickstart():
    """Build and return a LangGraph agent wired to Azure AI Tool Client."""
    
    # Get configuration from environment
    project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    deployment_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o")
    
    if not project_endpoint:
        raise ValueError(
            "AZURE_AI_PROJECT_ENDPOINT environment variable is required. "
            "Set it to your Azure AI project endpoint, e.g., "
             "https://<your-account>.services.ai.azure.com/api/projects/<your-project>"
        )
    tool_connection_id = os.getenv("AZURE_AI_PROJECT_TOOL_CONNECTION_ID")
    
    # Create Azure credentials
    credential = DefaultAzureCredential()
    tool_definitions = [
    {
        "type": "mcp",
        "project_connection_id": tool_connection_id
    },
    {
        "type": "code_interpreter",
    }
    ]
    # Create the AzureAIToolClient
    # This client supports both MCP tools and Azure AI Tools API
    tool_client = FoundryToolClient(
        endpoint=project_endpoint,
        credential=credential,
        tools=tool_definitions
    )
    
    # Create the ToolClient
    client = ToolClient(tool_client)
    
    # List all available tools and convert to LangChain format
    print("Fetching tools from Azure AI Tool Client...")
    tools = await client.list_tools_details()
    print(f"Found {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    if not tools:
        print("\nNo tools found!")
        print("Make sure your Azure AI project has tools configured.")
        print("This can include:")
        print("  - MCP (Model Context Protocol) servers")
        print("  - Foundry AI Tools")
        return None
    
    # Create the language model
    model = AzureChatOpenAI(model=deployment_name)
    
    # Create a memory checkpointer for conversation history
    memory = MemorySaver()
    
    # Create the LangGraph agent with the tools
    print("\nCreating LangGraph agent with tools...")
    agent = create_agent(model, tools, memory)
    
    print("Agent created successfully!")
    return agent


async def main():  # pragma: no cover - sample entrypoint
    """Main function to run the agent."""
    agent = await quickstart()
    
    if agent:
        print("\nStarting agent server...")
        await from_langgraph(agent).run_async()


if __name__ == "__main__":
    asyncio.run(main())
