# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_create_delete_table.py

DESCRIPTION:
    These samples demonstrate creating and deleting individual tables from the
    TableServiceClient and TableClient

USAGE:
    python sample_create_delete_table.py

    Set the environment variables with your own values before running the sample:
    1) TABLES_STORAGE_ENDPOINT_SUFFIX - the Table service account URL suffix
    2) TABLES_STORAGE_ACCOUNT_NAME - the name of the storage account
    3) TABLES_PRIMARY_STORAGE_ACCOUNT_KEY - the storage account access key
"""

import os
from dotenv import find_dotenv, load_dotenv


class CreateDeleteTable(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.environ["TABLES_PRIMARY_STORAGE_ACCOUNT_KEY"]
        self.endpoint_suffix = os.environ["TABLES_STORAGE_ENDPOINT_SUFFIX"]
        self.account_name = os.environ["TABLES_STORAGE_ACCOUNT_NAME"]
        self.connection_string = f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.access_key};EndpointSuffix={self.endpoint_suffix}"
        self.table_name = "myTable"

    def create_table(self):
        from azure.data.tables import TableServiceClient
        from azure.core.exceptions import ResourceExistsError

        # [START create_table_from_tsc]
        with TableServiceClient.from_connection_string(self.connection_string) as table_service_client:
            try:
                table_client = table_service_client.create_table(table_name=self.table_name)
                print(f"Created table {table_client.table_name}!")
            except ResourceExistsError:
                print("Table already exists")
        # [END create_table_from_tsc]

    def create_if_not_exists(self):
        from azure.data.tables import TableServiceClient

        # [START create_table_if_not_exists]
        with TableServiceClient.from_connection_string(self.connection_string) as table_service_client:
            table_client = table_service_client.create_table_if_not_exists(table_name=self.table_name)
            print(f"Table name: {table_client.table_name}")
        # [END create_table_if_not_exists]

    def delete_table(self):
        from azure.data.tables import TableServiceClient

        # [START delete_table_from_tc]
        with TableServiceClient.from_connection_string(self.connection_string) as table_service_client:
            table_service_client.delete_table(table_name=self.table_name)
            print(f"Deleted table {self.table_name}!")
        # [END delete_table_from_tc]

    def create_from_table_client(self):
        from azure.data.tables import TableClient
        from azure.core.exceptions import ResourceExistsError

        # [START create_table_from_table_client]
        with TableClient.from_connection_string(
            conn_str=self.connection_string, table_name=self.table_name
        ) as table_client:
            try:
                table_item = table_client.create_table()
                print(f"Created table {table_item.name}!")
            except ResourceExistsError:
                print("Table already exists")
        # [END create_table_from_table_client]

    def delete_from_table_client(self):
        from azure.data.tables import TableClient

        # [START delete_table_from_table_client]
        with TableClient.from_connection_string(
            conn_str=self.connection_string, table_name=self.table_name
        ) as table_client:
            table_client.delete_table()
            print(f"Deleted table {table_client.table_name}!")
        # [END delete_table_from_table_client]


if __name__ == "__main__":
    sample = CreateDeleteTable()
    sample.create_table()
    sample.create_if_not_exists()
    sample.delete_table()
