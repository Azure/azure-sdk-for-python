# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates text search and finding documents similar to a document key.
USAGE:
    python sample_query_simple_async.py

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


async def simple_query_async():
    # [START simple_query_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.aio import SearchClient

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

    async with search_client:
        results = await search_client.search(search_text="spa")

        print("Results: hotels with 'spa'")
        async for result in results:
            print(f"  HotelName: {result['HotelName']} (rating {result['Rating']})")
    # [END simple_query_async]


async def similar_documents_async():
    # [START similar_documents_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.aio import SearchClient

    async with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
        results = await search_client.search(
            more_like_this="1",
            search_fields=["HotelName", "Description"],
            select=["HotelId", "HotelName"],
            top=5,
        )
        async for result in results:
            print(f"Similar hotel: {result['HotelId']}: {result['HotelName']}")
    # [END similar_documents_async]


async def main():
    await simple_query_async()
    await similar_documents_async()


if __name__ == "__main__":
    asyncio.run(main())
