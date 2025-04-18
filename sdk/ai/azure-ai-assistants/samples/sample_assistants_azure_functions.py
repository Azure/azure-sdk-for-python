# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use azure function assistant operations from
    the Azure Assistants service using a synchronous client.
 
USAGE:
    python sample_assistants_azure_functions.py
 
    Before running the sample:
 
    pip install azure-ai-assistants azure-identity
 
    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - the Azure AI Assistants endpoint.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) STORAGE_SERVICE_ENDPONT - the storage service queue endpoint, triggering Azure function.
       Please see Getting Started with Azure Functions page for more information on Azure Functions:
       https://learn.microsoft.com/azure/azure-functions/functions-get-started
"""

import os
from azure.ai.assistants import AssistantsClient
from azure.ai.assistants.models import AzureFunctionStorageQueue, AzureFunctionTool, MessageRole
from azure.identity import DefaultAzureCredential

assistants_client = AssistantsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with assistants_client:

    storage_service_endpoint = os.environ["STORAGE_SERVICE_ENDPONT"]

    # [START create_assistant_with_azure_function_tool]
    azure_function_tool = AzureFunctionTool(
        name="foo",
        description="Get answers from the foo bot.",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The question to ask."},
                "outputqueueuri": {"type": "string", "description": "The full output queue uri."},
            },
        },
        input_queue=AzureFunctionStorageQueue(
            queue_name="azure-function-foo-input",
            storage_service_endpoint=storage_service_endpoint,
        ),
        output_queue=AzureFunctionStorageQueue(
            queue_name="azure-function-tool-output",
            storage_service_endpoint=storage_service_endpoint,
        ),
    )

    assistant = assistants_client.create_assistant(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="azure-function-assistant-foo",
        instructions=f"You are a helpful support assistant. Use the provided function any time the prompt contains the string 'What would foo say?'. When you invoke the function, ALWAYS specify the output queue uri parameter as '{storage_service_endpoint}/azure-function-tool-output'. Always responds with \"Foo says\" and then the response from the tool.",
        tools=azure_function_tool.definitions,
    )
    print(f"Created assistant, assistant ID: {assistant.id}")
    # [END create_assistant_with_azure_function_tool]

    # Create a thread
    thread = assistants_client.create_thread()
    print(f"Created thread, thread ID: {thread.id}")

    # Create a message
    message = assistants_client.create_message(
        thread_id=thread.id,
        role="user",
        content="What is the most prevalent element in the universe? What would foo say?",
    )
    print(f"Created message, message ID: {message.id}")

    run = assistants_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)
    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Get messages from the thread
    messages = assistants_client.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")

    # Get the last message from assistant
    last_msg = messages.get_last_text_message_by_role(MessageRole.ASSISTANT)
    if last_msg:
        print(f"Last Message: {last_msg.text.value}")

    # Delete the assistant once done
    result = assistants_client.delete_assistant(assistant.id)
    if result.deleted:
        print(f"Deleted assistant {result.id}")
    else:
        print(f"Failed to delete assistant {result.id}")
