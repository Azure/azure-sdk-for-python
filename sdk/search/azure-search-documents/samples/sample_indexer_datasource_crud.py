# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Demonstrates how to create, get, update, and delete a data source.

USAGE:
    python sample_indexer_datasource_crud.py

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

data_source_connection_name = "hotels-sample-blob"
container_name = "hotels-sample-container"


def create_data_source_connection():
    # [START create_data_source_connection]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexerClient
    from azure.search.documents.indexes.models import (
        SearchIndexerDataContainer,
        SearchIndexerDataSourceConnection,
    )

    indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))

    container = SearchIndexerDataContainer(name=container_name)
    data_source_connection = SearchIndexerDataSourceConnection(
        name=data_source_connection_name,
        type="azureblob",
        connection_string=connection_string,
        container=container,
    )
    result = indexer_client.create_data_source_connection(data_source_connection)
    print(f"Created: data source '{result.name}'")
    # [END create_data_source_connection]


def list_data_source_connections():
    # [START list_data_source_connections]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexerClient

    indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))

    result = indexer_client.get_data_source_connections()
    names = [ds.name for ds in result]
    print(f"Data sources ({len(result)}): {', '.join(names)}")
    # [END list_data_source_connections]


def get_data_source_connection():
    # [START get_data_source_connection]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexerClient

    indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))

    result = indexer_client.get_data_source_connection(data_source_connection_name)
    print(f"Retrieved: data source '{result.name}'")
    # [END get_data_source_connection]


def delete_data_source_connection():
    # [START delete_data_source_connection]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexerClient

    indexer_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))

    indexer_client.delete_data_source_connection(data_source_connection_name)
    print(f"Deleted: data source '{data_source_connection_name}'")
    # [END delete_data_source_connection]


if __name__ == "__main__":
    create_data_source_connection()
    list_data_source_connections()
    get_data_source_connection()
    delete_data_source_connection()
