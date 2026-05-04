# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates how to create, get, update, list, and delete a knowledge base.
    A knowledge base orchestrates retrieval from one or more knowledge sources for
    agentic retrieval.

    Prerequisite: a knowledge source named "hotels-sample-knowledge-source" must
    already exist (see sample_knowledge_source_crud.py).

    To query the knowledge base, see sample_agentic_retrieval.py.

USAGE:
    python sample_knowledge_base_crud.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
        (e.g., https://<your-search-service-name>.search.windows.net)
    2) AZURE_SEARCH_API_KEY - the admin key for your search service
"""


import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
key = os.environ["AZURE_SEARCH_API_KEY"]
knowledge_source_name = "hotels-sample-knowledge-source"
knowledge_base_name = "hotels-sample-knowledge-base"


def create_knowledge_base():
    # [START create_knowledge_base]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        KnowledgeBase,
        KnowledgeSourceReference,
    )

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    knowledge_base = KnowledgeBase(
        name=knowledge_base_name,
        knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
    )

    result = index_client.create_or_update_knowledge_base(knowledge_base=knowledge_base)
    print(f"Created: knowledge base '{result.name}'")
    # [END create_knowledge_base]


def get_knowledge_base():
    # [START get_knowledge_base]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    result = index_client.get_knowledge_base(knowledge_base_name)
    print(f"Retrieved: knowledge base '{result.name}'")
    # [END get_knowledge_base]


def update_knowledge_base():
    # [START update_knowledge_base]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        KnowledgeBase,
        KnowledgeSourceReference,
    )

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    knowledge_base = KnowledgeBase(
        name=knowledge_base_name,
        description="Updated knowledge base",
        knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
    )

    result = index_client.create_or_update_knowledge_base(knowledge_base=knowledge_base)
    print(f"Updated: knowledge base '{result.name}'")
    # [END update_knowledge_base]


def list_knowledge_bases():
    # [START list_knowledge_bases]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    for kb in index_client.list_knowledge_bases():
        print(f"Listed: knowledge base '{kb.name}'")
    # [END list_knowledge_bases]


def delete_knowledge_base():
    # [START delete_knowledge_base]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    index_client.delete_knowledge_base(knowledge_base_name)
    print(f"Deleted: knowledge base '{knowledge_base_name}'")
    # [END delete_knowledge_base]


if __name__ == "__main__":
    create_knowledge_base()
    get_knowledge_base()
    update_knowledge_base()
    list_knowledge_bases()
    delete_knowledge_base()
