# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_azure_functions.py
 
DESCRIPTION:
    This sample demonstrates how to use azure function agent operations from
    the Azure Agents service using a synchronous client.
 
USAGE:
    python sample_agents_azure_functions.py
 
    Before running the sample:
 
    pip install azure-ai-projects azure-identity
 
    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AzureFunctionDefinition,
    AzureFunctionToolDefinition,
    AzureFunctionStorageQueue,
    AzureStorageQueueBinding,
    FunctionDefinition,
)
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(exclude_managed_identity_credential=True, exclude_environment_credential=True),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

with project_client:

    storage_queue_uri = os.environ["STORAGE_QUEUE_URI"]
    agent = project_client.agents.create_agent(
        model="gpt-4",
        name="azure-function-agent-foo",
        instructions=f"You are a helpful support agent. Use the provided function any time the prompt contains the string 'What would foo say?'. When you invoke the function, ALWAYS specify the output queue uri parameter as '{storage_queue_uri}/azure-function-tool-output'. Always responds with \"Foo says\" and then the response from the tool.",
        headers={"x-ms-enable-preview": "true"},
        tools=[
            AzureFunctionToolDefinition(
                azure_function=AzureFunctionDefinition(
                    function=FunctionDefinition(
                        name="foo",
                        description="Get answers from the foo bot.",
                        parameters={
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "The question to ask."},
                                "outputqueueuri": {"type": "string", "description": "The full output queue uri."},
                            },
                        },
                    ),
                    input_binding=AzureStorageQueueBinding(
                        storage_queue=AzureFunctionStorageQueue(
                            queue_name="azure-function-foo-input",
                            storage_queue_uri=storage_queue_uri,
                        )
                    ),
                    output_binding=AzureStorageQueueBinding(
                        storage_queue=AzureFunctionStorageQueue(
                            queue_name="azure-function-tool-output",
                            storage_queue_uri=storage_queue_uri,
                        )
                    ),
                )
            )
        ],
    )
    print(f"Created agent, agent ID: {agent.id}")

    # Create a thread
    thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID: {thread.id}")

    # Create a message
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="What is the most prevalent element in the universe? What would foo say?",
    )
    print(f"Created message, message ID: {message.id}")

    run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Get messages from the thread
    messages = project_client.agents.get_messages(thread_id=thread.id)
    print(f"Messages: {messages}")

    # Get the last message from the sender
    last_msg = messages.get_last_text_message_by_sender("assistant")
    if last_msg:
        print(f"Last Message: {last_msg.text.value}")

    # Delete the agent once done
    result = project_client.agents.delete_agent(agent.id)
    if result.deleted:
        print(f"Deleted agent {result.id}")
    else:
        print(f"Failed to delete agent {result.id}")
