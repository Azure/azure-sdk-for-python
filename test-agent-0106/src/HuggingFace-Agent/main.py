# Copyright (c) Microsoft. All rights reserved.
"""Example showing how to use an agent factory function with ToolClient.

This sample demonstrates how to pass a factory function to from_agent_framework
that receives a ToolClient and returns an AgentProtocol. This pattern allows
the agent to be created dynamically with access to tools from Azure AI Tool
Client at runtime.
"""

import asyncio
import os
from typing import List, AsyncGenerator
from dotenv import load_dotenv
from agent_framework import AIFunction, AgentProtocol
from agent_framework.azure import AzureOpenAIChatClient

from azure.ai.agentserver.agentframework import from_agent_framework
from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider

load_dotenv()

# Keep-alive interval is 15 seconds, so we need delays > 15s to trigger keep-alive
KEEP_ALIVE_INTERVAL = 15.0
TEST_DELAY_SECONDS = 60.0  # Delay between events to test keep-alive


class DelayedAgentWrapper(AgentProtocol):
    """Wrapper around an agent to add delays for keep-alive testing.
    
    This wrapper adds delays between streaming events to test the keep-alive
    mechanism. If no event is received within 15 seconds, the server will
    send a keep-alive signal.
    """
    
    def __init__(self, agent: AgentProtocol, delay_seconds: float = TEST_DELAY_SECONDS):
        self._agent = agent
        self._delay_seconds = delay_seconds
    
    async def run(self, message):
        """Run the agent in non-streaming mode."""
        return await self._agent.run(message)
    
    async def run_stream(self, message) -> AsyncGenerator:
        """Run the agent in streaming mode with delays for keep-alive testing."""
        print(f"Starting delayed streaming with {self._delay_seconds}s delay between events...")
        print(f"Keep-alive interval is {KEEP_ALIVE_INTERVAL}s, delay is {self._delay_seconds}s")
        
        event_count = 0
        async for event in self._agent.run_stream(message):
            event_count += 1
            print(f"Received event #{event_count}, yielding it...")
            yield event
            
            # Add delay AFTER yielding event to test keep-alive
            # This will trigger keep-alive if delay > 15 seconds
            # Only delay for first few events to avoid too long total time
            if event_count < 5:  # Only delay for first 5 events
                print(f"Waiting {self._delay_seconds}s before next event (to test keep-alive)...")
                await asyncio.sleep(self._delay_seconds)
        print(f"Streaming completed with {event_count} events")


def create_agent_factory():
    """Create a factory function that builds an agent with ToolClient.

    This function returns a factory that takes a ToolClient and returns
    an AgentProtocol. The agent is created at runtime for every request,
    allowing it to access the latest tool configuration dynamically.
    """

    async def agent_factory(tools: List[AIFunction]) -> AgentProtocol:
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
        base_agent = AzureOpenAIChatClient(ad_token_provider=token_provider).create_agent(
            name="ToolClientAgent",
            instructions="You are a helpful assistant with access to various tools.",
            tools=tools,
        )

        # Wrap the agent with delay wrapper for keep-alive testing
        # This will add delays between streaming events to test keep-alive mechanism
        print(f"Wrapping agent with delay wrapper (delay: {TEST_DELAY_SECONDS}s > keep-alive interval: {KEEP_ALIVE_INTERVAL}s)")
        agent = DelayedAgentWrapper(base_agent, delay_seconds=TEST_DELAY_SECONDS)

        print("Agent created and wrapped successfully!")
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
 
