# Copyright (c) Microsoft. All rights reserved.

"""
Simple Agent with Foundry Managed Checkpointer

This sample demonstrates how to use FoundryCheckpointSaver with a LangGraph
agent to persist checkpoints in Azure AI Foundry.

Foundry managed checkpoints enable graph state to be persisted across
requests, allowing conversations to be paused, resumed, and replayed.

Prerequisites:
    - Set AZURE_AI_PROJECT_ENDPOINT to your Azure AI Foundry project endpoint
      e.g. "https://<resource>.services.ai.azure.com/api/projects/<project-id>"
    - Set AZURE_OPENAI_CHAT_DEPLOYMENT_NAME (defaults to "gpt-4o")
    - Azure credentials configured (e.g. az login)
"""

import asyncio
import os

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI
from azure.identity.aio import AzureCliCredential

from azure.ai.agentserver.langgraph import from_langgraph
from azure.ai.agentserver.langgraph.checkpointer import FoundryCheckpointSaver

load_dotenv()

deployment_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o")
model = AzureChatOpenAI(model=deployment_name)


@tool
def get_word_length(word: str) -> int:
    """Returns the length of a word."""
    return len(word)


@tool
def calculator(expression: str) -> str:
    """Evaluates a mathematical expression."""
    try:
        result = eval(expression)  # noqa: S307
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


tools = [get_word_length, calculator]


def create_agent(checkpointer):
    """Create a react agent with the given checkpointer."""
    from langgraph.prebuilt import create_react_agent

    return create_react_agent(model, tools, checkpointer=checkpointer)


async def main() -> None:
    """Run the agent with Foundry managed checkpoints."""
    project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "")

    async with AzureCliCredential() as cred:
        # Use FoundryCheckpointSaver for Azure AI Foundry managed storage.
        # This persists graph checkpoints remotely, enabling pause/resume
        # across requests and server restarts.
        saver = FoundryCheckpointSaver(
            project_endpoint=project_endpoint,
            credential=cred,
        )

        # Pass the checkpointer via LangGraph's native compile/create API
        executor = create_agent(checkpointer=saver)

        await from_langgraph(executor).run_async()


if __name__ == "__main__":
    asyncio.run(main())
