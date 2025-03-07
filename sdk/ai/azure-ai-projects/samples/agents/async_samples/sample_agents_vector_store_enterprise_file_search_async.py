# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to add files to agent during the vector store creation.

USAGE:
    python sample_agents_vector_store_enterprise_file_search_async.py

    Before running the sample:

    pip install azure-ai-projects azure-identity azure-ai-ml aiohttp

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
"""
import asyncio
import os

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import FileSearchTool, VectorStoreDataSource, VectorStoreDataSourceAssetType
from azure.identity.aio import DefaultAzureCredential


async def main():
    async with DefaultAzureCredential() as credential:
        async with AIProjectClient.from_connection_string(
            credential=credential, conn_str=os.environ["PROJECT_CONNECTION_STRING"]
        ) as project_client:
            # We will upload the local file to Azure and will use it for vector store creation.
            _, asset_uri = project_client.upload_file("../product_info_1.md")
            ds = VectorStoreDataSource(asset_identifier=asset_uri, asset_type=VectorStoreDataSourceAssetType.URI_ASSET)
            vector_store = await project_client.agents.create_vector_store_and_poll(
                data_sources=[ds], name="sample_vector_store"
            )
            print(f"Created vector store, vector store ID: {vector_store.id}")

            # Create a file search tool
            file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])

            # Notices that FileSearchTool as tool and tool_resources must be added or the assistant unable to search the file
            agent = await project_client.agents.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-assistant",
                instructions="You are helpful assistant",
                tools=file_search_tool.definitions,
                tool_resources=file_search_tool.resources,
            )
            print(f"Created agent, agent ID: {agent.id}")

            thread = await project_client.agents.create_thread()
            print(f"Created thread, thread ID: {thread.id}")

            message = await project_client.agents.create_message(
                thread_id=thread.id, role="user", content="What feature does Smart Eyewear offer?"
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
