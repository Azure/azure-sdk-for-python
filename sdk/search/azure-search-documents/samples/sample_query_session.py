# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates how to use session IDs for consistent scoring.
USAGE:
    python sample_query_session.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
    2) AZURE_SEARCH_INDEX_NAME - target search index name (e.g., "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - the primary admin key for your search service
"""

import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]


def query_session():
    # [START query_session]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

    results = search_client.search(search_text="spa", session_id="session-1")

    print("Results: hotels with 'spa'")
    for result in results:
        print(f"  HotelName: {result['HotelName']} (rating {result['Rating']})")
    # [END query_session]


if __name__ == "__main__":
    query_session()
