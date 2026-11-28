# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates text search and finding documents similar to a document key.
USAGE:
    python sample_query_simple.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
    2) AZURE_SEARCH_INDEX_NAME - target search index name (e.g., "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - the primary admin key for your search service
"""

import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]


def simple_query():
    # [START simple_query]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

    results = search_client.search(search_text="spa")

    print("Results: hotels with 'spa'")
    for result in results:
        print(f"  HotelName: {result['HotelName']} (rating {result['Rating']})")
    # [END simple_query]


def similar_documents():
    # [START similar_documents]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient

    with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
        results = search_client.search(
            more_like_this="1",
            search_fields=["HotelName", "Description"],
            select=["HotelId", "HotelName"],
            top=5,
        )
        for result in results:
            print(f"Similar hotel: {result['HotelId']}: {result['HotelName']}")
    # [END similar_documents]


if __name__ == "__main__":
    simple_query()
    similar_documents()
