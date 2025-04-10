# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_assistants_fabric.py

DESCRIPTION:
    This sample demonstrates how to use Assistant operations with the Microsoft Fabric grounding tool from
    the Azure Assistants service using a synchronous client.

USAGE:
    python sample_assistants_fabric.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""

import os
from azure.ai.assistants import AssistantsClient
from azure.identity import DefaultAzureCredential
from azure.ai.assistants.models import FabricTool

assistants_client = AssistantsClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

# [START create_assistant_with_fabric_tool]
conn_id = os.environ['FABRIC_CONNECTION_ID']

print(conn_id)

# Initialize an Assistant Fabric tool and add the connection id
fabric = FabricTool(connection_id=conn_id)

# Create an Assistant with the Fabric tool and process an Assistant run
with assistants_client:
    assistant = assistants_client.create_assistant(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-assistant",
        instructions="You are a helpful assistant",
        tools=fabric.definitions,
        headers={"x-ms-enable-preview": "true"},
    )
    # [END create_assistant_with_fabric_tool]
    print(f"Created Assistant, ID: {assistant.id}")

    # Create thread for communication
    thread = assistants_client.create_thread()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = assistants_client.create_message(
        thread_id=thread.id,
        role="user",
        content="<User query against Fabric resource>",
    )
    print(f"Created message, ID: {message.id}")

    # Create and process an Assistant run in thread with tools
    run = assistants_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Delete the Assistant when done
    assistants_client.delete_assistant(assistant.id)
    print("Deleted assistant")

    # Fetch and log all messages
    messages = assistants_client.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
