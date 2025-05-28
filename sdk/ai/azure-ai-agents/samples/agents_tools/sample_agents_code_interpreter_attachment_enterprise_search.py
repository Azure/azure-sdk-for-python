# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with code interpreter from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_code_interpreter_attachment_enterprise_search.py

    Before running the sample:

    pip install azure-ai-agents azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) AZURE_BLOB_URI - The URI of the blob storage where the file is uploaded. In the format:
         azureml://subscriptions/{subscription-id}/resourcegroups/{resource-group-name}/workspaces/{workspace-name}/datastores/{datastore-name}/paths/{path-to-file}
"""

import os
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    CodeInterpreterTool,
    MessageAttachment,
    MessageRole,
    VectorStoreDataSource,
    VectorStoreDataSourceAssetType,
)
from azure.identity import DefaultAzureCredential

agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with agents_client:

    code_interpreter = CodeInterpreterTool()

    # notice that CodeInterpreter must be enabled in the agent creation, otherwise the agent will not be able to see the file attachment
    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are helpful agent",
        tools=code_interpreter.definitions,
    )
    print(f"Created agent, agent ID: {agent.id}")

    thread = agents_client.threads.create()
    print(f"Created thread, thread ID: {thread.id}")

    # [START upload_file_and_create_message_with_code_interpreter]
    # We will upload the local file to Azure and will use it for vector store creation.
    asset_uri = os.environ["AZURE_BLOB_URI"]
    ds = VectorStoreDataSource(asset_identifier=asset_uri, asset_type=VectorStoreDataSourceAssetType.URI_ASSET)

    # Create a message with the attachment
    attachment = MessageAttachment(data_source=ds, tools=code_interpreter.definitions)
    message = agents_client.messages.create(
        thread_id=thread.id, role="user", content="What does the attachment say?", attachments=[attachment]
    )
    # [END upload_file_and_create_message_with_code_interpreter]

    print(f"Created message, message ID: {message.id}")

    run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        # Check if you got "Rate limit is exceeded.", then you want to get more quota
        print(f"Run failed: {run.last_error}")

    agents_client.delete_agent(agent.id)
    print("Deleted agent")

    last_msg = agents_client.messages.get_last_message_text_by_role(thread_id=thread.id, role=MessageRole.AGENT)
    if last_msg:
        print(f"Last Message: {last_msg.text.value}")
