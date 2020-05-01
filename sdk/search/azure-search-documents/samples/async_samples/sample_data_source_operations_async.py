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

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import DataSource, DataContainer, DataSourceCredentials
from azure.search.documents.aio import SearchServiceClient

service_client = SearchServiceClient(service_endpoint, AzureKeyCredential(key))

async def create_data_source():
    # [START create_data_source_async]
    credentials = DataSourceCredentials(connection_string=connection_string)
    container = DataContainer(name='searchcontainer')
    data_source = DataSource(name="async-sample-datasource", type="azureblob", credentials=credentials, container=container)
    async with service_client:
        result = await service_client.create_datasource(data_source)
    print("Create new Data Source - async-sample-datasource")
    # [END create_data_source_async]

async def list_data_sources():
    # [START list_data_source_async]
    async with service_client:
        result = await service_client.get_datasources()
    names = [x.name for x in result]
    print("Found {} Data Sources in the service: {}".format(len(result), ", ".join(names)))
    # [END list_data_source_async]

async def get_data_source():
    # [START get_data_source_async]
    async with service_client:
        result = await service_client.get_datasource("async-sample-datasource")
        print("Retrived Data Source 'async-sample-datasource'")
        return result
    # [END get_data_source_async]

async def delete_data_source():
    # [START delete_data_source_async]
    async with service_client:
        service_client.delete_datasource("async-sample-datasource")
    print("Data Source 'async-sample-datasource' successfully deleted")
    # [END delete_data_source_async]

async def main():
    await create_data_source()
    await list_data_sources()
    await get_data_source()
    await delete_data_source()
    await service_client.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
