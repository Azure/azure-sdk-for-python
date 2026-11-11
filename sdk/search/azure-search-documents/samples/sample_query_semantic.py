# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates fuzzy term matching and semantic search with the 2026-10-01 GA API.
    Fuzzy Lucene queries replace the preview-only query speller.
USAGE:
    python sample_query_semantic.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
    2) AZURE_SEARCH_INDEX_NAME - target search index name (e.g., "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - the primary admin key for your search service
"""

import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]
semantic_configuration_name = "hotels-sample-semantic-config"


def create_semantic_configuration():
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        SemanticConfiguration,
        SemanticPrioritizedFields,
        SemanticField,
        SemanticSearch,
    )

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    index = index_client.get_index(index_name)

    semantic_config = SemanticConfiguration(
        name=semantic_configuration_name,
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="HotelName"),
            content_fields=[SemanticField(field_name="Description")],
            keywords_fields=[SemanticField(field_name="Tags")],
        ),
    )

    index.semantic_search = SemanticSearch(configurations=[semantic_config])
    index_client.create_or_update_index(index)
    print(f"Updated: index '{index_name}' (semantic config '{semantic_configuration_name}')")


def speller():
    # [START speller]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient

    credential = AzureKeyCredential(key)
    search_client = SearchClient(endpoint=service_endpoint, index_name=index_name, credential=credential)
    results = list(search_client.search(search_text="luxry~1", query_type="full"))

    print("Results: fuzzy matching for 'luxry'")
    for result in results:
        print(f"  HotelId: {result['HotelId']}")
        print(f"  HotelName: {result['HotelName']}")
    # [END speller]


def semantic_ranking():
    # [START semantic_ranking]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient

    credential = AzureKeyCredential(key)
    search_client = SearchClient(endpoint=service_endpoint, index_name=index_name, credential=credential)
    results = list(
        search_client.search(
            search_text="luxury",
            query_type="semantic",
            semantic_configuration_name=semantic_configuration_name,
        )
    )

    print("Results: semantic ranking")
    for result in results:
        print(f"  HotelId: {result['HotelId']}")
        print(f"  HotelName: {result['HotelName']}")
    # [END semantic_ranking]


def delete_semantic_configuration():
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    index = index_client.get_index(index_name)

    index.semantic_search = None
    index_client.create_or_update_index(index)
    print(f"Deleted: semantic config from index '{index_name}'")


if __name__ == "__main__":
    create_semantic_configuration()
    speller()
    semantic_ranking()
    delete_semantic_configuration()
