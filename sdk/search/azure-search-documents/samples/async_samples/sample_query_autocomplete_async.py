# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates how to retrieve autocomplete suggestions.

USAGE:
    python sample_query_autocomplete_async.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
        (e.g., https://<your-search-service-name>.search.windows.net)
    2) AZURE_SEARCH_INDEX_NAME - target search index name (e.g., "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - the admin key for your search service
"""

import os
import asyncio


service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]


async def autocomplete_query_async():
    # [START autocomplete_query_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.aio import SearchClient

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

    async with search_client:
        results = await search_client.autocomplete(search_text="bo", suggester_name="sg")

        print("Results: autocomplete for 'bo'")
        for result in results:
            print(f"  Completion: {result['text']}")
    # [END autocomplete_query_async]


if __name__ == "__main__":
    asyncio.run(autocomplete_query_async())
