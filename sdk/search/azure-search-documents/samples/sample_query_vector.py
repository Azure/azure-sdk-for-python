# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates how to create a vector-enabled index, upload documents with
    pre-computed DescriptionVector values, and run vector queries.

USAGE:
    python sample_query_vector.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
    2) AZURE_SEARCH_API_KEY - the primary admin key for your search service

NOTE:
    This sample uses a pre-computed vector for the query "quintessential lodging
    near running trails, eateries, retail" instead of calling an embedding API.
    The vector was generated using text-embedding-ada-002 (1536 dimensions).
"""

import json
import os
from pathlib import Path
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SimpleField,
    SearchField,
    SearchFieldDataType,
    SearchableField,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
    ExhaustiveKnnAlgorithmConfiguration,
)

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
key = os.environ["AZURE_SEARCH_API_KEY"]

index_name = "hotels-sample-index-query-vector"
data_dir = Path(__file__).resolve().parent / "data"
documents_path = data_dir / "hotels_with_description_vector.json"
query_vector_path = data_dir / "query_vector.json"


def load_query_vector(query_vector_path):
    """Load the query vector from the samples/data folder."""
    with open(query_vector_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


vector = load_query_vector(query_vector_path)


def create_index():
    """Create or update the vector-enabled search index."""
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    fields = [
        SimpleField(name="HotelId", type=SearchFieldDataType.STRING, key=True, filterable=True),
        SearchableField(name="HotelName", type=SearchFieldDataType.STRING, sortable=True),
        SearchableField(name="Description", type=SearchFieldDataType.STRING),
        SearchField(
            name="DescriptionVector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.SINGLE),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_profile_name="my-vector-profile",
        ),
        SearchableField(
            name="Category",
            type=SearchFieldDataType.STRING,
            sortable=True,
            filterable=True,
            facetable=True,
        ),
        SearchField(
            name="Tags",
            type=SearchFieldDataType.Collection(SearchFieldDataType.STRING),
            searchable=True,
            filterable=True,
            facetable=True,
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(name="my-hnsw-vector-config-1", kind="hnsw"),
            ExhaustiveKnnAlgorithmConfiguration(name="my-eknn-vector-config", kind="exhaustiveKnn"),
        ],
        profiles=[
            VectorSearchProfile(
                name="my-vector-profile",
                algorithm_configuration_name="my-hnsw-vector-config-1",
            )
        ],
    )

    semantic_config = SemanticConfiguration(
        name="my-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="HotelName"),
            content_fields=[SemanticField(field_name="Description")],
            keywords_fields=[SemanticField(field_name="Category")],
        ),
    )

    semantic_search = SemanticSearch(configurations=[semantic_config])

    index = SearchIndex(
        name=index_name,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search,
    )

    result = index_client.create_or_update_index(index)
    print(f"Created: index '{result.name}'")


def load_documents():
    with open(documents_path, "r", encoding="utf-8") as handle:
        raw = handle.read().strip()

    payload = json.loads(raw)
    documents = payload["value"]

    return documents


def upload_documents():
    """Upload documents to the search index."""
    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
    documents = load_documents()
    result = search_client.upload_documents(documents=documents)
    print(f"Uploaded: {len(result)} documents to index '{index_name}'")


def single_vector_search():
    """Perform a single vector search using a pre-computed query vector."""
    # [START single_vector_search]
    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

    vector_query = VectorizedQuery(
        vector=vector,
        k=5,
        fields="DescriptionVector",
    )

    results = search_client.search(
        vector_queries=[vector_query],
        select=["HotelId", "HotelName", "Description", "Category", "Tags"],
        top=5,
    )

    print("Results: single vector search")
    for result in results:
        print(
            f"  HotelId: {result['HotelId']}, HotelName: {result['HotelName']}, " f"Category: {result.get('Category')}"
        )
    # [END single_vector_search]


def single_vector_search_with_filter():
    """Perform a vector search with a filter applied."""
    # [START single_vector_search_with_filter]
    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

    vector_query = VectorizedQuery(
        vector=vector,
        k=5,
        fields="DescriptionVector",
    )

    results = search_client.search(
        vector_queries=[vector_query],
        filter="Tags/any(tag: tag eq 'free wifi')",
        select=["HotelId", "HotelName", "Description", "Category", "Tags"],
        top=5,
    )

    print("Results: vector search with filter")
    for result in results:
        print(f"  HotelId: {result['HotelId']}, HotelName: {result['HotelName']}, " f"Tags: {result.get('Tags')}")
    # [END single_vector_search_with_filter]


def simple_hybrid_search():
    """Perform a hybrid search combining vector and text search."""
    # [START simple_hybrid_search]
    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

    vector_query = VectorizedQuery(
        vector=vector,
        k=5,
        fields="DescriptionVector",
    )

    results = search_client.search(
        search_text="historic hotel walk to restaurants and shopping",
        vector_queries=[vector_query],
        select=["HotelId", "HotelName", "Description", "Category", "Tags"],
        top=5,
    )

    print("Results: hybrid search")
    for result in results:
        score = result.get("@search.score", "N/A")
        print(f"  Score: {score}")
        print(f"  HotelId: {result['HotelId']}")
        print(f"  HotelName: {result['HotelName']}")
        print(f"  Description: {result.get('Description')}")
        print(f"  Category: {result.get('Category')}")
        print(f"  Tags: {result.get('Tags', 'N/A')}")
        print()
    # [END simple_hybrid_search]


def delete_index():
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    index_client.delete_index(index_name)
    print(f"Deleted: index '{index_name}'")


if __name__ == "__main__":
    print("Query: 'quintessential lodging near running trails, eateries, retail'")
    try:
        create_index()
        upload_documents()
        single_vector_search()
        print()
        single_vector_search_with_filter()
        print()
        simple_hybrid_search()
        print()
    finally:
        delete_index()
