# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_indexer_operations.py
DESCRIPTION:
    This sample demonstrates how to get, create, update, or delete a Indexer.
USAGE:
    python sample_indexer_operations.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - the endpoint of your Azure Cognitive Search service
    2) AZURE_SEARCH_API_KEY - your search API key
"""

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
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient

indexers_client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))

def create_indexer():
    # create an index
    index_name = "indexer-hotels"
    fields = [
        SimpleField(name="hotelId", type=SearchFieldDataType.String, key=True),
        SimpleField(name="baseRate", type=SearchFieldDataType.Double)
    ]
    index = SearchIndex(name=index_name, fields=fields)
    ind_client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    ind_client.create_index(index)

    # [START create_indexer]
    # create a datasource
    container = SearchIndexerDataContainer(name='searchcontainer')
    data_source_connection = SearchIndexerDataSourceConnection(
        name="indexer-datasource",
        type="azureblob",
        connection_string=connection_string,
        container=container
    )
    data_source = indexers_client.create_data_source_connection(data_source_connection)

    # create an indexer
    indexer = SearchIndexer(
        name="sample-indexer",
        data_source_name="indexer-datasource",
        target_index_name="indexer-hotels"
    )
    result = indexers_client.create_indexer(indexer)
    print("Create new Indexer - sample-indexer")
    # [END create_indexer]

def list_indexers():
    # [START list_indexer]
    result = indexers_client.get_indexers()
    names = [x.name for x in result]
    print("Found {} Indexers in the service: {}".format(len(result), ", ".join(names)))
    # [END list_indexer]

def get_indexer():
    # [START get_indexer]
    result = indexers_client.get_indexer("sample-indexer")
    print("Retrived Indexer 'sample-indexer'")
    return result
    # [END get_indexer]

def get_indexer_status():
    # [START get_indexer_status]
    result = indexers_client.get_indexer_status("sample-indexer")
    print("Retrived Indexer status for 'sample-indexer'")
    return result
    # [END get_indexer_status]

def run_indexer():
    # [START run_indexer]
    result = indexers_client.run_indexer("sample-indexer")
    print("Ran the Indexer 'sample-indexer'")
    return result
    # [END run_indexer]

def reset_indexer():
    # [START reset_indexer]
    result = indexers_client.reset_indexer("sample-indexer")
    print("Reset the Indexer 'sample-indexer'")
    return result
    # [END reset_indexer]

def delete_indexer():
    # [START delete_indexer]
    indexers_client.delete_indexer("sample-indexer")
    print("Indexer 'sample-indexer' successfully deleted")
    # [END delete_indexer]

if __name__ == '__main__':
    create_indexer()
    list_indexers()
    get_indexer()
    get_indexer_status()
    run_indexer()
    reset_indexer()
    delete_indexer()
