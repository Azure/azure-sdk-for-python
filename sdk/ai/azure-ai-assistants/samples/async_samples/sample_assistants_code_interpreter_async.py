# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use code interpreter tool with assistant from
    the Azure Assistants service using a asynchronous client.

USAGE:
    python sample_assistants_code_interpreter_async.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity aiohttp

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
"""
import asyncio

from azure.ai.assistants.aio import AssistantsClient
from azure.ai.assistants.models import CodeInterpreterTool, FilePurpose, ListSortOrder, MessageRole
from azure.identity.aio import DefaultAzureCredential
from pathlib import Path

import os


async def main() -> None:

    async with DefaultAzureCredential() as creds:

        async with AssistantsClient.from_connection_string(
            credential=creds, conn_str=os.environ["PROJECT_CONNECTION_STRING"]
        ) as assistants_client:
            # Upload a file and wait for it to be processed
            file = await assistants_client.upload_file_and_poll(
                file_path="../nifty_500_quarterly_results.csv", purpose=FilePurpose.ASSISTANTS
            )
            print(f"Uploaded file, file ID: {file.id}")

            code_interpreter = CodeInterpreterTool(file_ids=[file.id])

            assistant = await assistants_client.create_assistant(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-assistant",
                instructions="You are helpful assistant",
                tools=code_interpreter.definitions,
                tool_resources=code_interpreter.resources,
            )
            print(f"Created assistant, assistant ID: {assistant.id}")

            thread = await assistants_client.create_thread()
            print(f"Created thread, thread ID: {thread.id}")

            message = await assistants_client.create_message(
                thread_id=thread.id,
                role="user",
                content="Could you please create bar chart in TRANSPORTATION sector for the operating profit from the uploaded csv file and provide file to me?",
            )
            print(f"Created message, message ID: {message.id}")

            run = await assistants_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)
            print(f"Run finished with status: {run.status}")

            if run.status == "failed":
                # Check if you got "Rate limit is exceeded.", then you want to get more quota
                print(f"Run failed: {run.last_error}")

            messages = await assistants_client.list_messages(thread_id=thread.id, order=ListSortOrder.ASCENDING)
            print(f"Messages: {messages}")

            last_msg = messages.get_last_text_message_by_role(MessageRole.ASSISTANT)
            if last_msg:
                print(f"Last Message: {last_msg.text.value}")

            for image_content in messages.image_contents:
                print(f"Image File ID: {image_content.image_file.file_id}")
                file_name = f"{image_content.image_file.file_id}_image_file.png"
                await assistants_client.save_file(file_id=image_content.image_file.file_id, file_name=file_name)
                print(f"Saved image file to: {Path.cwd() / file_name}")

            for file_path_annotation in messages.file_path_annotations:
                print(f"File Paths:")
                print(f"Type: {file_path_annotation.type}")
                print(f"Text: {file_path_annotation.text}")
                print(f"File ID: {file_path_annotation.file_path.file_id}")
                print(f"Start Index: {file_path_annotation.start_index}")
                print(f"End Index: {file_path_annotation.end_index}")
                file_name = Path(file_path_annotation.text).name
                await assistants_client.save_file(file_id=file_path_annotation.file_path.file_id, file_name=file_name)
                print(f"Saved image file to: {Path.cwd() / file_name}")

            await assistants_client.delete_assistant(assistant.id)
            print("Deleted assistant")


if __name__ == "__main__":
    asyncio.run(main())
