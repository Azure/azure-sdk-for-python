# Copyright (c) Microsoft. All rights reserved.
"""Example showing how to use an agent factory function with ToolClient.

This sample demonstrates how to pass a factory function to from_agent_framework
that receives a ToolClient and returns an AgentProtocol. This pattern allows
the agent to be created dynamically with access to tools from Azure AI Tool
Client at runtime.
"""

import os

from agent_framework import Agent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

from azure.ai.agentserver.agentframework import FoundryToolsChatMiddleware, from_agent_framework

load_dotenv()

def main():
    tool_connection_id = os.getenv("AZURE_AI_PROJECT_TOOL_CONNECTION_ID")

    agent = Agent(
        client=AzureOpenAIChatClient(
            credential=AzureCliCredential(),
        ),
        middleware=[
            FoundryToolsChatMiddleware(
                tools=[{"type": "web_search_preview"}, {"type": "mcp", "project_connection_id": tool_connection_id}]
            )
        ],
        name="FoundryToolAgent",
        instructions="You are a helpful assistant with access to various tools.",
    )

    from_agent_framework(agent).run()

if __name__ == "__main__":
    main()
