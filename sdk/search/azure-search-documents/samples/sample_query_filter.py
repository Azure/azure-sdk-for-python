# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates how to filter and sort search results.

USAGE:
    python sample_query_filter.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
        (e.g., https://<your-search-service-name>.search.windows.net)
    2) AZURE_SEARCH_INDEX_NAME - target search index name (e.g., "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - the admin key for your search service
"""

import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]


def filter_query():
    # [START filter_query]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

    results = search_client.search(
        search_text="WiFi",
        filter="Address/StateProvince eq 'FL' and Address/Country eq 'USA'",
        select=["HotelName", "Rating"],
        order_by=["Rating desc"],
    )

    print("Results: Florida hotels with WiFi (sorted by rating)")
    for result in results:
        print(f"  HotelName: {result['HotelName']} (rating {result['Rating']})")
    # [END filter_query]


if __name__ == "__main__":
    filter_query()
