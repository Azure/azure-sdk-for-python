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

    pip install azure-ai-projects azure-ai-agents azure-identity azure-ai-ml

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) AZURE_BLOB_URI - The URI of the blob storage where the file is uploaded. In the format:
         azureml://subscriptions/{subscription-id}/resourcegroups/{resource-group-name}/workspaces/{workspace-name}/datastores/{datastore-name}/paths/{path-to-file}
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import (
    FileSearchTool,
    ListSortOrder,
    VectorStoreDataSource,
    VectorStoreDataSourceAssetType,
    RunStatus,
)
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:
    agents_client = project_client.agents

    # [START upload_file_and_create_agent_with_file_search]
    # If provided, we will upload the local file to Azure and will use it for vector store creation.
    # Otherwise, we'll use a previously created dataset reference
    if "AZURE_BLOB_URI" in os.environ:
        asset_uri = os.environ["AZURE_BLOB_URI"]
    else:
        dataset_name = os.environ["AZURE_DATASET_NAME"]
        dataset_version = os.environ["AZURE_DATASET_VERSION"]
        dataset = project_client.datasets.get(name=dataset_name, version=dataset_version)
        asset_uri = dataset.id

    # Create a vector store and wait for it to be processed
    ds = VectorStoreDataSource(asset_identifier=asset_uri, asset_type=VectorStoreDataSourceAssetType.URI_ASSET)
    vector_store = agents_client.vector_stores.create_and_poll(data_sources=[ds], name="sample_vector_store")
    print(f"Created vector store, vector store ID: {vector_store.id}")
    vector_store_files = {}
    for fle in agents_client.vector_store_files.list(vector_store.id):
        uploaded_file = agents_client.files.get(fle.id)
        vector_store_files[fle.id] = uploaded_file.filename

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
        thread_id=thread.id, role="user", content="What is the content of the files you have access to?"
    )
    print(f"Created message, message ID: {message.id}")

    run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    print(f"Created run, run ID: {run.id}")

    if run.status == RunStatus.FAILED:
        print(f"Run failed with: |{run.last_error}|")

    agents_client.vector_stores.delete(vector_store.id)
    print("Deleted vector store")

    agents_client.delete_agent(agent.id)
    print("Deleted agent")

    messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1].text.value
            for annotation in msg.text_messages[-1].text.annotations:

                citation = vector_store_files.get(annotation.file_citation.file_id, annotation.file_citation.file_id)
                last_text = last_text.replace(annotation.text, f" [{citation}]")
            print(f"{msg.role}: {last_text}")
