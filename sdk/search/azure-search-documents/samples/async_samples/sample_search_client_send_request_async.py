# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_search_client_send_request_async.py

DESCRIPTION:
    This sample demonstrates how to make custom HTTP requests through a client pipeline.

USAGE:
    python sample_search_client_send_request_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - the endpoint of your Azure Cognitive Search service
    2) AZURE_SEARCH_INDEX_NAME - the name of your search index (e.g. "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - your search API key
"""

import asyncio
import os
from azure.core.credentials import AzureKeyCredential
from azure.core.rest import HttpRequest
from azure.search.documents.aio import SearchClient


async def sample_send_request():
    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
    key = os.environ["AZURE_SEARCH_API_KEY"]

    client = SearchClient(endpoint, index_name, AzureKeyCredential(key))

    # The `send_request` method can send custom HTTP requests that share the client's existing pipeline,
    # while adding convenience for endpoint construction.
    request = HttpRequest(method="GET", url=f"/docs/$count?api-version=2024-03-01-Preview")
    async with client:
        response = await client.send_request(request)
    response.raise_for_status()
    response_body = response.json()
    print(response_body)


if __name__ == "__main__":
    asyncio.run(sample_send_request())
