# pylint: disable=line-too-long,useless-suppression
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

    pip install azure-ai-agents azure-identity azure-ai-ml aiohttp

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model.
"""
import asyncio
import os

from azure.ai.agents.aio import AgentsClient
from azure.ai.agents.models import (
    FileSearchTool,
    VectorStoreDataSource,
    VectorStoreDataSourceAssetType,
    ListSortOrder,
    MessageTextContent,
)
from azure.identity.aio import DefaultAzureCredential


async def main():
    async with DefaultAzureCredential() as credential:
        async with AgentsClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=credential,
        ) as agents_client:
            # We will upload the local file to Azure and will use it for vector store creation.
            asset_uri = os.environ["AZURE_BLOB_URI"]
            ds = VectorStoreDataSource(asset_identifier=asset_uri, asset_type=VectorStoreDataSourceAssetType.URI_ASSET)
            vector_store = await agents_client.vector_stores.create_and_poll(
                data_sources=[ds], name="sample_vector_store"
            )
            print(f"Created vector store, vector store ID: {vector_store.id}")

            # Create a file search tool
            file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])

            # Notices that FileSearchTool as tool and tool_resources must be added or the agent unable to search the file
            agent = await agents_client.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-agent",
                instructions="You are helpful agent",
                tools=file_search_tool.definitions,
                tool_resources=file_search_tool.resources,
            )
            print(f"Created agent, agent ID: {agent.id}")

            thread = await agents_client.threads.create()
            print(f"Created thread, thread ID: {thread.id}")

            message = await agents_client.messages.create(
                thread_id=thread.id, role="user", content="What feature does Smart Eyewear offer?"
            )
            print(f"Created message, message ID: {message.id}")

            run = await agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
            print(f"Created run, run ID: {run.id}")

            await agents_client.vector_stores.delete(vector_store.id)
            print("Deleted vector store")

            await agents_client.delete_agent(agent.id)
            print("Deleted agent")

            messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
            async for msg in messages:
                last_part = msg.content[-1]
                if isinstance(last_part, MessageTextContent):
                    print(f"{msg.role}: {last_part.text.value}")


if __name__ == "__main__":
    asyncio.run(main())
