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
from azure.search.documents import SearchServiceClient, DataSource, DataContainer, DataSourceCredentials

service_client = SearchServiceClient(service_endpoint, AzureKeyCredential(key))

def create_data_source():
    # [START create_data_source]
    credentials = DataSourceCredentials(connection_string=connection_string)
    container = DataContainer(name='searchcontainer')
    data_source = DataSource(name="sample-datasource", type="azureblob", credentials=credentials, container=container)
    result = service_client.create_datasource(data_source)
    print(result)
    print("Create new Data Source - sample-datasource")
    # [END create_data_source]

def list_data_sources():
    # [START list_data_source]
    result = service_client.get_datasources()
    names = [ds.name for ds in result]
    print("Found {} Data Sources in the service: {}".format(len(result), ", ".join(names)))
    # [END list_data_source]

def get_data_source():
    # [START get_data_source]
    result = service_client.get_datasource("sample-datasource")
    print("Retrived Data Source 'sample-datasource'")
    # [END get_data_source]

def delete_data_source():
    # [START delete_data_source]
    service_client.delete_datasource("sample-datasource")
    print("Data Source 'sample-datasource' successfully deleted")
    # [END delete_data_source]

if __name__ == '__main__':
    create_data_source()
    list_data_sources()
    get_data_source()
    delete_data_source()
