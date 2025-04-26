# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with toolset from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_run_with_toolset_async.py

    Before running the sample:

    pip install azure-ai-agents azure-identity aiohttp

    Set this environment variables with your own values:
    PROJECT_ENDPOINT - the Azure AI Agents endpoint.
"""

import os, asyncio
from azure.ai.agents.aio import AgentsClient
from azure.identity.aio import DefaultAzureCredential
from azure.ai.agents.models import AsyncFunctionTool, AsyncToolSet
from utils.user_async_functions import user_async_functions


async def main() -> None:

    async with DefaultAzureCredential() as creds:
        async with AgentsClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=creds,
        ) as agents_client:

            # Initialize agent toolset with user functions and code interpreter
            # [START create_agent_with_async_function_tool]
            functions = AsyncFunctionTool(user_async_functions)

            toolset = AsyncToolSet()
            toolset.add(functions)

            agent = await agents_client.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-agent",
                instructions="You are a helpful agent",
                toolset=toolset,
            )
            # [END create_agent_with_async_function_tool]
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

            # Delete the agent when done
            await agents_client.delete_agent(agent.id)
            print("Deleted agent")

            # Fetch and log all messages
            messages = await agents_client.messages.list(thread_id=thread.id)
            print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
