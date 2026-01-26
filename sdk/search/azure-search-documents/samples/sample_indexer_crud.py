# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates how to create, get, update, and delete an indexer.

USAGE:
    python sample_indexer_crud.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
        (e.g., https://<your-search-service-name>.search.windows.net)
    2) AZURE_SEARCH_API_KEY - the admin key for your search service
    3) AZURE_STORAGE_CONNECTION_STRING - connection string for the Azure Storage account
"""

import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
key = os.environ["AZURE_SEARCH_API_KEY"]
connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
container_name = "hotels-sample-container"
index_name = "hotels-sample-index-indexer-crud"
data_source_name = "hotels-sample-blob"
indexer_name = "hotels-sample-indexer-indexer-crud"


def create_indexer():
    # [START create_indexer]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
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
        SimpleField(name="HotelId", type=SearchFieldDataType.String, key=True),
        SimpleField(name="BaseRate", type=SearchFieldDataType.Double),
    ]
    index = SearchIndex(name=index_name, fields=fields)
    index_client.create_index(index)

    # create a datasource
    container = SearchIndexerDataContainer(name=container_name)
    data_source_connection = SearchIndexerDataSourceConnection(
        name=data_source_name,
        type="azureblob",
        connection_string=connection_string,
        container=container,
    )
    indexer_client.create_data_source_connection(data_source_connection)

    # create an indexer
    indexer = SearchIndexer(
        name=indexer_name,
        data_source_name=data_source_name,
        target_index_name=index_name,
    )
    result = indexer_client.create_indexer(indexer)
    print(f"Created: indexer '{result.name}'")
    # [END create_indexer]


def list_indexers():
    # [START list_indexers]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexerClient

    indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))

    result = indexer_client.get_indexers()
    names = [x.name for x in result]
    print(f"Indexers ({len(result)}): {', '.join(names)}")
    # [END list_indexers]


def get_indexer():
    # [START get_indexer]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexerClient

    indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))

    result = indexer_client.get_indexer(indexer_name)
    print(f"Retrieved: indexer '{result.name}'")
    return result
    # [END get_indexer]


def get_indexer_status():
    # [START get_indexer_status]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexerClient

    indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))

    status = indexer_client.get_indexer_status(indexer_name)
    print(f"Status: indexer '{indexer_name}' is {status.status}")
    return status
    # [END get_indexer_status]


def run_indexer():
    # [START run_indexer]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexerClient

    indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))

    indexer_client.run_indexer(indexer_name)
    print(f"Ran: indexer '{indexer_name}'")
    # [END run_indexer]


def reset_indexer():
    # [START reset_indexer]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexerClient

    indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))
    result = indexer_client.reset_indexer(indexer_name)
    print(f"Reset: indexer '{indexer_name}'")
    return result
    # [END reset_indexer]


def delete_indexer():
    # [START delete_indexer]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexerClient

    indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))
    indexer_client.delete_indexer(indexer_name)
    print(f"Deleted: indexer '{indexer_name}'")
    # [END delete_indexer]


def delete_data_source():
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexerClient

    indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))
    indexer_client.delete_data_source_connection(data_source_name)
    print(f"Deleted: data source '{data_source_name}'")


def delete_index():
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient

    index_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    index_client.delete_index(index_name)
    print(f"Deleted: index '{index_name}'")


if __name__ == "__main__":
    create_indexer()
    list_indexers()
    get_indexer()
    get_indexer_status()
    run_indexer()
    reset_indexer()
    delete_indexer()
    delete_data_source()
    delete_index()
