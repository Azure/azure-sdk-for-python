# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_autocomplete_async.py
DESCRIPTION:
    This sample demonstrates how to obtain autocompletion suggestions from an
    Azure search index.
USAGE:
    python sample_autocomplete_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - the endpoint of your Azure Cognitive Search service
    2) AZURE_SEARCH_INDEX_NAME - the name of your search index (e.g. "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - your search API key
"""

import os
import asyncio


service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]


async def autocomplete_query():
    # [START autocomplete_query_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.aio import SearchClient

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

    async with search_client:
        results = await search_client.autocomplete(search_text="bo", suggester_name="sg")

        print("Autocomplete suggestions for 'bo'")
        for result in results:
            print("    Completion: {}".format(result["text"]))
    # [END autocomplete_query_async]


if __name__ == "__main__":
    asyncio.run(autocomplete_query())
