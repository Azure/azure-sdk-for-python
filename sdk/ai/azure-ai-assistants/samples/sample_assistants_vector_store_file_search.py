# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to add files to assistant during the vector store creation.

USAGE:
    python sample_assistants_vector_store_file_search.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - the Azure AI Assistants endpoint.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import os
from azure.ai.assistants import AssistantsClient
from azure.ai.assistants.models import FileSearchTool, FilePurpose
from azure.identity import DefaultAzureCredential

assistants_client = AssistantsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with assistants_client:

    # Upload a file and wait for it to be processed
    file = assistants_client.upload_file_and_poll(file_path="product_info_1.md", purpose=FilePurpose.ASSISTANTS)
    print(f"Uploaded file, file ID: {file.id}")

    # Create a vector store with no file and wait for it to be processed
    vector_store = assistants_client.create_vector_store_and_poll(file_ids=[file.id], name="sample_vector_store")
    print(f"Created vector store, vector store ID: {vector_store.id}")

    # Create a file search tool
    file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])

    # Notices that FileSearchTool as tool and tool_resources must be added or the assistant unable to search the file
    assistant = assistants_client.create_assistant(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-assistant",
        instructions="You are helpful assistant",
        tools=file_search_tool.definitions,
        tool_resources=file_search_tool.resources,
    )
    print(f"Created assistant, assistant ID: {assistant.id}")

    thread = assistants_client.create_thread()
    print(f"Created thread, thread ID: {thread.id}")

    message = assistants_client.create_message(
        thread_id=thread.id, role="user", content="What feature does Smart Eyewear offer?"
    )
    print(f"Created message, message ID: {message.id}")

    run = assistants_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)
    print(f"Created run, run ID: {run.id}")

    assistants_client.delete_vector_store(vector_store.id)
    print("Deleted vector store")

    assistants_client.delete_assistant(assistant.id)
    print("Deleted assistant")

    messages = assistants_client.list_messages(thread_id=thread.id)

    for message in reversed(messages.data):
        # To remove characters, which are not correctly handled by print, we will encode the message
        # and then decode it again.
        clean_message = "\n".join(
            text_msg.text.value.encode("ascii", "ignore").decode("utf-8") for text_msg in message.text_messages
        )
        print(f"Role: {message.role}  Message: {clean_message}")
