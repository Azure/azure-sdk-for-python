# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_synonym_map_operations_async.py
DESCRIPTION:
    This sample demonstrates how to get, create, update, or delete a Synonym Map.
USAGE:
    python sample_synonym_map_operations_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - the endpoint of your Azure Cognitive Search service
    2) AZURE_SEARCH_API_KEY - your search API key
"""

import asyncio
import os

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes.aio import SearchIndexClient
from azure.search.documents.indexes.models import SynonymMap

client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

async def create_synonym_map():
    # [START create_synonym_map_async]
    solr_format_synonyms = "\n".join([
        "USA, United States, United States of America",
        "Washington, Wash. => WA",
    ])
    synonym_map = SynonymMap(name="test-syn-map", synonyms=solr_format_synonyms)
    result = await client.create_synonym_map(synonym_map)
    print("Create new Synonym Map 'test-syn-map succeeded")
    # [END create_synonym_map_async]

async def get_synonym_maps():
    # [START get_synonym_maps_async]
    result = await client.get_synonym_maps()
    names = [x.name for x in result]
    print("Found {} Synonym Maps in the service: {}".format(len(result), ", ".join(names)))
    # [END get_synonym_maps_async]

async def get_synonym_map():
    # [START get_synonym_map_async]
    result = await client.get_synonym_map("test-syn-map")
    print("Retrived Synonym Map 'test-syn-map' with synonyms")
    for syn in result.synonyms:
        print("    {}".format(syn))
    # [END get_synonym_map_async]

async def delete_synonym_map():
    # [START delete_synonym_map_async]
    await client.delete_synonym_map("test-syn-map")
    print("Synonym Map 'test-syn-map' deleted")
    # [END delete_synonym_map_async]

async def main():
    await create_synonym_map()
    await get_synonym_maps()
    await get_synonym_map()
    await delete_synonym_map()
    await client.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
