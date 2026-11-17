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

    Creates and cleans up a prerequisite knowledge source over an existing index.

    To query the knowledge base, see sample_agentic_retrieval.py.

USAGE:
    python sample_knowledge_base_crud.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
        (e.g., https://<your-search-service-name>.search.windows.net)
    2) AZURE_SEARCH_API_KEY - the admin key for your search service
    3) AZURE_SEARCH_INDEX_NAME - existing search index with a semantic configuration
    4) SAMPLE_RUN_TAG - optional resource-name suffix for this run
"""

import os

from sample_utils import cleanup_knowledge_resources, get_sample_run_tag, setup_search_index_knowledge_source

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
key = os.environ["AZURE_SEARCH_API_KEY"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
run_tag = get_sample_run_tag()
knowledge_source_name = f"hotels-sample-knowledge-source-{run_tag}"
knowledge_base_name = f"hotels-sample-knowledge-base-{run_tag}"


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

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    knowledge_base = index_client.get_knowledge_base(knowledge_base_name)
    knowledge_base.description = "Updated hotel knowledge base"
    result = index_client.create_or_update_knowledge_base(knowledge_base=knowledge_base)
    assert result.description == "Updated hotel knowledge base"
    print(f"Updated: knowledge base '{result.name}'")
    # [END update_knowledge_base]


def list_knowledge_bases():
    # [START list_knowledge_bases]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import KnowledgeBase, KnowledgeSourceReference

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    companion_name = f"{knowledge_base_name}-page"
    companion = KnowledgeBase(
        name=companion_name,
        knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
    )
    index_client.create_or_update_knowledge_base(companion)
    try:
        knowledge_bases = list(
            index_client.list_knowledge_bases(
                search=knowledge_base_name,
                page_size=1,
                search_type="prefix",
            )
        )
        knowledge_base_names = [knowledge_base.name for knowledge_base in knowledge_bases]
        assert set(knowledge_base_names) == {knowledge_base_name, companion_name}
        assert len(knowledge_base_names) == len(set(knowledge_base_names))
        print(f"Paged through {len(knowledge_bases)} knowledge bases without duplicates")
    finally:
        index_client.delete_knowledge_base(companion_name)
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
    try:
        setup_search_index_knowledge_source(knowledge_source_name, index_name, service_endpoint, key)
        create_knowledge_base()
        get_knowledge_base()
        update_knowledge_base()
        list_knowledge_bases()
        delete_knowledge_base()
    finally:
        cleanup_knowledge_resources(
            service_endpoint,
            key,
            knowledge_base_name=knowledge_base_name,
            knowledge_source_name=knowledge_source_name,
        )
