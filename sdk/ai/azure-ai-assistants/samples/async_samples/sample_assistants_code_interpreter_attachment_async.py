# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use assistant operations with code interpreter from
    the Azure Assistants service using a synchronous client.

USAGE:
    python sample_assistants_code_interpreter_attachment_async.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity aiohttp

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
"""
import asyncio
import os
from azure.ai.assistants.aio import AssistantsClient
from azure.ai.assistants.models import CodeInterpreterTool, FilePurpose, MessageAttachment, ListSortOrder
from azure.identity.aio import DefaultAzureCredential


async def main():
    async with DefaultAzureCredential() as creds:
        async with AssistantsClient.from_connection_string(
            credential=creds, conn_str=os.environ["PROJECT_CONNECTION_STRING"]
        ) as assistants_client:
            # Upload a file and wait for it to be processed
            file = await assistants_client.upload_file_and_poll(
                file_path="../product_info_1.md", purpose=FilePurpose.ASSISTANTS
            )
            print(f"Uploaded file, file ID: {file.id}")

            code_interpreter = CodeInterpreterTool()

            # Notice that CodeInterpreter must be enabled in the assistant creation, otherwise the assistant will not be able to see the file attachment
            assistant = await assistants_client.create_assistant(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-assistant",
                instructions="You are helpful assistant",
                tools=code_interpreter.definitions,
            )
            print(f"Created assistant, assistant ID: {assistant.id}")

            thread = await assistants_client.create_thread()
            print(f"Created thread, thread ID: {thread.id}")

            # Create a message with the attachment
            attachment = MessageAttachment(file_id=file.id, tools=code_interpreter.definitions)
            message = await assistants_client.create_message(
                thread_id=thread.id, role="user", content="What does the attachment say?", attachments=[attachment]
            )
            print(f"Created message, message ID: {message.id}")

            run = await assistants_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)
            print(f"Run finished with status: {run.status}")

            if run.status == "failed":
                # Check if you got "Rate limit is exceeded.", then you want to get more quota
                print(f"Run failed: {run.last_error}")

            await assistants_client.delete_file(file.id)
            print("Deleted file")

            await assistants_client.delete_assistant(assistant.id)
            print("Deleted assistant")

            messages = await assistants_client.list_messages(thread_id=thread.id, order=ListSortOrder.ASCENDING)
            print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
