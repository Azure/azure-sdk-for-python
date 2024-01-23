# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_authentication.py
DESCRIPTION:
    This sample demonstrates how to authenticate with the Azure Congnitive Search
    service with an API key. See more details about authentication here:
    https://docs.microsoft.com/en-us/azure.search.documents/search-security-api-keys
USAGE:
    python sample_authentication.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - the endpoint of your Azure Cognitive Search service
    2) AZURE_SEARCH_INDEX_NAME - the name of your search index (e.g. "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - your search API key
"""

import os


def authentication_with_api_key_credential():
    # [START create_search_client_with_key]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient

    service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
    key = os.environ["AZURE_SEARCH_API_KEY"]

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
    # [END create_search_client_with_key]

    result = search_client.get_document_count()

    print("There are {} documents in the {} search index.".format(result, index_name))


def authentication_service_client_with_api_key_credential():
    # [START create_search_service_client_with_key]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient

    service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    key = os.environ["AZURE_SEARCH_API_KEY"]

    search_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    # [END create_search_service_client_with_key]


def authentication_with_aad():
    # [START authentication_with_aad]
    from azure.identity import DefaultAzureCredential
    from azure.search.documents import SearchClient

    service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
    credential = DefaultAzureCredential()

    search_client = SearchClient(service_endpoint, index_name, credential)
    # [END authentication_with_aad]

    result = search_client.get_document_count()

    print("There are {} documents in the {} search index.".format(result, index_name))


def authentication_service_client_with_aad():
    # [START authentication_service_client_with_aad]
    from azure.identity import DefaultAzureCredential
    from azure.search.documents.indexes import SearchIndexClient

    service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    credential = DefaultAzureCredential()

    search_client = SearchIndexClient(service_endpoint, credential)
    # [END authentication_service_client_with_aad]


if __name__ == "__main__":
    authentication_with_api_key_credential()
    authentication_service_client_with_api_key_credential()
    authentication_with_aad()
    authentication_service_client_with_aad()
