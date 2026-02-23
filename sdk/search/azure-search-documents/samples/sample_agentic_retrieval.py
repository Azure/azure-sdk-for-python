# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates Knowledge Source and Knowledge Base CRUD operations and
    a minimal retrieval query using a semantic intent.

USAGE:
    python sample_agentic_retrieval.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
        (e.g., https://<your-search-service-name>.search.windows.net)
    2) AZURE_SEARCH_INDEX_NAME - target search index name (e.g., "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - the admin key for your search service
"""

import json
import os

from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient
from azure.search.documents.knowledgebases.models import (
    KnowledgeBaseRetrievalRequest,
    KnowledgeRetrievalSemanticIntent,
    KnowledgeRetrievalMinimalReasoningEffort,
)
from azure.search.documents.indexes.models import (
    KnowledgeBase,
    KnowledgeSourceReference,
    SearchIndexFieldReference,
    SearchIndexKnowledgeSource,
    SearchIndexKnowledgeSourceParameters,
)

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]

knowledge_source_name = "hotels-sample-knowledge-source"
knowledge_base_name = "hotels-sample-knowledge-base"


def create_knowledge_source():
    # [START create_knowledge_source]
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    knowledge_source = SearchIndexKnowledgeSource(
        name=knowledge_source_name,
        search_index_parameters=SearchIndexKnowledgeSourceParameters(search_index_name=index_name),
    )

    index_client.create_or_update_knowledge_source(knowledge_source=knowledge_source)
    print(f"Created: knowledge source '{knowledge_source_name}'")
    # [END create_knowledge_source]


def get_knowledge_source():
    # [START get_knowledge_source]
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    knowledge_source = index_client.get_knowledge_source(knowledge_source_name)
    print(f"Retrieved: knowledge source '{knowledge_source.name}'")
    # [END get_knowledge_source]


def update_knowledge_source():
    # [START update_knowledge_source]
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    knowledge_source = SearchIndexKnowledgeSource(
        name=knowledge_source_name,
        search_index_parameters=SearchIndexKnowledgeSourceParameters(
            search_index_name=index_name,
            source_data_fields=[
                SearchIndexFieldReference(name="HotelId"),
                SearchIndexFieldReference(name="HotelName"),
                SearchIndexFieldReference(name="Description"),
                SearchIndexFieldReference(name="Category"),
                SearchIndexFieldReference(name="Tags"),
            ],
        ),
    )

    index_client.create_or_update_knowledge_source(knowledge_source=knowledge_source)
    print(f"Updated: knowledge source '{knowledge_source_name}'")
    # [END update_knowledge_source]


def delete_knowledge_source():
    # [START delete_knowledge_source]
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    try:
        index_client.delete_knowledge_source(knowledge_source_name)
        print(f"Deleted: knowledge source '{knowledge_source_name}'")
    except ResourceNotFoundError:
        print(f"Skipped: knowledge source '{knowledge_source_name}' not found")
    # [END delete_knowledge_source]


def create_knowledge_base():
    # [START create_knowledge_base]
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    knowledge_base = KnowledgeBase(
        name=knowledge_base_name,
        knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
    )

    index_client.create_or_update_knowledge_base(knowledge_base)
    print(f"Created: knowledge base '{knowledge_base_name}'")
    # [END create_knowledge_base]


def get_knowledge_base():
    # [START get_knowledge_base]
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    knowledge_base = index_client.get_knowledge_base(knowledge_base_name)
    print(f"Retrieved: knowledge base '{knowledge_base.name}'")
    # [END get_knowledge_base]


def update_knowledge_base():
    # [START update_knowledge_base]
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    knowledge_base = KnowledgeBase(
        name=knowledge_base_name,
        knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
        retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
    )

    index_client.create_or_update_knowledge_base(knowledge_base)
    print(f"Updated: knowledge base '{knowledge_base_name}'")
    # [END update_knowledge_base]


def retrieve_knowledge_base():
    # [START retrieve_knowledge_base]
    retrieval_client = KnowledgeBaseRetrievalClient(
        service_endpoint,
        credential=AzureKeyCredential(key),
    )

    request = KnowledgeBaseRetrievalRequest(intents=[KnowledgeRetrievalSemanticIntent(search="hotels with free wifi")])

    result = retrieval_client.retrieve(knowledge_base_name=knowledge_base_name, retrieval_request=request)
    print("Results: knowledge base retrieval")

    response_parts = []
    for resp in result.response or []:
        for content in resp.content or []:
            if hasattr(content, "text"):
                response_parts.append(content.text)

    if response_parts:
        response_content = "\n\n".join(response_parts)

        items = json.loads(response_content)
        for i, item in enumerate(items[:5], start=1):
            print(f"  Result {i}:")
            print(f"    Title: {item.get('title')}")
            print(f"    Content: {item.get('content')}")
    else:
        print("Results: none")
    # [END retrieve_knowledge_base]


def delete_knowledge_base():
    # [START delete_knowledge_base]
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    try:
        index_client.delete_knowledge_base(knowledge_base_name)
        print(f"Deleted: knowledge base '{knowledge_base_name}'")
    except ResourceNotFoundError:
        print(f"Skipped: knowledge base '{knowledge_base_name}' not found")
    # [END delete_knowledge_base]


if __name__ == "__main__":
    create_knowledge_source()
    get_knowledge_source()
    update_knowledge_source()
    create_knowledge_base()
    get_knowledge_base()
    update_knowledge_base()
    retrieve_knowledge_base()
    delete_knowledge_base()
    delete_knowledge_source()
