# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_filter_query_async.py
DESCRIPTION:
    This sample demonstrates how search results from an Azure Search index can
    be filtered and ordered.
USAGE:
    python sample_filter_query_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - the endpoint of your Azure Cognitive Search service
    2) AZURE_SEARCH_INDEX_NAME - the name of your search index (e.g. "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - your search API key
"""

import os
import asyncio


service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
key = os.getenv("AZURE_SEARCH_API_KEY")

async def filter_query():
    # [START filter_query_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.aio import SearchClient

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

    select = ("HotelName", "Rating")
    async with search_client:
        results = await search_client.search(
            search_text="WiFi",
            filter="Address/StateProvince eq 'FL' and Address/Country eq 'USA'",
            select=",".join(select),
            order_by="Rating desc"
        )

        print("Florida hotels containing 'WiFi', sorted by Rating:")
        async for result in results:
            print("    Name: {} (rating {})".format(result["HotelName"], result["Rating"]))
    # [END filter_query_async]

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(filter_query())