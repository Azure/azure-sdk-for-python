# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_text.py
DESCRIPTION:
    This sample demonstrates how to analyze text.
USAGE:
    python sample_analyze_text.py

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

async def simple_analyze_text():
    # [START simple_analyze_text_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.aio import SearchServiceClient
    from azure.search.documents import AnalyzeRequest

    service_client = SearchServiceClient(service_endpoint, AzureKeyCredential(key))
    client = service_client.get_indexes_client()

    analyze_request = AnalyzeRequest(text="One's <two/>", analyzer="standard.lucene")

    async with service_client:
        result = await client.analyze_text(index_name, analyze_request)
        print(result.as_dict())
    # [END simple_analyze_text_async]

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(simple_analyze_text())
