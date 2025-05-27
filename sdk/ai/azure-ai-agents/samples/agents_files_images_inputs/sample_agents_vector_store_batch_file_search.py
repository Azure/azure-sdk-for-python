# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to use agent operations to add files to an existing vector store and perform search from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_vector_store_batch_file_search.py

    Before running the sample:

    pip install azure-ai-agents azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import os
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FileSearchTool, FilePurpose, ListSortOrder
from azure.identity import DefaultAzureCredential

asset_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/product_info_1.md"))

agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with agents_client:

    # Upload a file and wait for it to be processed
    file = agents_client.files.upload_and_poll(file_path=asset_file_path, purpose=FilePurpose.AGENTS)
    print(f"Uploaded file, file ID: {file.id}")

    # Create a vector store with no file and wait for it to be processed
    vector_store = agents_client.vector_stores.create_and_poll(data_sources=[], name="sample_vector_store")
    print(f"Created vector store, vector store ID: {vector_store.id}")

    # Add the file to the vector store or you can supply file ids in the vector store creation
    vector_store_file_batch = agents_client.vector_store_file_batches.create_and_poll(
        vector_store_id=vector_store.id, file_ids=[file.id]
    )
    print(f"Created vector store file batch, vector store file batch ID: {vector_store_file_batch.id}")

    # Create a file search tool
    # [START create_agent_with_tools_and_tool_resources]
    file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])

    # Notices that FileSearchTool as tool and tool_resources must be added or the agent unable to search the file
    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are helpful agent",
        tools=file_search_tool.definitions,
        tool_resources=file_search_tool.resources,
    )
    # [END create_agent_with_tools_and_tool_resources]
    print(f"Created agent, agent ID: {agent.id}")

    thread = agents_client.threads.create()
    print(f"Created thread, thread ID: {thread.id}")

    message = agents_client.messages.create(
        thread_id=thread.id, role="user", content="What feature does Smart Eyewear offer?"
    )
    print(f"Created message, message ID: {message.id}")

    run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    print(f"Created run, run ID: {run.id}")

    file_search_tool.remove_vector_store(vector_store.id)
    print(f"Removed vector store from file search, vector store ID: {vector_store.id}")

    agents_client.update_agent(
        agent_id=agent.id, tools=file_search_tool.definitions, tool_resources=file_search_tool.resources
    )
    print(f"Updated agent, agent ID: {agent.id}")

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
