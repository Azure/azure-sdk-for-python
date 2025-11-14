# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to interact with the memory store to add and retrieve memory
    using the asynchronous AIProjectClient. It uses some additional operations compared
    to the basic memory sample.

    See also /samples/agents/tools/sample_agent_memory_search_async.py that shows
    how to use the Memory Search Tool in a prompt agent.

USAGE:
    python sample_memory_advanced_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity openai python-dotenv aiohttp

    Deploy a chat model (e.g. gpt-4.1) and an embedding model (e.g. text-embedding-3-small).
    Once you have deployed models, set the deployment name in the variables below.

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_CHAT_MODEL_DEPLOYMENT_NAME - The deployment name of the chat model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) AZURE_AI_EMBEDDING_MODEL_DEPLOYMENT_NAME - The deployment name of the embedding model, as found under the
       "Name" column in the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import asyncio
import os
from dotenv import load_dotenv
from azure.core.exceptions import ResourceNotFoundError
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    MemoryStoreDefaultDefinition,
    MemoryStoreDefaultOptions,
    MemorySearchOptions,
    ResponsesUserMessageItemParam,
    ResponsesAssistantMessageItemParam,
)

load_dotenv()


async def main() -> None:

    endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):

        # Delete memory store, if it already exists
        memory_store_name = "my_memory_store"
        try:
            await project_client.memory_stores.delete(memory_store_name)
            print(f"Memory store `{memory_store_name}` deleted")
        except ResourceNotFoundError:
            pass

        # Create memory store with advanced options
        options = MemoryStoreDefaultOptions(
            user_profile_enabled=True,
            user_profile_details="Preferences and interests relevant to coffee expert agent",
            chat_summary_enabled=True,
        )
        definition = MemoryStoreDefaultDefinition(
            chat_model=os.environ["AZURE_AI_CHAT_MODEL_DEPLOYMENT_NAME"],
            embedding_model=os.environ["AZURE_AI_EMBEDDING_MODEL_DEPLOYMENT_NAME"],
            options=options,
        )
        memory_store = await project_client.memory_stores.create(
            name=memory_store_name,
            description="Example memory store for conversations",
            definition=definition,
        )
        print(f"Created memory store: {memory_store.name} ({memory_store.id}): {memory_store.description}")

        # Set scope to associate the memories with.
        # You can also use "{{$userId}}"" to take the oid of the request authentication header.
        scope = "user_123"

        # Extract memories from messages and add them to the memory store
        user_message = ResponsesUserMessageItemParam(
            content="I prefer dark roast coffee and usually drink it in the morning"
        )
        update_poller = await project_client.memory_stores.begin_update_memories(
            name=memory_store.name,
            scope=scope,
            items=[user_message],  # Pass conversation items that you want to add to memory
            # update_delay=300 # Keep default inactivity delay before starting update
        )
        print(
            f"Scheduled memory update operation (Update ID: {update_poller.update_id}, Status: {update_poller.status()})"
        )

        # Extend the previous update with another update and more messages
        new_message = ResponsesUserMessageItemParam(content="I also like cappuccinos in the afternoon")
        new_update_poller = await project_client.memory_stores.begin_update_memories(
            name=memory_store.name,
            scope=scope,
            items=[new_message],
            previous_update_id=update_poller.update_id,  # Extend from previous update ID
            update_delay=0,  # Trigger update immediately without waiting for inactivity
        )
        print(
            f"Scheduled memory update operation (Update ID: {new_update_poller.update_id}, Status: {new_update_poller.status()})"
        )

        # As first update has not started yet, the new update will cancel the first update and cover both sets of messages
        print(
            f"Superseded first memory update operation (Update ID: {update_poller.update_id}, Status: {update_poller.status()})"
        )

        new_update_result = await new_update_poller.result()
        print(
            f"Second update {new_update_poller.update_id} completed with {len(new_update_result.memory_operations)} memory operations"
        )
        for operation in new_update_result.memory_operations:
            print(
                f"  - Operation: {operation.kind}, Memory ID: {operation.memory_item.memory_id}, Content: {operation.memory_item.content}"
            )

        # Retrieve memories from the memory store
        query_message = ResponsesUserMessageItemParam(content="What are my morning coffee preferences?")
        search_response = await project_client.memory_stores.search_memories(
            name=memory_store.name, scope=scope, items=[query_message], options=MemorySearchOptions(max_memories=5)
        )
        print(f"Found {len(search_response.memories)} memories")
        for memory in search_response.memories:
            print(f"  - Memory ID: {memory.memory_item.memory_id}, Content: {memory.memory_item.content}")

        # Perform another search using the previous search as context
        agent_message = ResponsesAssistantMessageItemParam(
            content="You previously indicated a preference for dark roast coffee in the morning."
        )
        followup_query = ResponsesUserMessageItemParam(
            content="What about afternoon?"  # Follow-up assuming context from previous messages
        )
        followup_search_response = await project_client.memory_stores.search_memories(
            name=memory_store.name,
            scope=scope,
            items=[agent_message, followup_query],
            previous_search_id=search_response.search_id,
            options=MemorySearchOptions(max_memories=5),
        )
        print(f"Found {len(followup_search_response.memories)} memories")
        for memory in followup_search_response.memories:
            print(f"  - Memory ID: {memory.memory_item.memory_id}, Content: {memory.memory_item.content}")

        # Delete memories for the current scope
        await project_client.memory_stores.delete_scope(name=memory_store.name, scope=scope)
        print(f"Deleted memories for scope '{scope}'")

        # Delete memory store
        await project_client.memory_stores.delete(memory_store.name)
        print(f"Deleted memory store `{memory_store.name}`")


if __name__ == "__main__":
    asyncio.run(main())
