# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use assistant operations with the Bing Custom Search tool from
    the Azure Assistants service using a synchronous client.
    For more information on the Bing Custom Search tool, see: https://aka.ms/AssistantCustomSearchDoc

USAGE:
    python sample_assistants_bing_custom_search.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity

    Set these environment variables with your own values:
    1) PROJECT_CONNECTION_STRING - The project connection string, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) BING_CUSTOM_CONNECTION_ID - The connection ID of the Bing Custom Search connection, as found in the 
       "Connected resources" tab in your Azure AI Foundry project.
"""

import os
from azure.ai.assistants import AssistantsClient
from azure.ai.assistants.models import MessageRole, BingCustomSearchTool
from azure.identity import DefaultAzureCredential


assistants_client = AssistantsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# [START create_assistant_with_bing_custom_search_tool]
conn_id = os.environ["BING_CUSTOM_CONNECTION_ID"]

print(conn_id)

# Initialize assistant bing custom search tool and add the connection id
bing_custom_tool = BingCustomSearchTool(connection_id=conn_id, instance_name="<config_instance_name>")

# Create assistant with the bing custom search tool and process assistant run
with assistants_client:
    assistant = assistants_client.create_assistant(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-assistant",
        instructions="You are a helpful assistant",
        tools=bing_custom_tool.definitions,
        headers={"x-ms-enable-preview": "true"},
    )
    # [END create_assistant_with_bing_custom_search_tool]

    print(f"Created assistant, ID: {assistant.id}")

    # Create thread for communication
    thread = assistants_client.create_thread()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = assistants_client.create_message(
        thread_id=thread.id,
        role=MessageRole.USER,
        content="How many medals did the USA win in the 2024 summer olympics?",
    )
    print(f"Created message, ID: {message.id}")

    # Create and process assistant run in thread with tools
    run = assistants_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Delete the assistant when done
    assistants_client.delete_assistant(assistant.id)
    print("Deleted assistant")

    # Print the Assistant's response message with optional citation
    response_message = assistants_client.list_messages(thread_id=thread.id).get_last_message_by_role(
        MessageRole.ASSISTANT
    )
    if response_message:
        for text_message in response_message.text_messages:
            print(f"Assistant response: {text_message.text.value}")
        for annotation in response_message.url_citation_annotations:
            print(f"URL Citation: [{annotation.url_citation.title}]({annotation.url_citation.url})")