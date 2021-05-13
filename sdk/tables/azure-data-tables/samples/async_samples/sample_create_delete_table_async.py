# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_create_delete_table_async.py

DESCRIPTION:
    These samples demonstrate creating and deleting individual tables from the
    TableServiceClient and TableClient

USAGE:
    python sample_create_client_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
    2) AZURE_STORAGE_ENDPOINT_SUFFIX - the Table service account URL
    3) AZURE_STORAGE_ACCOUNT_NAME - the name of the storage account
    4) AZURE_STORAGE_ACCESS_KEY - the storage account access key
"""

import asyncio
from dotenv import find_dotenv, load_dotenv


class CreateDeleteTable(object):
    def __init__(self):
        load_dotenv(find_dotenv())

    async def create_table(self):
        # [START create_table]
        import os

        from azure.data.tables.aio import TableServiceClient
        from azure.core.exceptions import ResourceExistsError

        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            account_name, access_key, endpoint_suffix
        )
        table_name = "CreateDeleteTable"

        async with TableServiceClient.from_connection_string(connection_string) as table_service_client:
            try:
                table_item = await table_service_client.create_table(table_name=table_name)
                print("Created table {}!".format(table_item.table_name))
            except ResourceExistsError:
                print("Table already exists")
        # [END create_table]

    async def create_if_not_exists(self):
        # [START create_if_not_exists]
        import os

        from azure.data.tables.aio import TableServiceClient

        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            account_name, access_key, endpoint_suffix
        )
        table_name = "CreateDeleteTable"

        async with TableServiceClient.from_connection_string(connection_string) as table_service_client:
            table_item = await table_service_client.create_table_if_not_exists(table_name=table_name)
            print("Table name: {}".format(table_item.table_name))
        # [END create_if_not_exists]

    async def delete_table(self):
        # [START delete_table]
        import os

        from azure.data.tables.aio import TableServiceClient

        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            account_name, access_key, endpoint_suffix
        )
        table_name = "CreateDeleteTable"

        async with TableServiceClient.from_connection_string(connection_string) as table_service_client:
            await table_service_client.delete_table(table_name=table_name)
            print("Deleted table {}!".format(table_name))
        # [END delete_table]

    async def create_from_table_client(self):
        # [START create_from_table_client]
        import os

        from azure.data.tables.aio import TableClient
        from azure.core.exceptions import ResourceExistsError

        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            account_name, access_key, endpoint_suffix
        )
        table_name = "CreateDeleteTable"

        async with TableClient.from_connection_string(
            conn_str=connection_string, table_name=table_name
        ) as table_client:
            try:
                table_item = await table_client.create_table()
                print("Created table {}!".format(table_item.table_name))
            except ResourceExistsError:
                print("Table already exists")
        # [END create_from_table_client]

    async def delete_from_table_client(self):
        # [START delete_from_table_client]
        import os

        from azure.data.tables.aio import TableClient

        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            account_name, access_key, endpoint_suffix
        )
        table_name = "CreateDeleteTable"

        async with TableClient.from_connection_string(
            conn_str=connection_string, table_name=table_name
        ) as table_client:
            await table_client.delete_table()
            print("Deleted table {}!".format(table_name))
        # [END delete_from_table_client]


async def main():
    sample = CreateDeleteTable()
    await sample.create_table()
    await sample.create_if_not_exists()
    await sample.delete_table()
    await sample.delete_from_table_client()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
