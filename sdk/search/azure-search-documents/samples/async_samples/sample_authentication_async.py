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

import asyncio
import os

async def authentication_with_api_key_credential_async():
    # [START create_search_client_with_key_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.aio import SearchClient
    service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
    key = os.getenv("AZURE_SEARCH_API_KEY")

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
    # [END create_search_client_with_key_async]

    async with search_client:
        result = await search_client.get_document_count()

    print("There are {} documents in the {} search index.".format(result, repr(index_name)))

async def authentication_service_client_with_api_key_credential_async():
    # [START create_search_service_with_key_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient
    service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
    key = os.getenv("AZURE_SEARCH_API_KEY")

    client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    # [END create_search_service_with_key_async]

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(authentication_with_api_key_credential_async())
    loop.run_until_complete(authentication_service_client_with_api_key_credential_async())