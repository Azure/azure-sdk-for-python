# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_batch_client.py
DESCRIPTION:
    This sample demonstrates how to upload, merge, or delete documents using SearchIndexingBufferedSender.
USAGE:
    python sample_batch_client.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - the endpoint of your Azure Cognitive Search service
    2) AZURE_SEARCH_INDEX_NAME - the name of your search index (e.g. "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - your search API key
"""

import os

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
key = os.getenv("AZURE_SEARCH_API_KEY")

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchIndexingBufferedSender


def sample_batching_client():
    DOCUMENT = {
        'Category': 'Hotel',
        'HotelId': '1000',
        'Rating': 4.0,
        'Rooms': [],
        'HotelName': 'Azure Inn',
    }

    with SearchIndexingBufferedSender(
            service_endpoint,
            index_name,
            AzureKeyCredential(key)) as batch_client:
        # add upload actions
        batch_client.upload_documents(documents=[DOCUMENT])
        # add merge actions
        batch_client.merge_documents(documents=[{"HotelId": "1000", "Rating": 4.5}])
        # add delete actions
        batch_client.delete_documents(documents=[{"HotelId": "1000"}])

if __name__ == '__main__':
    sample_batching_client()
