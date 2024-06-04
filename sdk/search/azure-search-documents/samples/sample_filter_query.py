# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_filter_query.py
DESCRIPTION:
    This sample demonstrates how search results from an Azure Search index can
    be filtered and ordered.
USAGE:
    python sample_filter_query.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - the endpoint of your Azure Cognitive Search service
    2) AZURE_SEARCH_INDEX_NAME - the name of your search index (e.g. "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - your search API key
"""

import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]


def filter_query():
    # [START filter_query]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

    results = search_client.search(
        search_text="WiFi",
        filter="Address/StateProvince eq 'FL' and Address/Country eq 'USA'",
        select=["hotelName", "rating"],
        order_by=["rating desc"],
    )

    print("Florida hotels containing 'WiFi', sorted by Rating:")
    for result in results:
        print("    Name: {} (rating {})".format(result["hotelName"], result["rating"]))
    # [END filter_query]


if __name__ == "__main__":
    filter_query()
