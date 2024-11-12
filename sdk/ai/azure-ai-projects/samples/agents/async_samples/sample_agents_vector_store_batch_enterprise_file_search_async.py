# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
FILE: sample_agents_vector_store_batch_enterprise_file_search_async.py

DESCRIPTION:
    This sample demonstrates how to use agent operations to add files to an existing vector store and perform search from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_vector_store_batch_enterprise_file_search_async.py

    Before running the sample:

    pip install azure-ai-projects azure-identity azure-ai-ml

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""
import asyncio
import os

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    FileSearchTool,
    VectorStoreDataSource,
    VectorStoreDataSourceAssetType,
)
from azure.identity.aio import DefaultAzureCredential


async def main():
    # Create an Azure AI Client from a connection string, copied from your AI Studio project.
    # At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
    # Customer needs to login to Azure subscription via Azure CLI and set the environment variables

    credential = DefaultAzureCredential()
    project_client = AIProjectClient.from_connection_string(
        credential=credential, conn_str=os.environ["PROJECT_CONNECTION_STRING"]
    )

    async with project_client:

        # We will upload the local file to Azure and will use it for vector store creation.
        _, asset_uri = project_client.upload_file("../product_info_1.md")
        ds = VectorStoreDataSource(
            asset_identifier=asset_uri,
            asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
        )
        vector_store = await project_client.agents.create_vector_store_and_poll(file_ids=[], name="sample_vector_store")
        print(f"Created vector store, vector store ID: {vector_store.id}")

        # add the file to the vector store or you can supply file ids in the vector store creation
        vector_store_file_batch = await project_client.agents.create_vector_store_file_batch_and_poll(
            vector_store_id=vector_store.id, data_sources=[ds]
        )
        print(f"Created vector store file batch, vector store file batch ID: {vector_store_file_batch.id}")

        # create a file search tool
        file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])

        # notices that FileSearchTool as tool and tool_resources must be added or the assistant unable to search the file
        agent = await project_client.agents.create_agent(
            model="gpt-4-1106-preview",
            name="my-assistant",
            instructions="You are helpful assistant",
            tools=file_search_tool.definitions,
            tool_resources=file_search_tool.resources,
        )
        print(f"Created agent, agent ID: {agent.id}")

        thread = await project_client.agents.create_thread()
        print(f"Created thread, thread ID: {thread.id}")

        message = await project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content="What feature does Smart Eyewear offer?",
        )
        print(f"Created message, message ID: {message.id}")

        run = await project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
        print(f"Created run, run ID: {run.id}")

        file_search_tool.remove_vector_store(vector_store.id)
        print(f"Removed vector store from file search, vector store ID: {vector_store.id}")

        await project_client.agents.update_agent(
            assistant_id=agent.id,
            tools=file_search_tool.definitions,
            tool_resources=file_search_tool.resources,
        )
        print(f"Updated agent, agent ID: {agent.id}")

        thread = await project_client.agents.create_thread()
        print(f"Created thread, thread ID: {thread.id}")

        message = await project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content="What feature does Smart Eyewear offer?",
        )
        print(f"Created message, message ID: {message.id}")

        run = await project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
        print(f"Created run, run ID: {run.id}")

        await project_client.agents.delete_vector_store(vector_store.id)
        print("Deleted vector store")

        await project_client.agents.delete_agent(agent.id)
        print("Deleted agent")

        messages = await project_client.agents.list_messages(thread_id=thread.id)
        print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
