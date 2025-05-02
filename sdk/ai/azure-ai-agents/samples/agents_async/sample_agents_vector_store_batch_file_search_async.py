# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations to add files to an existing vector store and perform search from
    the Azure Agents service using a asynchronous client.

USAGE:
    python sample_agents_vector_store_batch_file_search_async.py

    Before running the sample:

    pip install azure-ai-agents azure-identity aiohttp

    Set this environment variables with your own values:
    PROJECT_ENDPOINT - the Azure AI Agents endpoint.
"""

import asyncio
import os
from azure.ai.agents.aio import AgentsClient
from azure.ai.agents.models import FileSearchTool, FilePurpose, ListSortOrder, MessageTextContent
from azure.identity.aio import DefaultAzureCredential

asset_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/product_info_1.md"))


async def main() -> None:
    async with DefaultAzureCredential() as creds:
        async with AgentsClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=creds,
        ) as agents_client:
            # Upload a file and wait for it to be processed
            file = await agents_client.files.upload_and_poll(file_path=asset_file_path, purpose=FilePurpose.AGENTS)
            print(f"Uploaded file, file ID: {file.id}")

            # Create a vector store with no file and wait for it to be processed
            vector_store = await agents_client.vector_stores.create_and_poll(file_ids=[], name="sample_vector_store")
            print(f"Created vector store, vector store ID: {vector_store.id}")

            # Add the file to the vector store or you can supply file ids in the vector store creation
            vector_store_file_batch = await agents_client.vector_store_file_batches.create_and_poll(
                vector_store_id=vector_store.id, file_ids=[file.id]
            )
            print(f"Created vector store file batch, vector store file batch ID: {vector_store_file_batch.id}")

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

            file_search_tool.remove_vector_store(vector_store.id)
            print(f"Removed vector store from file search, vector store ID: {vector_store.id}")

            await agents_client.update_agent(
                agent_id=agent.id, tools=file_search_tool.definitions, tool_resources=file_search_tool.resources
            )
            print(f"Updated agent, agent ID: {agent.id}")

            thread = await agents_client.threads.create()
            print(f"Created thread, thread ID: {thread.id}")

            message = await agents_client.messages.create(
                thread_id=thread.id, role="user", content="What feature does Smart Eyewear offer?"
            )
            print(f"Created message, message ID: {message.id}")

            run = await agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
            print(f"Created run, run ID: {run.id}")

            await agents_client.files.delete(file.id)
            print("Deleted file")

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
