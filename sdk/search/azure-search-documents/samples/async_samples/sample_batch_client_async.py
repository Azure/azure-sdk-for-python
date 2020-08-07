# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_batch_client_async.py
DESCRIPTION:
    This sample demonstrates how to upload, merge, or delete documents using SearchIndexDocumentBatchingClient.
USAGE:
    python sample_batch_client_async.py

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

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchIndexDocumentBatchingClient

batch_client = SearchIndexDocumentBatchingClient(
    service_endpoint,
    index_name,
    AzureKeyCredential(key),
    window=100,
    batch_size=100
)

async def upload_document():
    DOCUMENT = {
        'Category': 'Hotel',
        'HotelId': '1000',
        'Rating': 4.0,
        'Rooms': [],
        'HotelName': 'Azure Inn',
    }

    await batch_client.upload_documents_actions(documents=[DOCUMENT])

async def merge_document():
    await batch_client.merge_documents_actions(documents=[{"HotelId": "1000", "Rating": 4.5}])

async def delete_document():
    await batch_client.delete_documents_actions(documents=[{"HotelId": "1000"}])

async def main():
    await upload_document()
    await merge_document()
    await delete_document()
    # flush() method will be auto-triggered if it is idle for 100s.
    await batch_client.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
