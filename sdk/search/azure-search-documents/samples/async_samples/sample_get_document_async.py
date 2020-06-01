# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_document_async.py
DESCRIPTION:
    This sample demonstrates how to retrieve a specific document by key from an
    Azure Search index.
USAGE:
    python sample_get_document_async.py

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

async def autocomplete_query():
    # [START get_document_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.aio import SearchClient

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

    async with search_client:
        result = await search_client.get_document(key="23")

        print("Details for hotel '23' are:")
        print("        Name: {}".format(result["HotelName"]))
        print("      Rating: {}".format(result["Rating"]))
        print("    Category: {}".format(result["Category"]))
    # [END get_document_async]

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(autocomplete_query())