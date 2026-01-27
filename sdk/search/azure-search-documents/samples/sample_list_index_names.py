# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_list_index_names.py
DESCRIPTION:
    This sample demonstrates how to list all index names in a search service.
USAGE:
    python sample_list_index_names.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - the endpoint of your Azure Cognitive Search service
    2) AZURE_SEARCH_API_KEY - your search API key
"""


import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
key = os.environ["AZURE_SEARCH_API_KEY"]

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient


def list_index_names():
    # [START list_index_names]
    client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    print("Listing all index names:")
    for index_name in client.list_index_names():
        print(f"  - {index_name}")
    # [END list_index_names]


if __name__ == "__main__":
    list_index_names()
