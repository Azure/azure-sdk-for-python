# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to perform CRUD operations on a memory store
    using the synchronous AIProjectClient.

    See also /samples/agents/tools/sample_agent_memory_search.py that shows
    how to use the Memory Search Tool in a prompt agent.

USAGE:
    python sample_memory_crud.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_CHAT_MODEL_DEPLOYMENT_NAME - The deployment name of the chat model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) AZURE_AI_EMBEDDING_MODEL_DEPLOYMENT_NAME - The deployment name of the embedding model, as found under the
       "Name" column in the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
from dotenv import load_dotenv
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import MemoryStoreDefaultDefinition

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]

with (
    DefaultAzureCredential(exclude_interactive_browser_credential=False) as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):

    # Delete memory store, if it already exists
    memory_store_name = "my_memory_store"
    try:
        project_client.memory_stores.delete(memory_store_name)
        print(f"Memory store `{memory_store_name}` deleted")
    except ResourceNotFoundError:
        pass

    # Create Memory Store
    definition = MemoryStoreDefaultDefinition(
        chat_model=os.environ["AZURE_AI_CHAT_MODEL_DEPLOYMENT_NAME"],
        embedding_model=os.environ["AZURE_AI_EMBEDDING_MODEL_DEPLOYMENT_NAME"],
    )
    memory_store = project_client.memory_stores.create(
        name=memory_store_name, description="Example memory store for conversations", definition=definition
    )
    print(f"Created memory store: {memory_store.name} ({memory_store.id}): {memory_store.description}")

    # Get Memory Store
    get_store = project_client.memory_stores.get(memory_store.name)
    print(f"Retrieved: {get_store.name} ({get_store.id}): {get_store.description}")

    # Update Memory Store
    updated_store = project_client.memory_stores.update(name=memory_store.name, description="Updated description")
    print(f"Updated: {updated_store.name} ({updated_store.id}): {updated_store.description}")

    # List Memory Store
    memory_stores = list(project_client.memory_stores.list(limit=10))
    print(f"Found {len(memory_stores)} memory stores")
    for store in memory_stores:
        print(f"  - {store.name} ({store.id}): {store.description}")

    # Delete Memory Store
    delete_response = project_client.memory_stores.delete(memory_store.name)
    print(f"Deleted: {delete_response.deleted}")
