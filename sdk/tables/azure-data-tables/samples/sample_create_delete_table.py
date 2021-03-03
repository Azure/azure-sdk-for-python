# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_create_delete_table.py

DESCRIPTION:
    These samples demonstrate creating a table and deleting a table ffrom a storage account

USAGE:
    python sample_create_delete_table.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

import os
from dotenv import find_dotenv, load_dotenv


class CreateDeleteTable(object):

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


    def create_table(self):
        from azure.data.tables import TableServiceClient
        from azure.core.exceptions import ResourceExistsError

        # [START create_table_from_tc]
        with TableServiceClient.from_connection_string(self.connection_string) as table_service_client:
            try:
                table_item = table_service_client.create_table(table_name="myTable")
                print("Created table {}!".format(table_item.table_name))
            except ResourceExistsError:
                print("Table already exists")
        # [END create_table_from_tc]

    def create_if_not_exists(self):
        from azure.data.tables import TableServiceClient

        # [START create_table_if_not_exists]
        with TableServiceClient.from_connection_string(self.connection_string) as table_service_client:
            table_item = TableServiceClient.create_table_if_not_exists(table_name="myTable")
            print("Table name: {}".format(table_item.table_name))
        # [END create_table_if_not_exists]

    def delete_table(self):
        from azure.data.tables import TableServiceClient
        from azure.core.exceptions import ResourceNotFoundError

        # [START delete_table_from_tc]
        with TableServiceClient.from_connection_string(self.connection_string) as table_service_client:
            try:
                table_service_client.delete_table(table_name="myTable")
                print("Deleted table {}!".format("myTable"))
            except ResourceNotFoundError:
                print("Table could not be found")
        # [END delete_table_from_tc]

    def create_from_table_client(self):
        from azure.data.table import TableClient

        # [START create_table_from_table_client]
        with TableClient.from_connection_string(conn_str=self.connection_string, table_name="myTable") as table_client:
            try:
                table_item = table_client.create_table()
                print("Created table {}!".format(table_item.table_name))
            except ResourceExistsError:
                print("Table already exists")
        # [END create_table_from_table_client]

    def delete_from_table_client(self):
        from azure.data.table import TableClient

        # [START delete_table_from_table_client]
        with TableClient.from_connection_string(conn_str=self.connection_string, table_name="myTable") as table_client:
            try:
                table_client.delete_table()
                print("Deleted table {}!".format("myTable"))
            except ResourceNotFoundError:
                print("Table could not be found")
        # [END delete_table_from_table_client]


if __name__ == '__main__':
    sample = CreateDeleteTable()
    sample.create_table()
    sample.delete_table()
