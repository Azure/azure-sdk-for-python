# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_data_source_operations.py
DESCRIPTION:
    This sample demonstrates how to get, create, update, or delete a Data Source.
USAGE:
    python sample_data_source_operations.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - the endpoint of your Azure Cognitive Search service
    2) AZURE_SEARCH_API_KEY - your search API key
"""

import os

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import SearchIndexerDataContainer, SearchIndexerDataSourceConnection

client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))

def create_data_source_connection():
    # [START create_data_source_connection]
    container = SearchIndexerDataContainer(name='searchcontainer')
    data_source_connection = SearchIndexerDataSourceConnection(
        name="sample-data-source-connection",
        type="azureblob",
        connection_string=connection_string,
        container=container
    )
    result = client.create_data_source_connection(data_source_connection)
    print(result)
    print("Create new Data Source Connection - sample-data-source-connection")
    # [END create_data_source_connection]

def list_data_source_connections():
    # [START list_data_source_connection]
    result = client.get_data_source_connections()
    names = [ds.name for ds in result]
    print("Found {} Data Source Connections in the service: {}".format(len(result), ", ".join(names)))
    # [END list_data_source_connection]

def get_data_source_connection():
    # [START get_data_source_connection]
    result = client.get_data_source_connection("sample-data-source-connection")
    print("Retrived Data Source Connection 'sample-data-source-connection'")
    # [END get_data_source_connection]

def delete_data_source_connection():
    # [START delete_data_source_connection]
    client.delete_data_source_connection("sample-data-source-connection")
    print("Data Source Connection 'sample-data-source-connection' successfully deleted")
    # [END delete_data_source_connection]

if __name__ == '__main__':
    create_data_source_connection()
    list_data_source_connections()
    get_data_source_connection()
    delete_data_source_connection()
