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
    1) TABLES_STORAGE_ENDPOINT_SUFFIX - the Table service account URL suffix
    2) TABLES_STORAGE_ACCOUNT_NAME - the name of the storage account
    3) TABLES_PRIMARY_STORAGE_ACCOUNT_KEY - the storage account access key
"""

import os
from time import sleep
import asyncio
from dotenv import find_dotenv, load_dotenv


class CreateDeleteTable(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        self.endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        self.account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        self.endpoint = "{}.table.{}".format(self.account_name, self.endpoint_suffix)
        self.connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            self.account_name, self.access_key, self.endpoint_suffix
        )
        self.table_name = "CreateDeleteTable"

    async def create_table(self):
        from azure.data.tables.aio import TableServiceClient
        from azure.core.exceptions import ResourceExistsError

        # [START create_table]
        async with TableServiceClient.from_connection_string(self.connection_string) as table_service_client:
            try:
                table_item = await table_service_client.create_table(table_name=self.table_name)
                print("Created table {}!".format(table_item.table_name))
            except ResourceExistsError:
                print("Table already exists")
        # [END create_table]

    async def create_if_not_exists(self):
        from azure.data.tables.aio import TableServiceClient

        # [START create_if_not_exists]
        async with TableServiceClient.from_connection_string(self.connection_string) as table_service_client:
            table_item = await table_service_client.create_table_if_not_exists(table_name=self.table_name)
            print("Table name: {}".format(table_item.table_name))
        # [END create_if_not_exists]

    async def delete_table(self):
        from azure.data.tables.aio import TableServiceClient
        from azure.core.exceptions import HttpResponseError

        # [START delete_table]
        async with TableServiceClient.from_connection_string(self.connection_string) as table_service_client:
            await table_service_client.delete_table(table_name=self.table_name)
            print("Deleted table {}!".format(self.table_name))
        # [END delete_table]

    async def create_from_table_client(self):
        from azure.data.tables.aio import TableClient

        # [START create_from_table_client]
        async with TableClient.from_connection_string(
            conn_str=self.connection_string, table_name=self.table_name
        ) as table_client:
            try:
                table_item = await table_client.create_table()
                print("Created table {}!".format(table_item.table_name))
            except ResourceExistsError:
                print("Table already exists")
        # [END create_from_table_client]

    async def delete_from_table_client(self):
        from azure.data.tables.aio import TableClient
        from azure.core.exceptions import HttpResponseError

        # [START delete_from_table_client]
        async with TableClient.from_connection_string(
            conn_str=self.connection_string, table_name=self.table_name
        ) as table_client:
            await table_client.delete_table()
            print("Deleted table {}!".format(self.table_name))
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
