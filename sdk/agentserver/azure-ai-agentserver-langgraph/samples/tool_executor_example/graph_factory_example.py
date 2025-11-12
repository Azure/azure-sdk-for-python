# Copyright (c) Microsoft. All rights reserved.
"""Example showing how to use a graph factory function with ToolClient.

This sample demonstrates how to pass a factory function to LangGraphAdapter
that receives a ToolClient and returns a CompiledStateGraph. This pattern
allows the graph to be created dynamically with access to tools from
Azure AI Tool Client at runtime.
"""

import asyncio
import os

from dotenv import load_dotenv
from importlib.metadata import version
from langchain_openai import AzureChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph

from azure.ai.agentserver.langgraph import ToolClient, from_langgraph
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


def create_agent(model, tools, checkpointer):
    """Create a LangGraph agent based on the version."""
    # for different langgraph versions
    langgraph_version = version("langgraph")
    if langgraph_version < "1.0.0":
        from langgraph.prebuilt import create_react_agent

        return create_react_agent(model, tools, checkpointer=checkpointer)
    else:
        from langchain.agents import create_agent

        return create_agent(model, tools, checkpointer=checkpointer)


def create_graph_factory():
    """Create a factory function that builds a graph with ToolClient.
    
    This function returns a factory that takes a ToolClient and returns
    a CompiledStateGraph. The graph is created at runtime when the agent
    first runs, allowing it to access the latest tool configuration.
    """
    
    async def graph_factory(tool_client: ToolClient) -> CompiledStateGraph:
        """Factory function that creates a graph using the provided ToolClient.
        
        :param tool_client: The ToolClient instance with access to Azure AI tools.
        :type tool_client: ToolClient
        :return: A compiled LangGraph state graph.
        :rtype: CompiledStateGraph
        """
        # Get configuration from environment
        deployment_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o")
        
        # List all available tools from the ToolClient
        print("Fetching tools from Azure AI Tool Client via factory...")
        tools = await tool_client.list_tools()
        print(f"Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
        if not tools:
            print("\nNo tools found!")
            print("Make sure your Azure AI project has tools configured.")
            raise ValueError("No tools available to create agent")
        
        # Create the language model
        model = AzureChatOpenAI(model=deployment_name)
        
        # Create a memory checkpointer for conversation history
        memory = MemorySaver()
        
        # Create the LangGraph agent with the tools
        print("\nCreating LangGraph agent with tools from factory...")
        agent = create_agent(model, tools, memory)
        
        print("Agent created successfully!")
        return agent
    
    return graph_factory


async def quickstart():
    """Build and return a LangGraphAdapter using a graph factory function."""
    
    # Get configuration from environment
    project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    
    if not project_endpoint:
        raise ValueError(
            "AZURE_AI_PROJECT_ENDPOINT environment variable is required. "
            "Set it to your Azure AI project endpoint, e.g., "
            "https://<your-account>.services.ai.azure.com/api/projects/<your-project>"
        )
    
    # Create Azure credentials
    credential = DefaultAzureCredential()
    
    # Create a factory function that will build the graph at runtime
    # The factory will receive a ToolClient when the agent first runs
    graph_factory = create_graph_factory()
    
    # Pass the factory function to from_langgraph instead of a compiled graph
    # The graph will be created on first agent run with access to ToolClient
    print("Creating LangGraph adapter with factory function...")
    adapter = from_langgraph(graph_factory, credentials=credential)
    
    print("Adapter created! Graph will be built on first run.")
    return adapter


async def main():  # pragma: no cover - sample entrypoint
    """Main function to run the agent."""
    adapter = await quickstart()
    
    if adapter:
        print("\nStarting agent server...")
        print("The graph factory will be called when the first request arrives.")
        await adapter.run_async()


if __name__ == "__main__":
    asyncio.run(main())
