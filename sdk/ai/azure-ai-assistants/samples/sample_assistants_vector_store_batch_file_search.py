# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to use assistant operations to add files to an existing vector store and perform search from
    the Azure Assistants service using a synchronous client.

USAGE:
    python sample_assistants_vector_store_batch_file_search.py

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
    vector_store = assistants_client.create_vector_store_and_poll(data_sources=[], name="sample_vector_store")
    print(f"Created vector store, vector store ID: {vector_store.id}")

    # Add the file to the vector store or you can supply file ids in the vector store creation
    vector_store_file_batch = assistants_client.create_vector_store_file_batch_and_poll(
        vector_store_id=vector_store.id, file_ids=[file.id]
    )
    print(f"Created vector store file batch, vector store file batch ID: {vector_store_file_batch.id}")

    # Create a file search tool
    # [START create_assistant_with_tools_and_tool_resources]
    file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])

    # Notices that FileSearchTool as tool and tool_resources must be added or the assistant unable to search the file
    assistant = assistants_client.create_assistant(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-assistant",
        instructions="You are helpful assistant",
        tools=file_search_tool.definitions,
        tool_resources=file_search_tool.resources,
    )
    # [END create_assistant_with_tools_and_tool_resources]
    print(f"Created assistant, assistant ID: {assistant.id}")

    thread = assistants_client.create_thread()
    print(f"Created thread, thread ID: {thread.id}")

    message = assistants_client.create_message(
        thread_id=thread.id, role="user", content="What feature does Smart Eyewear offer?"
    )
    print(f"Created message, message ID: {message.id}")

    run = assistants_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)
    print(f"Created run, run ID: {run.id}")

    file_search_tool.remove_vector_store(vector_store.id)
    print(f"Removed vector store from file search, vector store ID: {vector_store.id}")

    assistants_client.update_assistant(
        assistant_id=assistant.id, tools=file_search_tool.definitions, tool_resources=file_search_tool.resources
    )
    print(f"Updated assistant, assistant ID: {assistant.id}")

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
    print(f"Messages: {messages}")
