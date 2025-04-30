# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use assistant operations to create messages with file search attachments from
    the Azure Assistants service using a asynchronous client.

USAGE:
    python sample_assistants_with_file_search_attachment_async.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity aiohttp

    Set this environment variables with your own values:
    PROJECT_ENDPOINT - the Azure AI Assistants endpoint.
"""
import asyncio

from azure.ai.assistants.aio import AssistantsClient
from azure.ai.assistants.models import FilePurpose
from azure.ai.assistants.models import FileSearchTool, MessageAttachment
from azure.identity.aio import DefaultAzureCredential

import os


async def main() -> None:
    async with DefaultAzureCredential() as creds:
        async with AssistantsClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=creds,
        ) as assistants_client:
            # Upload a file and wait for it to be processed
            file = await assistants_client.upload_file_and_poll(
                file_path="../product_info_1.md", purpose=FilePurpose.ASSISTANTS
            )

            # Create assistant
            assistant = await assistants_client.create_assistant(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-assistant",
                instructions="You are helpful assistant",
            )
            print(f"Created assistant, assistant ID: {assistant.id}")

            thread = await assistants_client.create_thread()
            print(f"Created thread, thread ID: {thread.id}")

            # Create a message with the file search attachment
            # Notice that vector store is created temporarily when using attachments with a default expiration policy of seven days.
            attachment = MessageAttachment(file_id=file.id, tools=FileSearchTool().definitions)
            message = await assistants_client.create_message(
                thread_id=thread.id,
                role="user",
                content="What feature does Smart Eyewear offer?",
                attachments=[attachment],
            )
            print(f"Created message, message ID: {message.id}")

            run = await assistants_client.create_and_process_run(
                thread_id=thread.id, assistant_id=assistant.id, sleep_interval=4
            )
            print(f"Created run, run ID: {run.id}")

            print(f"Run completed with status: {run.status}")

            await assistants_client.delete_file(file.id)
            print("Deleted file")

            await assistants_client.delete_assistant(assistant.id)
            print("Deleted assistant")

            messages = await assistants_client.list_messages(thread_id=thread.id)
            print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
