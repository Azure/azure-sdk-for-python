# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to perform CRUD operations on a memory store
    and on the individual memory items inside it, using the asynchronous
    AIProjectClient.

    Memory store operations: create, get, update, list, delete.
    Memory item operations:  create_memory, get_memory, update_memory,
                             list_memories, delete_memory.

    See also /samples/agents/tools/sample_agent_memory_search_async.py that shows
    how to use the Memory Search Tool in a prompt agent.

USAGE:
    python sample_memory_crud_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv aiohttp

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) MEMORY_STORE_CHAT_MODEL_DEPLOYMENT_NAME - The deployment name of the chat model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) MEMORY_STORE_EMBEDDING_MODEL_DEPLOYMENT_NAME - The deployment name of the embedding model, as found under the
       "Name" column in the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import asyncio
import os
from dotenv import load_dotenv
from azure.core.exceptions import ResourceNotFoundError
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import MemoryItemKind, MemoryStoreDefaultDefinition


async def main() -> None:
    load_dotenv()

    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    memory_store_name = "my_memory_store"
    scope = "user_123"

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):

        # Delete memory store, if it already exists
        try:
            await project_client.beta.memory_stores.delete(memory_store_name)
            print(f"Memory store `{memory_store_name}` deleted")
        except ResourceNotFoundError:
            pass

        # Create memory store
        memory_store = await project_client.beta.memory_stores.create(
            name=memory_store_name,
            description="Example memory store for conversations",
            definition=MemoryStoreDefaultDefinition(
                chat_model=os.environ["MEMORY_STORE_CHAT_MODEL_DEPLOYMENT_NAME"],
                embedding_model=os.environ["MEMORY_STORE_EMBEDDING_MODEL_DEPLOYMENT_NAME"],
            ),
        )
        print(f"Created memory store: {memory_store.name} ({memory_store.id}): {memory_store.description}")

        # Get memory store
        get_store = await project_client.beta.memory_stores.get(memory_store.name)
        print(f"Retrieved: {get_store.name} ({get_store.id}): {get_store.description}")

        # Update memory store
        updated_store = await project_client.beta.memory_stores.update(
            name=memory_store.name,
            description="Updated description",
        )
        print(f"Updated: {updated_store.name} ({updated_store.id}): {updated_store.description}")

        # List memory stores
        memory_stores = [store async for store in project_client.beta.memory_stores.list(limit=10)]
        print(f"Found {len(memory_stores)} memory stores")
        for store in memory_stores:
            print(f"  - {store.name} ({store.id}): {store.description}")

        # Create a memory item
        created_item = await project_client.beta.memory_stores.create_memory(
            memory_store.name,
            scope=scope,
            content="The user prefers responses in concise bullet points.",
            kind=MemoryItemKind.USER_PROFILE,
        )
        print(f"Created memory item: {created_item.memory_id} (kind={created_item.kind}) -> {created_item.content}")

        # Get the memory item
        fetched_item = await project_client.beta.memory_stores.get_memory(memory_store.name, created_item.memory_id)
        print(f"Retrieved memory item: {fetched_item.memory_id} -> {fetched_item.content}")

        # Update the memory item
        updated_item = await project_client.beta.memory_stores.update_memory(
            memory_store.name,
            fetched_item.memory_id,
            content="The user prefers concise bullet points and Python code samples.",
        )
        print(f"Updated memory item: {updated_item.memory_id} -> {updated_item.content}")

        # Add a second memory item, then list items in the scope
        await project_client.beta.memory_stores.create_memory(
            memory_store.name,
            scope=scope,
            content="The user is working on the azure-ai-projects Python SDK.",
            kind=MemoryItemKind.USER_PROFILE,
        )
        items = [
            item
            async for item in project_client.beta.memory_stores.list_memories(memory_store.name, scope=scope, limit=10)
        ]
        print(f"Found {len(items)} memory items in scope '{scope}':")
        for item in items:
            print(f"  - {item.memory_id} ({item.kind}): {item.content}")

        # Delete a memory item
        delete_item_result = await project_client.beta.memory_stores.delete_memory(
            memory_store.name, created_item.memory_id
        )
        print(f"Deleted memory item {created_item.memory_id}: deleted={delete_item_result.deleted}")

        # Delete the memory store
        delete_response = await project_client.beta.memory_stores.delete(memory_store.name)
        print(f"Deleted memory store: {delete_response.deleted}")


if __name__ == "__main__":
    asyncio.run(main())
