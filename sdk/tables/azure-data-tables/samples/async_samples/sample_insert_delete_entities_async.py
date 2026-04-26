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
    and deleting entities from a table.

USAGE:
    python sample_insert_delete_entities_async.py

    Set the environment variables with your own values before running the sample:
    1) TABLES_STORAGE_ENDPOINT_SUFFIX - the Table service account URL suffix
    2) TABLES_STORAGE_ACCOUNT_NAME - the name of the storage account
    3) TABLES_PRIMARY_STORAGE_ACCOUNT_KEY - the storage account access key
"""
import sys
import os
import asyncio
from datetime import datetime
from uuid import uuid4, UUID
from dotenv import find_dotenv, load_dotenv
from typing_extensions import TypedDict


class EntityType(TypedDict, total=False):
    PartitionKey: str
    RowKey: str
    text: str
    color: str
    price: float
    last_updated: datetime
    product_id: UUID
    inventory_count: int
    barcode: bytes


class InsertDeleteEntity(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.environ["TABLES_PRIMARY_STORAGE_ACCOUNT_KEY"]
        self.endpoint_suffix = os.environ["TABLES_STORAGE_ENDPOINT_SUFFIX"]
        self.account_name = os.environ["TABLES_STORAGE_ACCOUNT_NAME"]
        self.endpoint = f"{self.account_name}.table.{self.endpoint_suffix}"
        self.connection_string = f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.access_key};EndpointSuffix={self.endpoint_suffix}"
        self.table_name = "InsertDeleteAsync"

        self.entity: EntityType = {
            "PartitionKey": "color",
            "RowKey": "brand",
            "text": "Marker",
            "color": "Purple",
            "price": 4.99,
            "last_updated": datetime.today(),
            "product_id": uuid4(),
            "inventory_count": 42,
            "barcode": b"135aefg8oj0ld58",  # cspell:disable-line
        }

    async def create_entity(self):
        from azure.data.tables.aio import TableClient
        from azure.core.exceptions import ResourceExistsError, HttpResponseError

        table_client = TableClient.from_connection_string(self.connection_string, self.table_name)
        # Create a table in case it does not already exist
        async with table_client:
            try:
                await table_client.create_table()
            except HttpResponseError:
                print("Table already exists")

            # [START create_entity]
            try:
                resp = await table_client.create_entity(entity=self.entity)
                print(resp)
            except ResourceExistsError:
                print("Entity already exists")
            # [END create_entity]

    async def delete_entity(self):
        from azure.data.tables.aio import TableClient
        from azure.core.exceptions import ResourceExistsError
        from azure.core.credentials import AzureNamedKeyCredential

        credential = AzureNamedKeyCredential(self.account_name, self.access_key)
        table_client = TableClient(endpoint=self.endpoint, table_name=self.table_name, credential=credential)

        async with table_client:
            try:
                await table_client.create_entity(entity=self.entity)
            except ResourceExistsError:
                print("Entity already exists!")

            # [START delete_entity]
            await table_client.delete_entity(row_key=self.entity["RowKey"], partition_key=self.entity["PartitionKey"])
            print("Successfully deleted!")
            # [END delete_entity]

    async def clean_up(self):
        from azure.data.tables.aio import TableServiceClient

        async with TableServiceClient.from_connection_string(self.connection_string) as tsc:
            async for table in tsc.list_tables():
                await tsc.delete_table(table.name)

            print("Cleaned up")


async def main():
    ide = InsertDeleteEntity()
    await ide.create_entity()
    await ide.delete_entity()
    await ide.clean_up()


if __name__ == "__main__":
    asyncio.run(main())
