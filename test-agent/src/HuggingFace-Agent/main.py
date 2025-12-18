# Copyright (c) Microsoft. All rights reserved.
"""Example showing how to use an agent factory function with ToolClient.

This sample demonstrates how to pass a factory function to from_agent_framework
that receives a ToolClient and returns an AgentProtocol. This pattern allows
the agent to be created dynamically with access to tools from Azure AI Tool
Client at runtime.
"""

import asyncio
import os
from typing import List
from dotenv import load_dotenv
from agent_framework import AIFunction
from agent_framework.azure import AzureOpenAIChatClient

from azure.ai.agentserver.agentframework import from_agent_framework
from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider

load_dotenv()


def create_agent_factory():
    """Create a factory function that builds an agent with ToolClient.

    This function returns a factory that takes a ToolClient and returns
    an AgentProtocol. The agent is created at runtime for every request,
    allowing it to access the latest tool configuration dynamically.
    """

    async def agent_factory(tools: List[AIFunction]) -> AzureOpenAIChatClient:
        """Factory function that creates an agent using the provided tools.

        :param tools: The list of AIFunction tools available to the agent.
        :type tools: List[AIFunction]
        :return: An Agent Framework ChatAgent instance.
        :rtype: ChatAgent
        """
        # List all available tools from the ToolClient
        print("Fetching tools from Azure AI Tool Client via factory...")
        print(f"Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - tool: {tool.name}, description: {tool.description}")

        if not tools:
            print("\nNo tools found!")
            print("Make sure your Azure AI project has tools configured.")
            raise ValueError("No tools available to create agent")

        azure_credential = DefaultAzureCredential()
        token_provider = get_bearer_token_provider(azure_credential, "https://cognitiveservices.azure.com/.default")
        # Create the Agent Framework agent with the tools
        print("\nCreating Agent Framework agent with tools from factory...")
        agent = AzureOpenAIChatClient(ad_token_provider=token_provider).create_agent(
            name="ToolClientAgent",
            instructions="You are a helpful assistant with access to various tools.",
            tools=tools,
        )

        print("Agent created successfully!")
        return agent

    return agent_factory


async def quickstart():
    """Build and return an AgentFrameworkCBAgent using an agent factory function."""

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

    # Create a factory function that will build the agent at runtime
    # The factory will receive a ToolClient when the agent first runs
    agent_factory = create_agent_factory()

    tool_connection_id = os.getenv("AZURE_AI_PROJECT_TOOL_CONNECTION_ID")
    # Pass the factory function to from_agent_framework instead of a compiled agent
    # The agent will be created on every agent run with access to ToolClient
    print("Creating Agent Framework adapter with factory function...")
    adapter = from_agent_framework(
        agent_factory,
        credentials=credential,
        tools=[
            {"type": "mcp", "project_connection_id": tool_connection_id}

            ]
    )

    print("Adapter created! Agent will be built on every request.")
    return adapter


async def main():  # pragma: no cover - sample entrypoint
    """Main function to run the agent."""
    adapter = await quickstart()

    if adapter:
        print("\nStarting agent server...")
        print("The agent factory will be called for every request that arrives.")
        await adapter.run_async()


if __name__ == "__main__":
    asyncio.run(main())
 
