# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_vector_search_async.py
DESCRIPTION:
    This sample demonstrates how to get search results from a basic search text
    from an Azure Search index.
USAGE:
    python sample_vector_search_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - the endpoint of your Azure Cognitive Search service
    2) AZURE_SEARCH_INDEX_NAME - the name of your search index (e.g. "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - your search API key
"""

import os
import asyncio

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import Vector

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
key = os.getenv("AZURE_SEARCH_API_KEY")


def get_embeddings(text: str):
    # There are a few ways to get embeddings. This is just one example.
    import openai

    open_ai_endpoint = os.getenv("OpenAIEndpoint")
    open_ai_key = os.getenv("OpenAIKey")

    openai.api_version = "2022-12-01"
    openai.api_base = open_ai_endpoint
    openai.api_type = "azure"
    openai.api_key = open_ai_key
    model_id = "text-embedding-ada-002"
    embedding = openai.Embedding.create(input=text, deployment_id=model_id)["data"][0]["embedding"]
    return embedding


def get_hotel_index(name: str):
    from azure.search.documents.indexes.models import (
        SearchIndex,
        SearchField,
        SearchFieldDataType,
        SimpleField,
        SearchableField,
        VectorSearch,
        HnswVectorSearchAlgorithmConfiguration,
    )

    fields = [
        SimpleField(name="hotelId", type=SearchFieldDataType.String, key=True),
        SearchableField(name="hotelName", type=SearchFieldDataType.String, sortable=True, filterable=True),
        SearchableField(name="description", type=SearchFieldDataType.String),
        SearchField(
            name="descriptionVector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_configuration="my-vector-config",
        ),
        SearchableField(
            name="category", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True
        ),
    ]
    vector_search = VectorSearch(
        algorithm_configurations=[HnswVectorSearchAlgorithmConfiguration(name="my-vector-config", kind="hnsw")]
    )
    return SearchIndex(name=name, fields=fields, vector_search=vector_search)


def get_hotel_documents():
    docs = [
        {
            "hotelId": "1",
            "hotelName": "Fancy Stay",
            "description": "Best hotel in town if you like luxury hotels.",
            "descriptionVector": get_embeddings("Best hotel in town if you like luxury hotels."),
            "category": "Luxury",
        },
        {
            "hotelId": "2",
            "hotelName": "Roach Motel",
            "descrdescriptioniption": "Cheapest hotel in town. Infact, a motel.",
            "descriptionVector": get_embeddings("Cheapest hotel in town. Infact, a motel."),
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


async def single_vector_search():
    # [START single_vector_search]
    query = "Top hotels in town"

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
    vector = Vector(value=get_embeddings(query), k=3, fields="descriptionVector")

    async with search_client:
        results = await search_client.search(
            search_text="",
            vectors=[vector],
            select=["hotelId", "hotelName"],
        )

        async for result in results:
            print(result)
    # [END single_vector_search]


async def single_vector_search_with_filter():
    # [START single_vector_search_with_filter]
    query = "Top hotels in town"

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
    vector = Vector(value=get_embeddings(query), k=3, fields="descriptionVector")

    async with search_client:
        results = await search_client.search(
            search_text="",
            vectors=[vector],
            filter="category eq 'Luxury'",
            select=["hotelId", "hotelName"],
        )

        async for result in results:
            print(result)
    # [END single_vector_search_with_filter]


async def simple_hybrid_search():
    # [START simple_hybrid_search]
    query = "Top hotels in town"

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
    vector = Vector(value=get_embeddings(query), k=3, fields="descriptionVector")

    async with search_client:
        results = await search_client.search(
            search_text=query,
            vectors=[vector],
            select=["hotelId", "hotelName"],
        )
        print(await results.get_answers())
        async for result in results:
            print(result)
    # [END simple_hybrid_search]


async def main():
    credential = AzureKeyCredential(key)
    index_client = SearchIndexClient(service_endpoint, credential)
    index = get_hotel_index(index_name)
    index_client.create_index(index)
    client = SearchClient(service_endpoint, index_name, credential)
    hotel_docs = get_hotel_documents()
    await client.upload_documents(documents=hotel_docs)

    await single_vector_search()
    await single_vector_search_with_filter()
    await simple_hybrid_search()


if __name__ == "__main__":
    asyncio.run(main())
