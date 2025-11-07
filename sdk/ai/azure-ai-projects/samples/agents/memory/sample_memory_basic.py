# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to interact with the memory store to add and retrieve memory.

USAGE:
    python sample_memory_basic.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity openai python-dotenv

    Deploy a chat model (e.g. gpt-4.1) and an embedding model (e.g. text-embedding-3-small).
    Once you have deployed models, set the deployment name in the variables below.

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Azure AI Foundry portal.
    2) AZURE_AI_CHAT_MODEL_DEPLOYMENT_NAME - The deployment name of the chat model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) AZURE_AI_EMBEDDING_MODEL_DEPLOYMENT_NAME - The deployment name of the embedding model, as found under the
       "Name" column in the "Models + endpoints" tab in your Azure AI Foundry project.
"""

# import os
# from dotenv import load_dotenv
# from azure.identity import DefaultAzureCredential
# from azure.ai.projects import AIProjectClient
# from azure.ai.projects.models import (
#     MemoryStoreDefaultDefinition,
#     MemoryStoreDefaultOptions,
#     MemorySearchOptions,
#     ResponsesUserMessageItemParam,
#     MemorySearchTool,
#     PromptAgentDefinition,
# )

# load_dotenv()

# project_client = AIProjectClient(endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"], credential=DefaultAzureCredential())

# with project_client:

#     # Create a memory store
#     definition = MemoryStoreDefaultDefinition(
#         chat_model=os.environ["AZURE_AI_CHAT_MODEL_DEPLOYMENT_NAME"],
#         embedding_model=os.environ["AZURE_AI_EMBEDDING_MODEL_DEPLOYMENT_NAME"],
#     )
#     memory_store = project_client.memory_stores.create(
#         name="my_memory_store",
#         description="Example memory store for conversations",
#         definition=definition,
#     )
#     print(f"Created memory store: {memory_store.name} ({memory_store.id}): {memory_store.description}")

#     # Set scope to associate the memories with
#     # You can also use "{{$userId}}"" to take the oid of the request authentication header
#     scope = "user_123"

#     # Add memories to the memory store
#     user_message = ResponsesUserMessageItemParam(
#         content="I prefer dark roast coffee and usually drink it in the morning"
#     )
#     update_poller = project_client.memory_stores.begin_update_memories(
#         name=memory_store.name,
#         scope=scope,
#         items=[user_message],  # Pass conversation items that you want to add to memory
#         update_delay=0,  # Trigger update immediately without waiting for inactivity
#     )

#     # Wait for the update operation to complete, but can also fire and forget
#     update_result = update_poller.result()
#     print(f"Updated with {len(update_result.memory_operations)} memory operations")
#     for operation in update_result.memory_operations:
#         print(
#             f"  - Operation: {operation.kind}, Memory ID: {operation.memory_item.memory_id}, Content: {operation.memory_item.content}"
#         )

#     # Retrieve memories from the memory store
#     query_message = ResponsesUserMessageItemParam(content="What are my coffee preferences?")
#     search_response = project_client.memory_stores.search_memories(
#         name=memory_store.name, scope=scope, items=[query_message], options=MemorySearchOptions(max_memories=5)
#     )
#     print(f"Found {len(search_response.memories)} memories")
#     for memory in search_response.memories:
#         print(f"  - Memory ID: {memory.memory_item.memory_id}, Content: {memory.memory_item.content}")

#     # Delete memories for a specific scope
#     delete_scope_response = project_client.memory_stores.delete_scope(name=memory_store.name, scope=scope)
#     print(f"Deleted memories for scope '{scope}': {delete_scope_response.deleted}")

#     # Delete memory store
#     delete_response = project_client.memory_stores.delete(memory_store.name)
#     print(f"Deleted: {delete_response.deleted}")
