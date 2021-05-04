# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_indexer_operations_async.py
DESCRIPTION:
    This sample demonstrates how to get, create, update, or delete a Indexer.
USAGE:
    python sample_indexer_operations_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - the endpoint of your Azure Cognitive Search service
    2) AZURE_SEARCH_API_KEY - your search API key
"""

import asyncio
import os

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SearchIndex,
    SearchIndexer,
    SimpleField,
    SearchFieldDataType
)
from azure.search.documents.indexes.aio import SearchIndexerClient, SearchIndexClient

indexers_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))

async def create_indexer():
    # create an index
    index_name = "async-indexer-hotels"
    fields = [
        SimpleField(name="hotelId", type=SearchFieldDataType.String, key=True),
        SimpleField(name="baseRate", type=SearchFieldDataType.Double)
    ]
    index = SearchIndex(name=index_name, fields=fields)
    ind_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    async with ind_client:
        await ind_client.create_index(index)

    # [START create_indexer_async]
    # create a datasource
    container = SearchIndexerDataContainer(name='searchcontainer')
    data_source_connection = SearchIndexerDataSourceConnection(
        name="async-indexer-datasource",
        type="azureblob",
        connection_string=connection_string,
        container=container
    )
    data_source = await indexers_client.create_data_source_connection(data_source_connection)

    # create an indexer
    indexer = SearchIndexer(
        name="async-sample-indexer",
        data_source_name="async-indexer-datasource",
        target_index_name="async-indexer-hotels"
    )
    result = await indexers_client.create_indexer(indexer)
    print("Create new Indexer - async-sample-indexer")
    # [END create_indexer_async]

async def list_indexers():
    # [START list_indexer_async]
    result = await indexers_client.get_indexers()
    names = [x.name for x in result]
    print("Found {} Indexers in the service: {}".format(len(result), ", ".join(names)))
    # [END list_indexer_async]

async def get_indexer():
    # [START get_indexer_async]
    result = await indexers_client.get_indexer("async-sample-indexer")
    print("Retrived Indexer 'async-sample-indexer'")
    return result
    # [END get_indexer_async]

async def get_indexer_status():
    # [START get_indexer_status_async]
    result = await indexers_client.get_indexer_status("async-sample-indexer")
    print("Retrived Indexer status for 'async-sample-indexer'")
    return result
    # [END get_indexer_status_async]

async def run_indexer():
    # [START run_indexer_async]
    result = await indexers_client.run_indexer("async-sample-indexer")
    print("Ran the Indexer 'async-sample-indexer'")
    return result
    # [END run_indexer_async]

async def reset_indexer():
    # [START reset_indexer_async]
    result = await indexers_client.reset_indexer("async-sample-indexer")
    print("Reset the Indexer 'async-sample-indexer'")
    return result
    # [END reset_indexer_async]

async def delete_indexer():
    # [START delete_indexer_async]
    await indexers_client.delete_indexer("async-sample-indexer")
    print("Indexer 'async-sample-indexer' successfully deleted")
    # [END delete_indexer_async]

async def main():
    await create_indexer()
    await list_indexers()
    await get_indexer()
    await get_indexer_status()
    await run_indexer()
    await reset_indexer()
    await delete_indexer()
    await indexers_client.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
