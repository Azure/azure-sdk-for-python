# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use assistant operations with toolset from
    the Azure Assistants service using a synchronous client.

USAGE:
    python sample_assistants_run_with_toolset_async.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity aiohttp

    Set this environment variables with your own values:
    PROJECT_ENDPOINT - the Azure AI Assistants endpoint.
"""

import os, asyncio
from azure.ai.assistants.aio import AssistantsClient
from azure.identity.aio import DefaultAzureCredential
from azure.ai.assistants.models import AsyncFunctionTool, AsyncToolSet
from user_async_functions import user_async_functions


async def main() -> None:

    async with DefaultAzureCredential() as creds:
        async with AssistantsClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=creds,
        ) as assistants_client:

            # Initialize assistant toolset with user functions and code interpreter
            # [START create_assistant_with_async_function_tool]
            functions = AsyncFunctionTool(user_async_functions)

            toolset = AsyncToolSet()
            toolset.add(functions)

            assistant = await assistants_client.create_assistant(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-assistant",
                instructions="You are a helpful assistant",
                toolset=toolset,
            )
            # [END create_assistant_with_async_function_tool]
            print(f"Created assistant, ID: {assistant.id}")

            # Create thread for communication
            thread = await assistants_client.create_thread()
            print(f"Created thread, ID: {thread.id}")

            # Create message to thread
            message = await assistants_client.create_message(
                thread_id=thread.id,
                role="user",
                content="Hello, send an email with the datetime and weather information in New York?",
            )
            print(f"Created message, ID: {message.id}")

            # Create and process assistant run in thread with tools
            run = await assistants_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)
            print(f"Run finished with status: {run.status}")

            if run.status == "failed":
                print(f"Run failed: {run.last_error}")

            # Delete the assistant when done
            await assistants_client.delete_assistant(assistant.id)
            print("Deleted assistant")

            # Fetch and log all messages
            messages = await assistants_client.list_messages(thread_id=thread.id)
            print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
