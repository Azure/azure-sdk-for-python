# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_hybrid_semantic_ranking.py
DESCRIPTION:
    This sample demonstrates how to use hybrid search + semantic ranking.
USAGE:
    python sample_hybrid_semantic_ranking.py
  
    Set the environment variables with your own values before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - the endpoint of your Azure Cognitive Search service
    2) AZURE_SEARCH_INDEX_NAME - the name of your search index (e.g. "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - your search API key
"""

import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizedQuery

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]


def get_embeddings(text: str):
    # There are a few ways to get embeddings. This is just one example.
    import openai

    open_ai_endpoint = os.getenv("OpenAIEndpoint")
    open_ai_key = os.getenv("OpenAIKey")

    client = openai.AzureOpenAI(
        azure_endpoint=open_ai_endpoint,
        api_key=open_ai_key,
        api_version="2023-09-01-preview",
    )
    embedding = client.embeddings.create(input=[text], model="text-embedding-ada-002")
    return embedding.data[0].embedding


def get_hotel_index(name: str):
    from azure.search.documents.indexes.models import (
        SearchIndex,
        SearchField,
        SearchFieldDataType,
        SimpleField,
        SearchableField,
        VectorSearch,
        VectorSearchProfile,
        HnswAlgorithmConfiguration,
        SemanticConfiguration,
        SemanticSearch,
        SemanticPrioritizedFields,
        SemanticField,
    )

    fields = [
        SimpleField(name="hotelId", type=SearchFieldDataType.String, key=True),
        SearchableField(
            name="hotelName",
            type=SearchFieldDataType.String,
            sortable=True,
            filterable=True,
        ),
        SearchableField(name="description", type=SearchFieldDataType.String),
        SearchField(
            name="descriptionVector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_profile_name="my-vector-config",
        ),
        SearchableField(
            name="category",
            type=SearchFieldDataType.String,
            sortable=True,
            filterable=True,
            facetable=True,
        ),
    ]
    vector_search = VectorSearch(
        profiles=[
            VectorSearchProfile(
                name="my-vector-config",
                algorithm_configuration_name="my-algorithms-config",
            )
        ],
        algorithms=[HnswAlgorithmConfiguration(name="my-algorithms-config")],
    )

    semantic_config = SemanticConfiguration(
        name="my-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="hotelName"),
            content_fields=[
                SemanticField(field_name="description"),
            ],
            keywords_fields=[],
        ),
    )

    semantic_settings = SemanticSearch(configurations=[semantic_config])

    index = SearchIndex(
        name=name,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_settings,
    )

    return index


def get_hotel_documents():
    docs = [
        {
            "hotelId": "1",
            "hotelName": "Fancy Stay",
            "description": "Best hotel in town if you like luxury hotels.",
            "descriptionVector": get_embeddings(
                "Best hotel in town if you like luxury hotels."
            ),
            "category": "Luxury",
        },
        {
            "hotelId": "2",
            "hotelName": "Roach Motel",
            "description": "Cheapest hotel in town. Infact, a motel.",
            "descriptionVector": get_embeddings(
                "Cheapest hotel in town. Infact, a motel."
            ),
            "category": "Budget",
        },
        {
            "hotelId": "3",
            "hotelName": "EconoStay",
            "description": "Very popular hotel in town.",
            "descriptionVector": get_embeddings("Very popular hotel in town."),
            "category": "Budget",
        },
        {
            "hotelId": "4",
            "hotelName": "Modern Stay",
            "description": "Modern architecture, very polite staff and very clean. Also very affordable.",
            "descriptionVector": get_embeddings(
                "Modern architecture, very polite staff and very clean. Also very affordable."
            ),
            "category": "Luxury",
        },
        {
            "hotelId": "5",
            "hotelName": "Secret Point",
            "description": "One of the best hotel in town. The hotel is ideally located on the main commercial artery of the city in the heart of New York.",
            "descriptionVector": get_embeddings(
                "One of the best hotel in town. The hotel is ideally located on the main commercial artery of the city in the heart of New York."
            ),
            "category": "Boutique",
        },
    ]
    return docs


def simple_hybrid_search_plus_semantic_ranking():
    # [START simple_hybrid_search_plus_semantic_ranking]
    query = "Top hotels in town"

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
    vector_query = VectorizedQuery(
        vector=get_embeddings(query), k_nearest_neighbors=3, fields="descriptionVector"
    )

    results = search_client.search(
        search_text=query,
        vector_queries=[vector_query],
        select=["hotelId", "hotelName"],
        query_type="semantic",
        semantic_configuration_name="my-semantic-config",
        query_caption="extractive",
        query_answer="extractive",
    )
    print(results.get_answers())
    for result in results:
        print(result)
    # [END simple_hybrid_search_plus_semantic_ranking]


if __name__ == "__main__":
    credential = AzureKeyCredential(key)
    index_client = SearchIndexClient(service_endpoint, credential)
    index = get_hotel_index(index_name)
    index_client.create_index(index)
    client = SearchClient(service_endpoint, index_name, credential)
    hotel_docs = get_hotel_documents()
    client.upload_documents(documents=hotel_docs)

    simple_hybrid_search_plus_semantic_ranking()
