# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use assistant operations to create messages with file search attachments from
    the Azure Assistants service using a synchronous client.

USAGE:
    python sample_assistants_with_file_search_attachment.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - the Azure AI Assistants endpoint.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""
import os
from azure.ai.assistants import AssistantsClient
from azure.ai.assistants.models import FilePurpose, FileSearchTool, MessageAttachment
from azure.identity import DefaultAzureCredential

assistants_client = AssistantsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with assistants_client:

    # Upload a file and wait for it to be processed
    file = assistants_client.upload_file_and_poll(file_path="product_info_1.md", purpose=FilePurpose.ASSISTANTS)
    print(f"Uploaded file, file ID: {file.id}")

    # Create assistant
    assistant = assistants_client.create_assistant(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-assistant",
        instructions="You are helpful assistant",
    )
    print(f"Created assistant, assistant ID: {assistant.id}")

    thread = assistants_client.create_thread()
    print(f"Created thread, thread ID: {thread.id}")

    # Create a message with the file search attachment
    # Notice that vector store is created temporarily when using attachments with a default expiration policy of seven days.
    # [START create_message_with_attachment]
    attachment = MessageAttachment(file_id=file.id, tools=FileSearchTool().definitions)
    message = assistants_client.create_message(
        thread_id=thread.id, role="user", content="What feature does Smart Eyewear offer?", attachments=[attachment]
    )
    # [END create_message_with_attachment]
    print(f"Created message, message ID: {message.id}")

    run = assistants_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)
    print(f"Created run, run ID: {run.id}")

    assistants_client.delete_file(file.id)
    print("Deleted file")

    assistants_client.delete_assistant(assistant.id)
    print("Deleted assistant")

    messages = assistants_client.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
