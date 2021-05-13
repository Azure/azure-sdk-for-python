# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_insert_delete_entities_async.py

DESCRIPTION:
    These samples demonstrate the following: inserting entities into a table
    and deleting tables from a table.

USAGE:
    python sample_insert_delete_entities_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

import os
import asyncio
from dotenv import find_dotenv, load_dotenv


class InsertDeleteEntity(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        endpoint = "{}.table.{}".format(account_name, endpoint_suffix)
        connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            account_name, access_key, endpoint_suffix
        )
        table_name = "InsertDeleteAsync"

        entity = {"PartitionKey": "color", "RowKey": "brand", "text": "Marker", "color": "Purple", "price": "5"}

    async def create_entity(self):
        from azure.data.tables.aio import TableClient
        from azure.core.exceptions import ResourceExistsError, HttpResponseError

        table_client = TableClient.from_connection_string(connection_string, table_name)
        # Create a table in case it does not already exist
        # [START create_entity]
        async with table_client:
            try:
                await table_client.create_table()
            except HttpResponseError:
                print("Table already exists")

            try:
                resp = await table_client.create_entity(entity=entity)
                print(resp)
            except ResourceExistsError:
                print("Entity already exists")
        # [END create_entity]

    async def delete_entity(self):
        from azure.data.tables.aio import TableClient
        from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
        from azure.core.credentials import AzureNamedKeyCredential

        credential = AzureNamedKeyCredential(account_name, access_key)
        table_client = TableClient(endpoint=endpoint, credential=credential, table_name=table_name)

        # [START delete_entity]
        async with table_client:
            try:
                resp = await table_client.create_entity(entity=entity)
            except ResourceExistsError:
                print("Entity already exists!")

            await table_client.delete_entity(row_key=entity["RowKey"], partition_key=entity["PartitionKey"])
            print("Successfully deleted!")
        # [END delete_entity]

    async def clean_up(self):
        from azure.data.tables.aio import TableServiceClient

        tsc = TableServiceClient.from_connection_string(connection_string)
        async with tsc:
            async for table in tsc.list_tables():
                await tsc.delete_table(table.name)

            print("Cleaned up")


async def main():
    ide = InsertDeleteEntity()
    await ide.create_entity()
    await ide.delete_entity()
    await ide.clean_up()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
