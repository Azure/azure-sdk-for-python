# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_batch_client_async.py
DESCRIPTION:
    This sample demonstrates how to upload, merge, or delete documents using SearchIndexingBufferedSender.
USAGE:
    python sample_batch_client_async.py

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

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchIndexingBufferedSender


async def sample_batching_client():
    DOCUMENT = {
        "category": "Hotel",
        "hotelId": "1000",
        "rating": 4.0,
        "rooms": [],
        "hotelName": "Azure Inn",
    }

    async with SearchIndexingBufferedSender(service_endpoint, index_name, AzureKeyCredential(key)) as batch_client:
        # add upload actions
        await batch_client.upload_documents(documents=[DOCUMENT])
        # add merge actions
        await batch_client.merge_documents(documents=[{"hotelId": "1000", "rating": 4.5}])
        # add delete actions
        await batch_client.delete_documents(documents=[{"hotelId": "1000"}])


async def main():
    await sample_batching_client()


if __name__ == "__main__":
    asyncio.run(main())
