# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates how to create, get, update, list, and delete a knowledge source.
    A knowledge source is a reusable reference to source data (such as a search index)
    used by a knowledge base for agentic retrieval.

    To query a knowledge base built on this knowledge source, see
    sample_agentic_retrieval_async.py.

USAGE:
    python sample_knowledge_source_crud_async.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
        (e.g., https://<your-search-service-name>.search.windows.net)
    2) AZURE_SEARCH_API_KEY - the admin key for your search service
    3) AZURE_SEARCH_INDEX_NAME - target search index name. The index must have a
        semantic configuration (e.g., "hotels-sample-index").
"""


import asyncio
import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]
knowledge_source_name = "hotels-sample-knowledge-source"


async def create_knowledge_source_async():
    # [START create_knowledge_source_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import (
        SearchIndexKnowledgeSource,
        SearchIndexKnowledgeSourceParameters,
    )

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    knowledge_source = SearchIndexKnowledgeSource(
        name=knowledge_source_name,
        search_index_parameters=SearchIndexKnowledgeSourceParameters(
            search_index_name=index_name,
        ),
    )

    async with index_client:
        result = await index_client.create_or_update_knowledge_source(knowledge_source=knowledge_source)
    print(f"Created: knowledge source '{result.name}' -> index '{index_name}'")
    # [END create_knowledge_source_async]


async def get_knowledge_source_async():
    # [START get_knowledge_source_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    async with index_client:
        result = await index_client.get_knowledge_source(knowledge_source_name)
    print(f"Retrieved: knowledge source '{result.name}'")
    # [END get_knowledge_source_async]


async def update_knowledge_source_async():
    # [START update_knowledge_source_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import (
        SearchIndexFieldReference,
        SearchIndexKnowledgeSource,
        SearchIndexKnowledgeSourceParameters,
    )

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    knowledge_source = SearchIndexKnowledgeSource(
        name=knowledge_source_name,
        description="Updated with source data fields",
        search_index_parameters=SearchIndexKnowledgeSourceParameters(
            search_index_name=index_name,
            source_data_fields=[
                SearchIndexFieldReference(name="HotelId"),
                SearchIndexFieldReference(name="HotelName"),
            ],
        ),
    )

    async with index_client:
        result = await index_client.create_or_update_knowledge_source(knowledge_source=knowledge_source)
    print(f"Updated: knowledge source '{result.name}'")
    # [END update_knowledge_source_async]


async def list_knowledge_sources_async():
    # [START list_knowledge_sources_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    async with index_client:
        async for ks in index_client.list_knowledge_sources():
            print(f"Listed: knowledge source '{ks.name}'")
    # [END list_knowledge_sources_async]


async def delete_knowledge_source_async():
    # [START delete_knowledge_source_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    async with index_client:
        await index_client.delete_knowledge_source(knowledge_source_name)
    print(f"Deleted: knowledge source '{knowledge_source_name}'")
    # [END delete_knowledge_source_async]


if __name__ == "__main__":
    asyncio.run(create_knowledge_source_async())
    asyncio.run(get_knowledge_source_async())
    asyncio.run(update_knowledge_source_async())
    asyncio.run(list_knowledge_sources_async())
    asyncio.run(delete_knowledge_source_async())
