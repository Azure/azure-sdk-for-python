# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_data_source_operations_async.py
DESCRIPTION:
    This sample demonstrates how to get, create, update, or delete a Data Source.
USAGE:
    python sample_data_source_operations_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - the endpoint of your Azure Cognitive Search service
    2) AZURE_SEARCH_API_KEY - your search API key
"""

import asyncio
import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
key = os.environ["AZURE_SEARCH_API_KEY"]
connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes.models import SearchIndexerDataContainer, SearchIndexerDataSourceConnection
from azure.search.documents.indexes.aio import SearchIndexerClient

client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))


async def create_data_source_connection():
    # [START create_data_source_connection_async]
    container = SearchIndexerDataContainer(name="searchcontainer")
    data_source = SearchIndexerDataSourceConnection(
        name="async-sample-data-source-connection",
        type="azureblob",
        connection_string=connection_string,
        container=container,
    )
    result = await client.create_data_source_connection(data_source)
    print("Create new Data Source Connection - async-sample-data-source-connection")
    # [END create_data_source_connection_async]


async def list_data_source_connections():
    # [START list_data_source_connection_async]
    result = await client.get_data_source_connections()
    names = [x.name for x in result]
    print("Found {} Data Source Connections in the service: {}".format(len(result), ", ".join(names)))
    # [END list_data_source_connection_async]


async def get_data_source_connection():
    # [START get_data_source_connection_async]
    result = await client.get_data_source_connection("async-sample-data-source-connection")
    print("Retrived Data Source Connection 'async-sample-data-source-connection'")
    return result
    # [END get_data_source_connection_async]


async def delete_data_source_connection():
    # [START delete_data_source_connection_async]
    await client.delete_data_source_connection("async-sample-data-source-connection")
    print("Data Source Connection 'async-sample-data-source-connection' successfully deleted")
    # [END delete_data_source_connection_async]


async def main():
    await create_data_source_connection()
    await list_data_source_connections()
    await get_data_source_connection()
    await delete_data_source_connection()
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
