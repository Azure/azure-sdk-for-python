# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_facet_query.py
DESCRIPTION:
    This sample demonstrates how to obtain search facets on specified field in
    an Azure Search index.
USAGE:
    python sample_facet_query.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - the endpoint of your Azure Cognitive Search service
    2) AZURE_SEARCH_INDEX_NAME - the name of your search index (e.g. "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - your search API key
"""

import os

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
key = os.getenv("AZURE_SEARCH_API_KEY")

def filter_query():
    # [START facet_query]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

    results = search_client.search(search_text="WiFi", facets=["Category,count:3", "ParkingIncluded"])

    facets = results.get_facets()

    print("Catgory facet counts for hotels:")
    for facet in facets["Category"]:
        print("    {}".format(facet))
    # [END facet_query]

if __name__ == '__main__':
    filter_query()