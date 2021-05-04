# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_crud_operations.py
DESCRIPTION:
    This sample demonstrates how to upload, merge, or delete documents from an
    Azure Search index.
USAGE:
    python sample_crud_operations.py

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
from azure.search.documents import SearchClient

search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

def upload_document():
    # [START upload_document]
    DOCUMENT = {
        'Category': 'Hotel',
        'HotelId': '1000',
        'Rating': 4.0,
        'Rooms': [],
        'HotelName': 'Azure Inn',
    }

    result = search_client.upload_documents(documents=[DOCUMENT])

    print("Upload of new document succeeded: {}".format(result[0].succeeded))
    # [END upload_document]

def merge_document():
    # [START merge_document]
    result = search_client.merge_documents(documents=[{"HotelId": "1000", "Rating": 4.5}])

    print("Merge into new document succeeded: {}".format(result[0].succeeded))
    # [END merge_document]

def delete_document():
    # [START delete_document]
    result = search_client.delete_documents(documents=[{"HotelId": "1000"}])

    print("Delete new document succeeded: {}".format(result[0].succeeded))
    # [END delete_document]

if __name__ == '__main__':
    upload_document()
    merge_document()
    delete_document()
