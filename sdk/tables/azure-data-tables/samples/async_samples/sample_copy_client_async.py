# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_copy_table_async.py

DESCRIPTION:
    These samples demonstrate how to copy tables between table and blob storage.

USAGE:
    python sample_copy_table_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
    2) TABLES_STORAGE_ENDPOINT_SUFFIX - the Table service account URL suffix
    3) TABLES_STORAGE_ACCOUNT_NAME - the name of the storage account
    4) TABLES_PRIMARY_STORAGE_ACCOUNT_KEY - the storage account access key
"""


from datetime import datetime
import os
import json
import asyncio
from azure.storage.blob.aio import BlobClient, BlobServiceClient
from azure.data.tables.aio import TableClient
from dotenv import find_dotenv, load_dotenv


class CopyTableSamples(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        self.endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        self.account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        self.endpoint = "{}.table.{}".format(self.account_name, self.endpoint_suffix)
        self.table_connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            self.account_name, self.access_key, self.endpoint_suffix
        )
        self.blob_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.entity = {
            "PartitionKey": "color",
            "RowKey": "brand",
            "text": "Marker",
            "color": "Purple",
            "price": 4.99,
            "last_updated": datetime.today(),
            "product_id": uuid4(),
            "inventory_count": 42,
            "barcode": b"135aefg8oj0ld58"
        }
        self.table = TableClient.from_connection_string(conn_str=self.table_connection_string, table_name="mytable")
        blob_service = BlobServiceClient.from_connection_string(self.blob_connection_string)
        self.container = blob_service.get_container_client("mycontainer")
        self.blob = BlobClient.from_connection_string(conn_str=self.blob_connection_string, container_name="mycontainer", blob_name="myblob")


    async def copy_table_from_table_to_blob(self):
        try:
            # Upload entities to a table
            await self.table.create_table()
            await self.table.create_entity(self.entity)
            # Download entities from table to memory
            entities = self.table.list_entities()

            self.container.create_container()
            # Upload in-memory table data to a blob that stays in a container
            async for e in entities:
                await self.blob.upload_blob(json.dumps(e))
        finally:
            await self._tear_down()

    async def copy_table_from_blob_to_table(self):
        try:
            self.container.create_container()
            # Upload entities to a blob that stays in a container
            await self.blob.upload_blob(json.dumps(self.entity))
            # Download entities from blob to memory
            # Note: when entities size is too big, may need to do copy by chunk
            download_stream = await self.blob.download_blob()
            entities = json.load(download_stream.readall())
            # Upload entities to a table
            await self.table.create_table()
            async for e in entities:
                await self.table.upsert_entity(e)
        finally:
            await self._tear_down()
    
    async def _tear_down(self):
        await self.table.delete_table()
        await self.blob.delete_blob()
        await self.container.delete_container()


async def main():
    sample = CopyTableSamples()
    await sample.copy_table_from_table_to_blob()
    await sample.copy_table_from_blob_to_table()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
