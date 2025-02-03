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

    pip install azure-ai-projects azure-identity aiohttp

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
"""

import os, asyncio
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.models import AsyncFunctionTool, AsyncToolSet
from user_async_functions import user_async_functions


async def main() -> None:

    async with DefaultAzureCredential() as creds:
        async with AIProjectClient.from_connection_string(
            credential=creds,
            conn_str=os.environ["PROJECT_CONNECTION_STRING"],
        ) as project_client:

            # Initialize agent toolset with user functions and code interpreter
            # [START create_agent_with_async_function_tool]
            functions = AsyncFunctionTool(user_async_functions)

            toolset = AsyncToolSet()
            toolset.add(functions)

            agent = await project_client.agents.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-assistant",
                instructions="You are a helpful assistant",
                toolset=toolset,
            )
            # [END create_agent_with_async_function_tool]
            print(f"Created agent, ID: {agent.id}")

            # Create thread for communication
            thread = await project_client.agents.create_thread()
            print(f"Created thread, ID: {thread.id}")

            # Create message to thread
            message = await project_client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content="Hello, send an email with the datetime and weather information in New York?",
            )
            print(f"Created message, ID: {message.id}")

            # Create and process agent run in thread with tools
            run = await project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
            print(f"Run finished with status: {run.status}")

            if run.status == "failed":
                print(f"Run failed: {run.last_error}")

            # Delete the assistant when done
            await project_client.agents.delete_agent(agent.id)
            print("Deleted agent")

            # Fetch and log all messages
            messages = await project_client.agents.list_messages(thread_id=thread.id)
            print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
