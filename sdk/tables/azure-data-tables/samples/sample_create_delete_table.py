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

from dotenv import find_dotenv, load_dotenv


class CreateDeleteTable(object):
    def __init__(self):
        load_dotenv(find_dotenv())

    def create_table(self):
        # [START create_table_from_tc]
        import os

        from azure.data.tables import TableServiceClient
        from azure.core.exceptions import ResourceExistsError

        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            account_name, access_key, endpoint_suffix
        )

        with TableServiceClient.from_connection_string(connection_string) as table_service_client:
            try:
                table_client = table_service_client.create_table(table_name="myTable")
                print("Created table {}!".format(table_client.table_name))
            except ResourceExistsError:
                print("Table already exists")
        # [END create_table_from_tc]

    def create_if_not_exists(self):
        # [START create_table_if_not_exists]
        import os
        from azure.data.tables import TableServiceClient

        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            account_name, access_key, endpoint_suffix
        )

        with TableServiceClient.from_connection_string(connection_string) as table_service_client:
            table_client = TableServiceClient.create_table_if_not_exists(table_name="myTable")
            print("Table name: {}".format(table_client.table_name))
        # [END create_table_if_not_exists]

    def delete_table(self):
        # [START delete_table_from_tc]
        import os
        from azure.data.tables import TableServiceClient

        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        endpoint = "{}.table.{}".format(account_name, endpoint_suffix)
        connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            account_name, access_key, endpoint_suffix
        )

        with TableServiceClient.from_connection_string(connection_string) as table_service_client:
            table_service_client.delete_table(table_name="myTable")
            print("Deleted table {}!".format("myTable"))
        # [END delete_table_from_tc]

    def create_from_table_client(self):
        # [START create_table_from_table_client]
        import os

        from azure.data.tables import TableClient
        from azure.core.exceptions import ResourceExistsError

        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            account_name, access_key, endpoint_suffix
        )

        with TableClient.from_connection_string(conn_str=connection_string, table_name="myTable") as table_client:
            try:
                table_client.create_table()
                print("Created table {}!".format(table_client.table_name))
            except ResourceExistsError:
                print("Table already exists")
        # [END create_table_from_table_client]

    def delete_from_table_client(self):
        # [START delete_table_from_table_client]
        import os

        from azure.data.tables import TableClient

        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        endpoint = "{}.table.{}".format(account_name, endpoint_suffix)
        connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            account_name, access_key, endpoint_suffix
        )

        with TableClient.from_connection_string(conn_str=connection_string, table_name="myTable") as table_client:
            table_client.delete_table()
            print("Deleted table {}!".format(table_client.table_name))
        # [END delete_table_from_table_client]


if __name__ == "__main__":
    sample = CreateDeleteTable()
    sample.create_if_not_exists()
    sample.create_table()
    sample.delete_table()
    sample.delete_from_table_client
