# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_suggestions.py
DESCRIPTION:
    This sample demonstrates how to obtain search suggestions from an Azure
    search index
USAGE:
    python sample_suggestions.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - the endpoint of your Azure Cognitive Search service
    2) AZURE_SEARCH_INDEX_NAME - the name of your search index (e.g. "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - your search API key
"""

import os

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
key = os.getenv("AZURE_SEARCH_API_KEY")

def suggest_query():
    # [START suggest_query]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

    results = search_client.suggest(search_text="coffee", suggester_name="sg")

    print("Search suggestions for 'coffee'")
    for result in results:
        hotel = search_client.get_document(key=result["HotelId"])
        print("    Text: {} for Hotel: {}".format(repr(result["text"]), hotel["HotelName"]))
    # [END suggest_query]

if __name__ == '__main__':
    suggest_query()
