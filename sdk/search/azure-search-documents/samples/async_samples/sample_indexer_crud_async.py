# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates how to create, get, update, and delete an indexer.

USAGE:
    python sample_indexer_crud_async.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
        (e.g., https://<your-search-service-name>.search.windows.net)
    2) AZURE_SEARCH_API_KEY - the admin key for your search service
    3) AZURE_STORAGE_CONNECTION_STRING - connection string for the Azure Storage account
"""

import asyncio
import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
key = os.environ["AZURE_SEARCH_API_KEY"]
connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
container_name = "hotels-sample-container"
index_name = "hotels-sample-index-indexer-crud"
data_source_name = "hotels-sample-blob"
indexer_name = "hotels-sample-indexer-indexer-crud"


async def create_indexer_async():
    # [START create_indexer_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import (
        SearchIndexClient,
        SearchIndexerClient,
    )
    from azure.search.documents.indexes.models import (
        SearchIndexerDataContainer,
        SearchIndexerDataSourceConnection,
        SearchIndex,
        SearchIndexer,
        SimpleField,
        SearchFieldDataType,
    )

    indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))
    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))

    # create an index
    fields = [
        SimpleField(name="HotelId", type=SearchFieldDataType.STRING, key=True),
        SimpleField(name="BaseRate", type=SearchFieldDataType.DOUBLE),
    ]
    index = SearchIndex(name=index_name, fields=fields)
    async with index_client:
        await index_client.create_index(index)

    # create a datasource
    container = SearchIndexerDataContainer(name=container_name)
    data_source_connection = SearchIndexerDataSourceConnection(
        name=data_source_name,
        type="azureblob",
        connection_string=connection_string,
        container=container,
    )
    async with indexer_client:
        await indexer_client.create_data_source_connection(data_source_connection)

        # create an indexer
        indexer = SearchIndexer(
            name=indexer_name,
            data_source_name=data_source_name,
            target_index_name=index_name,
        )
        result = await indexer_client.create_indexer(indexer)
        print(f"Created: indexer '{result.name}'")
    # [END create_indexer_async]


async def list_indexers_async():
    # [START list_indexers_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexerClient

    indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))

    async with indexer_client:
        result = await indexer_client.get_indexers()
    names = [x.name for x in result]
    print(f"Indexers ({len(result)}): {', '.join(names)}")
    # [END list_indexers_async]


async def get_indexer_async():
    # [START get_indexer_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexerClient

    indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))

    async with indexer_client:
        result = await indexer_client.get_indexer(indexer_name)
    print(f"Retrieved: indexer '{result.name}'")
    return result
    # [END get_indexer_async]


async def get_indexer_status_async():
    # [START get_indexer_status_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexerClient

    indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))

    async with indexer_client:
        result = await indexer_client.get_indexer_status(indexer_name)
    print(f"Status: indexer '{indexer_name}' is {result.status}")
    return result
    # [END get_indexer_status_async]


async def run_indexer_async():
    # [START run_indexer_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexerClient

    indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))

    async with indexer_client:
        await indexer_client.run_indexer(indexer_name)
    print(f"Ran: indexer '{indexer_name}'")
    # [END run_indexer_async]
    return


async def reset_indexer_async():
    # [START reset_indexer_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexerClient

    indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))
    async with indexer_client:
        await indexer_client.reset_indexer(indexer_name)
    print(f"Reset: indexer '{indexer_name}'")
    return
    # [END reset_indexer_async]


async def delete_indexer_async():
    # [START delete_indexer_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexerClient

    indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))
    async with indexer_client:
        await indexer_client.delete_indexer(indexer_name)
    print(f"Deleted: indexer '{indexer_name}'")
    # [END delete_indexer_async]


async def delete_data_source_async():
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexerClient

    indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))
    async with indexer_client:
        await indexer_client.delete_data_source_connection(data_source_name)
    print(f"Deleted: data source '{data_source_name}'")


async def delete_index_async():
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.aio import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    async with index_client:
        await index_client.delete_index(index_name)
    print(f"Deleted: index '{index_name}'")


if __name__ == "__main__":
    asyncio.run(create_indexer_async())
    asyncio.run(list_indexers_async())
    asyncio.run(get_indexer_async())
    asyncio.run(get_indexer_status_async())
    asyncio.run(run_indexer_async())
    asyncio.run(reset_indexer_async())
    asyncio.run(delete_indexer_async())
    asyncio.run(delete_data_source_async())
    asyncio.run(delete_index_async())
