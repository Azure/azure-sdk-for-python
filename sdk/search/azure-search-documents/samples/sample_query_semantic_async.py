# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates fuzzy term matching and semantic search with the 2026-10-01 GA API.
    Fuzzy Lucene queries replace the preview-only query speller.
USAGE:
    python sample_query_semantic_async.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
    2) AZURE_SEARCH_INDEX_NAME - target search index name (e.g., "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - the primary admin key for your search service
"""

import os
import asyncio

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]
semantic_configuration_name = "hotels-sample-semantic-config"


async def create_semantic_configuration_async():
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import (
        SemanticConfiguration,
        SemanticPrioritizedFields,
        SemanticField,
        SemanticSearch,
    )

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    async with index_client:
        index = await index_client.get_index(index_name)

        semantic_config = SemanticConfiguration(
            name=semantic_configuration_name,
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="HotelName"),
                content_fields=[SemanticField(field_name="Description")],
                keywords_fields=[SemanticField(field_name="Tags")],
            ),
        )

        index.semantic_search = SemanticSearch(configurations=[semantic_config])
        await index_client.create_or_update_index(index)
    print(f"Updated: index '{index_name}' (semantic config '{semantic_configuration_name}')")


async def speller_async():
    # [START speller_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.aio import SearchClient

    credential = AzureKeyCredential(key)
    search_client = SearchClient(endpoint=service_endpoint, index_name=index_name, credential=credential)
    async with search_client:
        results = await search_client.search(search_text="luxry~1", query_type="full")

        print("Results: fuzzy matching for 'luxry'")
        async for result in results:
            print(f"  HotelId: {result['HotelId']}")
            print(f"  HotelName: {result['HotelName']}")
    # [END speller_async]


async def semantic_ranking_async():
    # [START semantic_ranking_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.aio import SearchClient

    credential = AzureKeyCredential(key)
    search_client = SearchClient(endpoint=service_endpoint, index_name=index_name, credential=credential)
    async with search_client:
        results = await search_client.search(
            search_text="luxury",
            query_type="semantic",
            semantic_configuration_name=semantic_configuration_name,
        )

        print("Results: semantic ranking")
        async for result in results:
            print(f"  HotelId: {result['HotelId']}")
            print(f"  HotelName: {result['HotelName']}")
    # [END semantic_ranking_async]


async def delete_semantic_configuration_async():
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    async with index_client:
        index = await index_client.get_index(index_name)
        index.semantic_search = None
        await index_client.create_or_update_index(index)
    print(f"Deleted: semantic config from index '{index_name}'")


if __name__ == "__main__":
    asyncio.run(create_semantic_configuration_async())
    asyncio.run(speller_async())
    asyncio.run(semantic_ranking_async())
    asyncio.run(delete_semantic_configuration_async())
