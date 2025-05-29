# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to add files to agent during the vector store creation.

USAGE:
    python sample_agents_enterprise_file_search.py

    Before running the sample:

    pip install azure-ai-agents azure-identity azure-ai-ml

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
from azure.ai.agents.models import FileSearchTool, ListSortOrder, VectorStoreDataSource, VectorStoreDataSourceAssetType
from azure.identity import DefaultAzureCredential

agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with agents_client:

    # [START upload_file_and_create_agent_with_file_search]
    # We will upload the local file to Azure and will use it for vector store creation.
    asset_uri = os.environ["AZURE_BLOB_URI"]

    # Create a vector store with no file and wait for it to be processed
    ds = VectorStoreDataSource(asset_identifier=asset_uri, asset_type=VectorStoreDataSourceAssetType.URI_ASSET)
    vector_store = agents_client.vector_stores.create_and_poll(data_sources=[ds], name="sample_vector_store")
    print(f"Created vector store, vector store ID: {vector_store.id}")

    # Create a file search tool
    file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])

    # Notices that FileSearchTool as tool and tool_resources must be added or the agent unable to search the file
    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are helpful agent",
        tools=file_search_tool.definitions,
        tool_resources=file_search_tool.resources,
    )
    # [END upload_file_and_create_agent_with_file_search]
    print(f"Created agent, agent ID: {agent.id}")

    thread = agents_client.threads.create()
    print(f"Created thread, thread ID: {thread.id}")

    message = agents_client.messages.create(
        thread_id=thread.id, role="user", content="What feature does Smart Eyewear offer?"
    )
    print(f"Created message, message ID: {message.id}")

    run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    print(f"Created run, run ID: {run.id}")

    agents_client.vector_stores.delete(vector_store.id)
    print("Deleted vector store")

    agents_client.delete_agent(agent.id)
    print("Deleted agent")

    messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1]
            print(f"{msg.role}: {last_text.text.value}")
