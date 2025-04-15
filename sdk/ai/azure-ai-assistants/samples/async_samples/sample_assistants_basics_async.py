# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use basic assistant operations from
    the Azure Assistants service using a asynchronous client.

USAGE:
    python sample_assistants_basics_async.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity aiohttp

    Set this environment variables with your own values:
    PROJECT_ENDPOINT - the Azure AI Assistants endpoint.
"""
import asyncio
import time

from azure.ai.assistants.aio import AssistantsClient
from azure.ai.assistants.models import ListSortOrder
from azure.identity.aio import DefaultAzureCredential

import os


async def main() -> None:

    async with DefaultAzureCredential() as creds:
        assistant_client = AssistantsClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=creds,
        )

        async with assistant_client:
            assistant = await assistant_client.create_assistant(
                model=os.environ["MODEL_DEPLOYMENT_NAME"], name="my-assistant", instructions="You are helpful assistant"
            )
            print(f"Created assistant, assistant ID: {assistant.id}")

            thread = await assistant_client.create_thread()
            print(f"Created thread, thread ID: {thread.id}")

            message = await assistant_client.create_message(
                thread_id=thread.id, role="user", content="Hello, tell me a joke"
            )
            print(f"Created message, message ID: {message.id}")

            run = await assistant_client.create_run(thread_id=thread.id, assistant_id=assistant.id)

            # Poll the run as long as run status is queued or in progress
            while run.status in ["queued", "in_progress", "requires_action"]:
                # Wait for a second
                time.sleep(1)
                run = await assistant_client.get_run(thread_id=thread.id, run_id=run.id)

                print(f"Run status: {run.status}")

            print(f"Run completed with status: {run.status}")

            await assistant_client.delete_assistant(assistant.id)
            print("Deleted assistant")

            messages = await assistant_client.list_messages(thread_id=thread.id, order=ListSortOrder.ASCENDING)
            print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
