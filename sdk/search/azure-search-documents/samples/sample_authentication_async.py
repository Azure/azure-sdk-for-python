# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates how to authenticate with the Azure AI Search service.

USAGE:
    python sample_authentication_async.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
        (e.g., https://<your-search-service-name>.search.windows.net)
    2) AZURE_SEARCH_INDEX_NAME - target search index name (e.g., "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - the admin key for your search service
"""

import os
import asyncio


async def authenticate_search_client_with_api_key_async():
    # [START authenticate_search_client_with_api_key_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.aio import SearchClient

    service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
    key = os.environ["AZURE_SEARCH_API_KEY"]

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
    # [END authenticate_search_client_with_api_key_async]

    async with search_client:
        document_count = await search_client.get_document_count()

    print(f"Document count: {document_count} (index '{index_name}')")


async def authenticate_index_client_with_api_key_async():
    # [START authenticate_index_client_with_api_key_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient

    service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    key = os.environ["AZURE_SEARCH_API_KEY"]

    search_index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    # [END authenticate_index_client_with_api_key_async]

    async with search_index_client:
        result = search_index_client.list_indexes()
        names = [x.name async for x in result]
    print(f"Indexes ({len(names)}): {', '.join(names)}")


async def authenticate_search_client_with_aad_async():
    # [START authenticate_search_client_with_aad_async]
    from azure.identity.aio import DefaultAzureCredential
    from azure.search.documents.aio import SearchClient

    service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
    credential = DefaultAzureCredential()

    search_client = SearchClient(service_endpoint, index_name, credential)
    # [END authenticate_search_client_with_aad_async]

    async with search_client:
        document_count = await search_client.get_document_count()

    print(f"Document count: {document_count} (index '{index_name}')")


async def authenticate_index_client_with_aad_async():
    # [START authenticate_index_client_with_aad_async]
    from azure.identity.aio import DefaultAzureCredential
    from azure.search.documents.indexes.aio import SearchIndexClient

    service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    credential = DefaultAzureCredential()

    search_index_client = SearchIndexClient(service_endpoint, credential)
    # [END authenticate_index_client_with_aad_async]

    async with search_index_client:
        result = search_index_client.list_indexes()
        names = [x.name async for x in result]
    print(f"Indexes ({len(names)}): {', '.join(names)}")


if __name__ == "__main__":
    asyncio.run(authenticate_search_client_with_api_key_async())
    asyncio.run(authenticate_index_client_with_api_key_async())
    asyncio.run(authenticate_search_client_with_aad_async())
    asyncio.run(authenticate_index_client_with_aad_async())
