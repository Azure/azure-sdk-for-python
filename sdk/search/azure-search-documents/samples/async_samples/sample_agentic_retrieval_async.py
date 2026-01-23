# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates Knowledge Source and Knowledge Base CRUD operations and
    a minimal retrieval query using a semantic intent.

USAGE:
    python sample_agentic_retrieval_async.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
        (e.g., https://<your-search-service-name>.search.windows.net)
    2) AZURE_SEARCH_INDEX_NAME - target search index name (e.g., "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - the admin key for your search service
"""

import asyncio
import json
import os

from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.search.documents.indexes.aio import SearchIndexClient
from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient
from azure.search.documents.knowledgebases.models import (
    KnowledgeBaseRetrievalRequest,
    KnowledgeRetrievalSemanticIntent,
    KnowledgeRetrievalMinimalReasoningEffort,
)
from azure.search.documents.indexes.models import (
    KnowledgeBase,
    KnowledgeSourceReference,
    SearchIndexFieldReference,
    SearchIndexKnowledgeSource,
    SearchIndexKnowledgeSourceParameters,
)

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]

knowledge_source_name = "hotels-sample-knowledge-source"
knowledge_base_name = "hotels-sample-knowledge-base"


async def create_knowledge_source_async():
    # [START create_knowledge_source_async]
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    knowledge_source = SearchIndexKnowledgeSource(
        name=knowledge_source_name,
        search_index_parameters=SearchIndexKnowledgeSourceParameters(search_index_name=index_name),
    )

    async with index_client:
        await index_client.create_or_update_knowledge_source(knowledge_source=knowledge_source)
    print(f"Created: knowledge source '{knowledge_source_name}'")
    # [END create_knowledge_source_async]


async def get_knowledge_source_async():
    # [START get_knowledge_source_async]
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    async with index_client:
        knowledge_source = await index_client.get_knowledge_source(knowledge_source_name)
    print(f"Retrieved: knowledge source '{knowledge_source.name}'")
    # [END get_knowledge_source_async]


async def update_knowledge_source_async():
    # [START update_knowledge_source_async]
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    knowledge_source = SearchIndexKnowledgeSource(
        name=knowledge_source_name,
        search_index_parameters=SearchIndexKnowledgeSourceParameters(
            search_index_name=index_name,
            source_data_fields=[
                SearchIndexFieldReference(name="HotelId"),
                SearchIndexFieldReference(name="HotelName"),
                SearchIndexFieldReference(name="Description"),
                SearchIndexFieldReference(name="Category"),
                SearchIndexFieldReference(name="Tags"),
            ],
        ),
    )

    async with index_client:
        await index_client.create_or_update_knowledge_source(knowledge_source=knowledge_source)
    print(f"Updated: knowledge source '{knowledge_source_name}'")
    # [END update_knowledge_source_async]


async def delete_knowledge_source_async():
    # [START delete_knowledge_source_async]
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    try:
        async with index_client:
            await index_client.delete_knowledge_source(knowledge_source_name)
        print(f"Deleted: knowledge source '{knowledge_source_name}'")
    except ResourceNotFoundError:
        print(f"Skipped: knowledge source '{knowledge_source_name}' not found")
    # [END delete_knowledge_source_async]


async def create_knowledge_base_async():
    # [START create_knowledge_base_async]
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    knowledge_base = KnowledgeBase(
        name=knowledge_base_name,
        knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
    )

    async with index_client:
        await index_client.create_or_update_knowledge_base(knowledge_base)
    print(f"Created: knowledge base '{knowledge_base_name}'")
    # [END create_knowledge_base_async]


async def get_knowledge_base_async():
    # [START get_knowledge_base_async]
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    async with index_client:
        knowledge_base = await index_client.get_knowledge_base(knowledge_base_name)
    print(f"Retrieved: knowledge base '{knowledge_base.name}'")
    # [END get_knowledge_base_async]


async def update_knowledge_base_async():
    # [START update_knowledge_base_async]
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    knowledge_base = KnowledgeBase(
        name=knowledge_base_name,
        knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
        retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
    )

    async with index_client:
        await index_client.create_or_update_knowledge_base(knowledge_base)
    print(f"Updated: knowledge base '{knowledge_base_name}'")
    # [END update_knowledge_base_async]


async def retrieve_knowledge_base_async():
    # [START retrieve_knowledge_base_async]
    retrieval_client = KnowledgeBaseRetrievalClient(
        service_endpoint,
        knowledge_base_name=knowledge_base_name,
        credential=AzureKeyCredential(key),
    )

    request = KnowledgeBaseRetrievalRequest(intents=[KnowledgeRetrievalSemanticIntent(search="hotels with free wifi")])

    try:
        result = await retrieval_client.retrieve(request)
    finally:
        await retrieval_client.close()

    print("Results: knowledge base retrieval")

    response_parts = []
    for resp in result.response or []:
        for content in resp.content or []:
            if hasattr(content, "text"):
                response_parts.append(content.text)

    if response_parts:
        response_content = "\n\n".join(response_parts)

        items = json.loads(response_content)
        for i, item in enumerate(items[:5], start=1):
            print(f"  Result {i}:")
            print(f"    Title: {item.get('title')}")
            print(f"    Content: {item.get('content')}")
    else:
        print("Results: none")
    # [END retrieve_knowledge_base_async]


async def delete_knowledge_base_async():
    # [START delete_knowledge_base_async]
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    try:
        async with index_client:
            await index_client.delete_knowledge_base(knowledge_base_name)
        print(f"Deleted: knowledge base '{knowledge_base_name}'")
    except ResourceNotFoundError:
        print(f"Skipped: knowledge base '{knowledge_base_name}' not found")
    # [END delete_knowledge_base_async]


if __name__ == "__main__":
    asyncio.run(create_knowledge_source_async())
    asyncio.run(get_knowledge_source_async())
    asyncio.run(update_knowledge_source_async())
    asyncio.run(create_knowledge_base_async())
    asyncio.run(get_knowledge_base_async())
    asyncio.run(update_knowledge_base_async())
    asyncio.run(retrieve_knowledge_base_async())
    asyncio.run(delete_knowledge_base_async())
    asyncio.run(delete_knowledge_source_async())
