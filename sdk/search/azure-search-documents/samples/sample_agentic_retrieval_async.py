# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates the end-to-end agentic retrieval scenario using async clients:
    create a knowledge source over an existing search index, create a knowledge
    base that references it, query the knowledge base with a semantic intent,
    and clean up.

    For knowledge source / knowledge base CRUD details (get, update, list),
    see sample_knowledge_source_crud_async.py and sample_knowledge_base_crud_async.py.

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
from azure.search.documents.indexes.aio import SearchIndexClient
from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient
from azure.search.documents.knowledgebases.models import (
    KnowledgeBaseRetrievalRequest,
    KnowledgeRetrievalSemanticIntent,
)
from azure.search.documents.indexes.models import (
    KnowledgeBase,
    KnowledgeSourceReference,
    SearchIndexKnowledgeSource,
    SearchIndexKnowledgeSourceParameters,
)

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]

knowledge_source_name = "hotels-sample-knowledge-source"
knowledge_base_name = "hotels-sample-knowledge-base"


async def setup_knowledge_base_async():
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    async with index_client:
        knowledge_source = SearchIndexKnowledgeSource(
            name=knowledge_source_name,
            search_index_parameters=SearchIndexKnowledgeSourceParameters(search_index_name=index_name),
        )
        await index_client.create_or_update_knowledge_source(knowledge_source=knowledge_source)
        print(f"Created: knowledge source '{knowledge_source_name}'")

        knowledge_base = KnowledgeBase(
            name=knowledge_base_name,
            knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
        )
        await index_client.create_or_update_knowledge_base(knowledge_base)
        print(f"Created: knowledge base '{knowledge_base_name}'")


async def retrieve_knowledge_base_async():
    # [START retrieve_knowledge_base_async]
    retrieval_client = KnowledgeBaseRetrievalClient(
        service_endpoint,
        credential=AzureKeyCredential(key),
        knowledge_base_name=knowledge_base_name,
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
        items = json.loads("\n\n".join(response_parts))
        for i, item in enumerate(items[:5], start=1):
            print(f"  Result {i}:")
            print(f"    Title: {item.get('title')}")
            print(f"    Content: {item.get('content')}")
    else:
        print("Results: none")
    # [END retrieve_knowledge_base_async]


async def cleanup_async():
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    async with index_client:
        await index_client.delete_knowledge_base(knowledge_base_name)
        print(f"Deleted: knowledge base '{knowledge_base_name}'")
        await index_client.delete_knowledge_source(knowledge_source_name)
        print(f"Deleted: knowledge source '{knowledge_source_name}'")


async def main():
    await setup_knowledge_base_async()
    await retrieve_knowledge_base_async()
    await cleanup_async()


if __name__ == "__main__":
    asyncio.run(main())
