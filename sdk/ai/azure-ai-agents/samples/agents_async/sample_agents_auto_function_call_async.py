# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio

"""
DESCRIPTION:
    This sample demonstrates how to enable automatic function calls by calling `enable_auto_function_calls`
    using an asynchronous client.

USAGE:
    python sample_agents_auto_function_call_async.py

    Before running the sample:

    pip install azure-ai-agents azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview 
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import os, sys
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from azure.ai.agents.models import AsyncFunctionTool, AsyncToolSet, ListSortOrder

from utils.user_async_functions import user_async_functions


async def main() -> None:

    project_client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    async with project_client:
        agents_client = project_client.agents

        # To enable tool calls executed automatically you can pass a functions in one of these types:
        # Set[Callable[..., Any]], _models.AsyncFunctionTool, or _models.AsyncToolSet
        # Example 1:
        #    agents_client.enable_auto_function_calls(user_async_functions)
        # Example 2:
        #   functions = AsyncFunctionTool(user_async_functions)
        #   agents_client.enable_auto_function_calls(functions)
        # Example 3:
        #   functions = AsyncFunctionTool(user_async_functions)
        #   toolset = AsyncToolSet()
        #   toolset.add(functions)
        #   agents_client.enable_auto_function_calls(toolset)
        agents_client.enable_auto_function_calls(user_async_functions)
        # Notices that `enable_auto_function_calls` can be made at any time.

        functions = AsyncFunctionTool(user_async_functions)

        # Initialize agent.
        # Whether you would like the functions to be called automatically or not, it is required to pass functions as tools or toolset.
        # NOTE: To reuse existing agent, fetch it with get_agent(agent_id)
        agent = await agents_client.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name="my-agent",
            instructions="You are a helpful agent",
            tools=functions.definitions,
        )

        print(f"Created agent, ID: {agent.id}")

        # Create thread for communication
        thread = await agents_client.threads.create()
        print(f"Created thread, ID: {thread.id}")

        # Create message to thread
        message = await agents_client.messages.create(
            thread_id=thread.id,
            role="user",
            content="Hello, send an email with the datetime and weather information in New York?",
        )
        print(f"Created message, ID: {message.id}")

        # Create and process agent run in thread with tools
        run = await agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
        print(f"Run finished with status: {run.status}")

        if run.status == "failed":
            print(f"Run failed: {run.last_error}")

        # Clean-up and delete the agent once the run is finished.
        # NOTE: Comment out this line if you plan to reuse the agent later.
        await agents_client.delete_agent(agent.id)
        print("Deleted agent")

        # Fetch and log all messages
        messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
        async for msg in messages:
            if msg.text_messages:
                last_text = msg.text_messages[-1]
                print(f"{msg.role}: {last_text.text.value}")


if __name__ == "__main__":
    asyncio.run(main())
