# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_create_client.py

DESCRIPTION:
    These samples demonstrate creating a TableServiceClient and a TableClient

USAGE:
    python sample_create_client.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
    2) AZURE_STORAGE_ACCOUNT_URL - the Table service account URL
    3) AZURE_STORAGE_ACCOUNT_NAME - the name of the storage account
    4) AZURE_STORAGE_ACCESS_KEY - the storage account access key
"""

from datetime import datetime, timedelta
from dotenv import find_dotenv, load_dotenv
import os

class CreateClients(object):

    def __init__(self):
        load_dotenv(find_dotenv())
        # self.connection_string = os.getenv("AZURE_TABLES_CONNECTION_STRING")
        self.access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        self.endpoint = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        self.account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        self.account_url = "{}.table.{}".format(self.account_name, self.endpoint)
        self.connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            self.account_name,
            self.access_key,
            self.endpoint
        )


    def create_table_client(self):
        # Instantiate a TableServiceClient using a connection string
        # [START create_table_client]
        from azure.data.tables import TableClient
        with TableClient.from_connection_string(conn_str=self.connection_string, table_name="tableName") as table_client:
            print("Table name: {}".format(table_client.table_name))
        # [END create_table_client]

    def create_table_service_client(self):
        # Instantiate a TableServiceClient using a shared access key
        # [START create_table_service_client]
        from azure.data.tables import TableServiceClient
        with TableServiceClient(account_url=self.account_url, credential=self.access_key) as table_service:
            properties = table_service.get_service_properties()
            print("Properties: {}".format(properties))
        # [END create_table_service_client]


if __name__ == '__main__':
    sample = CreateClients()
    sample.create_table_client()
    sample.create_table_service_client()
