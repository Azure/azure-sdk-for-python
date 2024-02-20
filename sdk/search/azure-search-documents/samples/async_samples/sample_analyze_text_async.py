# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_text_async.py
DESCRIPTION:
    This sample demonstrates how to analyze text.
USAGE:
    python sample_analyze_text_async.py

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


async def simple_analyze_text():
    # [START simple_analyze_text_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import AnalyzeTextOptions

    client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    analyze_request = AnalyzeTextOptions(text="One's <two/>", analyzer_name="standard.lucene")

    async with client:
        result = await client.analyze_text(index_name, analyze_request)
        print(result.as_dict())
    # [END simple_analyze_text_async]


if __name__ == "__main__":
    asyncio.run(simple_analyze_text())
