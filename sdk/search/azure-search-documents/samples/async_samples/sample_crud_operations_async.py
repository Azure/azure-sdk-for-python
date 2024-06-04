# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_crud_operations_async.py
DESCRIPTION:
    This sample demonstrates how to upload, merge, or delete documents from an
    Azure Search index.
USAGE:
    python sample_crud_operations_async.py

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
from azure.search.documents.aio import SearchClient

search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))


async def upload_document():
    # [START upload_document_async]
    DOCUMENT = {
        "category": "Hotel",
        "hotelId": "1000",
        "rating": 4.0,
        "rooms": [],
        "hotelName": "Azure Inn",
    }

    result = await search_client.upload_documents(documents=[DOCUMENT])

    print("Upload of new document succeeded: {}".format(result[0].succeeded))
    # [END upload_document_async]


async def merge_document():
    # [START merge_document_async]
    result = await search_client.upload_documents(documents=[{"hotelId": "1000", "rating": 4.5}])

    print("Merge into new document succeeded: {}".format(result[0].succeeded))
    # [END merge_document_async]


async def delete_document():
    # [START delete_document_async]
    result = await search_client.upload_documents(documents=[{"hotelId": "1000"}])

    print("Delete new document succeeded: {}".format(result[0].succeeded))
    # [END delete_document_async]


async def main():
    await upload_document()
    await merge_document()
    await delete_document()
    await search_client.close()


if __name__ == "__main__":
    asyncio.run(main())
