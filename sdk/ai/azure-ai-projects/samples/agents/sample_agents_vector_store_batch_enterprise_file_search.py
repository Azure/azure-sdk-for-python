# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
FILE: sample_agents_vector_store_batch_enterprise_file_search.py

DESCRIPTION:
    This sample demonstrates how to create the vector store with the list of files.

USAGE:
    python sample_agents_vector_store_batch_enterprise_file_search.py

    Before running the sample:

    pip install azure-ai-projects azure-identity azure-ai-ml

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FileSearchTool, VectorStoreDataSource, VectorStoreDataSourceAssetType
from azure.identity import DefaultAzureCredential


# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables

credential = DefaultAzureCredential()
project_client = AIProjectClient.from_connection_string(
    credential=credential, conn_str=os.environ["PROJECT_CONNECTION_STRING"]
)

with project_client:

    # We will upload the local file to Azure and will use it for vector store creation.
    _, asset_uri = project_client.upload_file("./product_info_1.md")

    # create a vector store with no file and wait for it to be processed
    vector_store = project_client.agents.create_vector_store_and_poll(data_sources=[], name="sample_vector_store")
    print(f"Created vector store, vector store ID: {vector_store.id}")

    ds = VectorStoreDataSource(asset_identifier=asset_uri, asset_type=VectorStoreDataSourceAssetType.URI_ASSET)
    # add the file to the vector store or you can supply data sources in the vector store creation
    vector_store_file_batch = project_client.agents.create_vector_store_file_batch_and_poll(
        vector_store_id=vector_store.id, data_sources=[ds]
    )
    print(f"Created vector store file batch, vector store file batch ID: {vector_store_file_batch.id}")

    # create a file search tool
    file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])

    # notices that FileSearchTool as tool and tool_resources must be added or the assistant unable to search the file
    agent = project_client.agents.create_agent(
        model="gpt-4-1106-preview",
        name="my-assistant",
        instructions="You are helpful assistant",
        tools=file_search_tool.definitions,
        tool_resources=file_search_tool.resources,
    )
    print(f"Created agent, agent ID: {agent.id}")

    thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID: {thread.id}")

    message = project_client.agents.create_message(
        thread_id=thread.id, role="user", content="What feature does Smart Eyewear offer?"
    )
    print(f"Created message, message ID: {message.id}")

    run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    print(f"Created run, run ID: {run.id}")

    file_search_tool.remove_vector_store(vector_store.id)
    print(f"Removed vector store from file search, vector store ID: {vector_store.id}")

    project_client.agents.update_agent(
        assistant_id=agent.id, tools=file_search_tool.definitions, tool_resources=file_search_tool.resources
    )
    print(f"Updated agent, agent ID: {agent.id}")

    thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID: {thread.id}")

    message = project_client.agents.create_message(
        thread_id=thread.id, role="user", content="What feature does Smart Eyewear offer?"
    )
    print(f"Created message, message ID: {message.id}")

    run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    print(f"Created run, run ID: {run.id}")

    project_client.agents.delete_vector_store(vector_store.id)
    print("Deleted vector store")

    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    messages = project_client.agents.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
