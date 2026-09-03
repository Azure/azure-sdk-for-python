# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates how to create, get, update, list, and delete a knowledge base.
    A knowledge base orchestrates retrieval from one or more knowledge sources for
    agentic retrieval.

    Prerequisite: a knowledge source named "hotels-sample-knowledge-source" must
    already exist (see sample_knowledge_source_crud_async.py).

    To query the knowledge base, see sample_agentic_retrieval_async.py.

USAGE:
    python sample_knowledge_base_crud_async.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
        (e.g., https://<your-search-service-name>.search.windows.net)
    2) AZURE_SEARCH_API_KEY - the admin key for your search service
"""

import asyncio
import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
key = os.environ["AZURE_SEARCH_API_KEY"]
knowledge_source_name = "hotels-sample-knowledge-source"
knowledge_base_name = "hotels-sample-knowledge-base"


async def create_knowledge_base_async():
    # [START create_knowledge_base_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import (
        KnowledgeBase,
        KnowledgeSourceReference,
    )

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    knowledge_base = KnowledgeBase(
        name=knowledge_base_name,
        knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
        tags={"environment": "sample", "owner": "search-team"},
    )

    async with index_client:
        result = await index_client.create_or_update_knowledge_base(knowledge_base=knowledge_base)
    assert result.tags == {"environment": "sample", "owner": "search-team"}
    print(f"Created: knowledge base '{result.name}'")
    # [END create_knowledge_base_async]


async def get_knowledge_base_async():
    # [START get_knowledge_base_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    async with index_client:
        result = await index_client.get_knowledge_base(knowledge_base_name)
    assert result.tags == {"environment": "sample", "owner": "search-team"}
    print(f"Retrieved: knowledge base '{result.name}'")
    # [END get_knowledge_base_async]


async def update_knowledge_base_async():
    # [START update_knowledge_base_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    async with index_client:
        knowledge_base = await index_client.get_knowledge_base(knowledge_base_name)
        knowledge_base.tags = {"environment": "sample", "owner": "retrieval-team"}
        result = await index_client.create_or_update_knowledge_base(knowledge_base=knowledge_base)
    assert result.tags == {"environment": "sample", "owner": "retrieval-team"}
    print("Tags are metadata labels; this sample does not use them for billing attribution.")
    print(f"Updated: knowledge base '{result.name}'")
    # [END update_knowledge_base_async]


async def list_knowledge_bases_async():
    # [START list_knowledge_bases_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import KnowledgeBase, KnowledgeSourceReference

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    companion_name = f"{knowledge_base_name}-page"
    companion = KnowledgeBase(
        name=companion_name,
        knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
    )
    async with index_client:
        await index_client.create_or_update_knowledge_base(companion)
        try:
            knowledge_bases = [
                knowledge_base
                async for knowledge_base in index_client.list_knowledge_bases(
                    search=knowledge_base_name,
                    page_size=1,
                    search_type="prefix",
                )
            ]
            knowledge_base_names = [knowledge_base.name for knowledge_base in knowledge_bases]
            assert set(knowledge_base_names) == {knowledge_base_name, companion_name}
            assert len(knowledge_base_names) == len(set(knowledge_base_names))
            print(f"Paged through {len(knowledge_bases)} knowledge bases without duplicates")
        finally:
            await index_client.delete_knowledge_base(companion_name)
    # [END list_knowledge_bases_async]


async def delete_knowledge_base_async():
    # [START delete_knowledge_base_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    async with index_client:
        await index_client.delete_knowledge_base(knowledge_base_name)
    print(f"Deleted: knowledge base '{knowledge_base_name}'")
    # [END delete_knowledge_base_async]


if __name__ == "__main__":
    asyncio.run(create_knowledge_base_async())
    asyncio.run(get_knowledge_base_async())
    asyncio.run(update_knowledge_base_async())
    asyncio.run(list_knowledge_bases_async())
    asyncio.run(delete_knowledge_base_async())
