# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates how to make custom HTTP requests using SearchClient.

USAGE:
    python sample_search_client_custom_request.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
    2) AZURE_SEARCH_INDEX_NAME - target search index name (e.g., "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - the primary admin key for your search service
"""

import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]


def sample_send_request():
    from azure.core.credentials import AzureKeyCredential
    from azure.core.rest import HttpRequest
    from azure.search.documents import SearchClient
    from sample_utils import AZURE_SEARCH_API_VERSION

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

    # The `send_request` method can send custom HTTP requests that share the client's existing pipeline,
    # while adding convenience for endpoint construction.
    request = HttpRequest(
        method="GET", url=f"/docs/$count?api-version={AZURE_SEARCH_API_VERSION}"
    )
    response = search_client.send_request(request)
    response.raise_for_status()
    response_body = response.json()
    print(f"Document count: {response_body} (index '{index_name}')")


if __name__ == "__main__":
    sample_send_request()
