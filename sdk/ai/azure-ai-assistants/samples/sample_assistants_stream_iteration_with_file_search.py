# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use assistant operations with file search tools and iteration in streaming from
    the Azure Assistants service using a synchronous client.

USAGE:
    python sample_assistants_stream_iteration_with_file_search.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - the Azure AI Assistants endpoint.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import os
from azure.ai.assistants import AssistantsClient
from azure.ai.assistants.models import AssistantStreamEvent, FileSearchTool, RunStepDeltaChunk
from azure.ai.assistants.models import MessageDeltaChunk, RunStep, ThreadMessage, ThreadRun
from azure.identity import DefaultAzureCredential

assistants_client = AssistantsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with assistants_client:

    # Upload file and create vector store
    # [START upload_file_create_vector_store_and_assistant_with_file_search_tool]
    file = assistants_client.upload_file_and_poll(file_path="product_info_1.md", purpose="assistants")
    print(f"Uploaded file, file ID: {file.id}")

    vector_store = assistants_client.create_vector_store_and_poll(file_ids=[file.id], name="my_vectorstore")
    print(f"Created vector store, vector store ID: {vector_store.id}")

    # Create file search tool with resources followed by creating assistant
    file_search = FileSearchTool(vector_store_ids=[vector_store.id])

    assistant = assistants_client.create_assistant(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-assistant",
        instructions="Hello, you are helpful assistant and can search information from uploaded files",
        tools=file_search.definitions,
        tool_resources=file_search.resources,
    )
    print(f"Created assistant, assistant ID: {assistant.id}")

    thread = assistants_client.create_thread()
    print(f"Created thread, thread ID {thread.id}")

    message = assistants_client.create_message(
        thread_id=thread.id, role="user", content="What feature does Smart Eyewear offer?"
    )
    print(f"Created message, message ID {message.id}")

    with assistants_client.create_stream(thread_id=thread.id, assistant_id=assistant.id) as stream:

        for event_type, event_data, _ in stream:

            if isinstance(event_data, MessageDeltaChunk):
                print(f"Text delta received: {event_data.text}")

            elif isinstance(event_data, RunStepDeltaChunk):
                print(f"RunStepDeltaChunk received. ID: {event_data.id}.")

            elif isinstance(event_data, ThreadMessage):
                print(f"ThreadMessage created. ID: {event_data.id}, Status: {event_data.status}")
                for annotation in event_data.file_citation_annotations:
                    print(
                        f"Citation {annotation.text} from file ID: {annotation.file_citation.file_id}, start index: {annotation.start_index}, end index: {annotation.end_index}"
                    )

            elif isinstance(event_data, ThreadRun):
                print(f"ThreadRun status: {event_data.status}")

                if event_data.status == "failed":
                    print(f"Run failed. Error: {event_data.last_error}")

            elif isinstance(event_data, RunStep):
                print(f"RunStep type: {event_data.type}, Status: {event_data.status}")

            elif event_type == AssistantStreamEvent.ERROR:
                print(f"An error occurred. Data: {event_data}")

            elif event_type == AssistantStreamEvent.DONE:
                print("Stream completed.")

            else:
                print(f"Unhandled Event Type: {event_type}, Data: {event_data}")

    assistants_client.delete_assistant(assistant.id)
    print("Deleted assistant")

    messages = assistants_client.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
