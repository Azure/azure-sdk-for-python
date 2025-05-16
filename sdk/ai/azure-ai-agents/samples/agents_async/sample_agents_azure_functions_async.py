# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio

"""
DESCRIPTION:
    This sample demonstrates how to use azure function agent operations from
    the Azure Agents service using a asynchronous client.
 
USAGE:
    python sample_agents_azure_functions_async.py
 
    Before running the sample:
 
    pip install azure-ai-projects azure-identity
 
    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview 
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) STORAGE_SERVICE_ENDPONT - the storage service queue endpoint, triggering Azure function.

    Please see Getting Started with Azure Functions page for more information on Azure Functions:
    https://learn.microsoft.com/azure/azure-functions/functions-get-started
"""

import os
from azure.ai.agents.aio import AgentsClient
from azure.identity.aio import DefaultAzureCredential
from azure.ai.agents.models import (
    AzureFunctionStorageQueue,
    AzureFunctionTool,
    MessageRole,
)


async def main():

    async with DefaultAzureCredential(
        exclude_managed_identity_credential=True, exclude_environment_credential=True
    ) as creds:
        async with AgentsClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=creds,
        ) as agents_client:

            storage_service_endpoint = os.environ["STORAGE_SERVICE_ENDPONT"]
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

            agent = await agents_client.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="azure-function-agent-foo",
                instructions=f"You are a helpful support agent. Use the provided function any time the prompt contains the string 'What would foo say?'. When you invoke the function, ALWAYS specify the output queue uri parameter as '{storage_service_endpoint}/azure-function-tool-output'. Always responds with \"Foo says\" and then the response from the tool.",
                tools=azure_function_tool.definitions,
            )
            print(f"Created agent, agent ID: {agent.id}")

            # Create a thread
            thread = await agents_client.threads.create()
            print(f"Created thread, thread ID: {thread.id}")

            # Create a message
            message = await agents_client.messages.create(
                thread_id=thread.id,
                role="user",
                content="What is the most prevalent element in the universe? What would foo say?",
            )
            print(f"Created message, message ID: {message.id}")

            run = await agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
            if run.status == "failed":
                print(f"Run failed: {run.last_error}")

            # Get the last message from the sender
            last_msg = await agents_client.messages.get_last_message_text_by_role(
                thread_id=thread.id, role=MessageRole.AGENT
            )
            if last_msg:
                print(f"Last Message: {last_msg.text.value}")

            # Delete the agent once done
            await agents_client.delete_agent(agent.id)


if __name__ == "__main__":
    asyncio.run(main())
