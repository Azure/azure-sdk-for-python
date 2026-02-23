# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates how to make custom HTTP requests using SearchIndexClient.

USAGE:
    python sample_index_client_custom_request.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
        (e.g., https://<your-search-service-name>.search.windows.net)
    2) AZURE_SEARCH_INDEX_NAME - target search index name (e.g., "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - the admin key for your search service
"""


def sample_send_request():
    # [START sample_send_request]
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.core.rest import HttpRequest
    from azure.search.documents.indexes import SearchIndexClient
    from sample_utils import AZURE_SEARCH_API_VERSION

    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
    key = os.environ["AZURE_SEARCH_API_KEY"]

    index_client = SearchIndexClient(endpoint, AzureKeyCredential(key))

    # The `send_request` method can send custom HTTP requests that share the client's existing pipeline,
    # while adding convenience for endpoint construction.
    request = HttpRequest(
        method="GET",
        url=f"/indexes('{index_name}')?api-version={AZURE_SEARCH_API_VERSION}",
    )
    response = index_client.send_request(request)
    response.raise_for_status()
    response_body = response.json()
    print(f"Response: {response_body}")
    # [END sample_send_request]


if __name__ == "__main__":
    sample_send_request()
