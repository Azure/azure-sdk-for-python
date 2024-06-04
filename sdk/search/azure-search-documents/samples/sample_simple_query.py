# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_simple_query.py
DESCRIPTION:
    This sample demonstrates how to get search results from a basic search text
    from an Azure Search index.
USAGE:
    python sample_simple_query.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - the endpoint of your Azure Cognitive Search service
    2) AZURE_SEARCH_INDEX_NAME - the name of your search index (e.g. "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - your search API key
"""

import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]


def simple_text_query():
    # [START simple_query]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

    results = search_client.search(search_text="spa")

    print("Hotels containing 'spa' in the name (or other fields):")
    for result in results:
        print("    Name: {} (rating {})".format(result["hotelName"], result["rating"]))
    # [END simple_query]


if __name__ == "__main__":
    simple_text_query()
