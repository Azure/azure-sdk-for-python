# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates how to create, get, update, and delete a synonym map.
USAGE:
    python sample_index_synonym_map_crud_async.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
    2) AZURE_SEARCH_API_KEY - the primary admin key for your search service
"""

import asyncio
import os
from pathlib import Path

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
key = os.environ["AZURE_SEARCH_API_KEY"]

map1 = "hotels-sample-synonym-map"
map2 = "hotels-sample-synonym-map-file"
file_path = Path(__file__).resolve().parents[1] / "data" / "synonym_map.txt"


async def create_synonym_map_async(name):
    # [START create_synonym_map_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import SynonymMap

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    synonyms = [
        "USA, United States, United States of America",
        "Washington, Wash. => WA",
    ]
    synonym_map = SynonymMap(name=name, synonyms=synonyms)
    async with index_client:
        result = await index_client.create_synonym_map(synonym_map)
    print(f"Created: synonym map '{result.name}'")
    # [END create_synonym_map_async]


async def create_synonym_map_from_file_async(name):
    # [START create_synonym_map_from_file_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import SynonymMap

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    with open(file_path, "r") as f:
        solr_format_synonyms = f.read()
        synonyms = solr_format_synonyms.split("\n")
        synonym_map = SynonymMap(name=name, synonyms=synonyms)
        async with index_client:
            result = await index_client.create_synonym_map(synonym_map)
        print(f"Created: synonym map '{result.name}'")
    # [END create_synonym_map_from_file_async]


async def get_synonym_maps_async():
    # [START get_synonym_maps_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    async with index_client:
        result = await index_client.get_synonym_maps()
    names = [x.name for x in result]
    print(f"Synonym maps ({len(result)}): {', '.join(names)}")
    # [END get_synonym_maps_async]


async def get_synonym_map_async(name):
    # [START get_synonym_map_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    async with index_client:
        result = await index_client.get_synonym_map(name)
    print(f"Retrieved: synonym map '{name}'")
    if result:
        for syn in result.synonyms:
            print(f"  {syn}")
    # [END get_synonym_map_async]


async def delete_synonym_map_async(name):
    # [START delete_synonym_map_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    async with index_client:
        await index_client.delete_synonym_map(name)
    print(f"Deleted: synonym map '{name}'")
    # [END delete_synonym_map_async]


if __name__ == "__main__":
    asyncio.run(create_synonym_map_async(map1))
    asyncio.run(create_synonym_map_from_file_async(map2))
    asyncio.run(get_synonym_maps_async())
    asyncio.run(get_synonym_map_async(map1))
    asyncio.run(delete_synonym_map_async(map1))
    asyncio.run(delete_synonym_map_async(map2))
