# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to use assistant operations to add files to an existing vector store and perform search from
    the Azure Assistants service using a synchronous client.

USAGE:
    python sample_assistants_vector_store_batch_enterprise_file_search_async.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity azure-ai-ml aiohttp

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
"""
import asyncio
import os

from azure.ai.assistants.aio import AssistantsClient
from azure.ai.assistants.models import (
    FileSearchTool,
    VectorStoreDataSource,
    VectorStoreDataSourceAssetType,
)
from azure.identity.aio import DefaultAzureCredential


async def main():

    async with DefaultAzureCredential() as credential:
        async with AssistantsClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=creds,
        ) as assistants_client:
            # We will upload the local file to Azure and will use it for vector store creation.
            asset_uri = os.environ["AZURE_BLOB_URI"]
            ds = VectorStoreDataSource(
                asset_identifier=asset_uri,
                asset_type=VectorStoreDataSourceAssetType.URI_ASSET,
            )
            vector_store = await assistants_client.create_vector_store_and_poll(file_ids=[], name="sample_vector_store")
            print(f"Created vector store, vector store ID: {vector_store.id}")

            # Add the file to the vector store or you can supply file ids in the vector store creation
            vector_store_file_batch = await assistants_client.create_vector_store_file_batch_and_poll(
                vector_store_id=vector_store.id, data_sources=[ds]
            )
            print(f"Created vector store file batch, vector store file batch ID: {vector_store_file_batch.id}")

            # Create a file search tool
            file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])

            # Notices that FileSearchTool as tool and tool_resources must be added or the assistant unable to search the file
            assistant = await assistants_client.create_assistant(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-assistant",
                instructions="You are helpful assistant",
                tools=file_search_tool.definitions,
                tool_resources=file_search_tool.resources,
            )
            print(f"Created assistant, assistant ID: {assistant.id}")

            thread = await assistants_client.create_thread()
            print(f"Created thread, thread ID: {thread.id}")

            message = await assistants_client.create_message(
                thread_id=thread.id,
                role="user",
                content="What feature does Smart Eyewear offer?",
            )
            print(f"Created message, message ID: {message.id}")

            run = await assistants_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)
            print(f"Created run, run ID: {run.id}")

            file_search_tool.remove_vector_store(vector_store.id)
            print(f"Removed vector store from file search, vector store ID: {vector_store.id}")

            await assistants_client.update_assistant(
                assistant_id=assistant.id,
                tools=file_search_tool.definitions,
                tool_resources=file_search_tool.resources,
            )
            print(f"Updated assistant, assistant ID: {assistant.id}")

            thread = await assistants_client.create_thread()
            print(f"Created thread, thread ID: {thread.id}")

            message = await assistants_client.create_message(
                thread_id=thread.id,
                role="user",
                content="What feature does Smart Eyewear offer?",
            )
            print(f"Created message, message ID: {message.id}")

            run = await assistants_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)
            print(f"Created run, run ID: {run.id}")

            await assistants_client.delete_vector_store(vector_store.id)
            print("Deleted vector store")

            await assistants_client.delete_assistant(assistant.id)
            print("Deleted assistant")

            messages = await assistants_client.list_messages(thread_id=thread.id)
            print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
