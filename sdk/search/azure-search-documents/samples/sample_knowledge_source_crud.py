# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates how to create, get, update, list, and delete a knowledge source.
    A knowledge source is a reusable reference to source data (such as a search index)
    used by a knowledge base for agentic retrieval.

    To query a knowledge base built on this knowledge source, see
    sample_agentic_retrieval.py.

USAGE:
    python sample_knowledge_source_crud.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
        (e.g., https://<your-search-service-name>.search.windows.net)
    2) AZURE_SEARCH_API_KEY - the admin key for your search service
    3) AZURE_SEARCH_INDEX_NAME - target search index name. The index must have a
        semantic configuration (e.g., "hotels-sample-index").
"""


import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]
knowledge_source_name = "hotels-sample-knowledge-source"


def create_knowledge_source():
    # [START create_knowledge_source]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        SearchIndexKnowledgeSource,
        SearchIndexKnowledgeSourceParameters,
    )

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    knowledge_source = SearchIndexKnowledgeSource(
        name=knowledge_source_name,
        search_index_parameters=SearchIndexKnowledgeSourceParameters(
            search_index_name=index_name,
        ),
    )

    result = index_client.create_or_update_knowledge_source(knowledge_source=knowledge_source)
    print(f"Created: knowledge source '{result.name}' -> index '{index_name}'")
    # [END create_knowledge_source]


def get_knowledge_source():
    # [START get_knowledge_source]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    result = index_client.get_knowledge_source(knowledge_source_name)
    print(f"Retrieved: knowledge source '{result.name}'")
    # [END get_knowledge_source]


def update_knowledge_source():
    # [START update_knowledge_source]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        SearchIndexFieldReference,
        SearchIndexKnowledgeSource,
        SearchIndexKnowledgeSourceParameters,
    )

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    knowledge_source = SearchIndexKnowledgeSource(
        name=knowledge_source_name,
        description="Updated with source data fields",
        search_index_parameters=SearchIndexKnowledgeSourceParameters(
            search_index_name=index_name,
            source_data_fields=[
                SearchIndexFieldReference(name="HotelId"),
                SearchIndexFieldReference(name="HotelName"),
            ],
        ),
    )

    result = index_client.create_or_update_knowledge_source(knowledge_source=knowledge_source)
    print(f"Updated: knowledge source '{result.name}'")
    # [END update_knowledge_source]


def list_knowledge_sources():
    # [START list_knowledge_sources]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    for ks in index_client.list_knowledge_sources():
        print(f"Listed: knowledge source '{ks.name}'")
    # [END list_knowledge_sources]


def delete_knowledge_source():
    # [START delete_knowledge_source]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    index_client.delete_knowledge_source(knowledge_source_name)
    print(f"Deleted: knowledge source '{knowledge_source_name}'")
    # [END delete_knowledge_source]


if __name__ == "__main__":
    create_knowledge_source()
    get_knowledge_source()
    update_knowledge_source()
    list_knowledge_sources()
    delete_knowledge_source()
