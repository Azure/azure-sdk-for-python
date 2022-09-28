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
from uuid import uuid4, UUID
import copy
import os
import json
import asyncio
from azure.storage.blob.aio import BlobServiceClient
from azure.data.tables.aio import TableServiceClient
from dotenv import find_dotenv, load_dotenv


class CopyTableSamples(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        self.endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        self.account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        self.table_connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            self.account_name, self.access_key, self.endpoint_suffix
        )
        self.table_name="mytable"
        self.table_service_client = TableServiceClient.from_connection_string(conn_str=self.table_connection_string, table_name=self.table_name)
        self.blob_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.blob_service_client = BlobServiceClient.from_connection_string(self.blob_connection_string)
        self.container_name = self.table_name
        self.entity = {
            "PartitionKey": "color",
            "text": "Marker",
            "color": "Purple",
            "price": 4.99,
            "last_updated": datetime.today(),
            "product_id": uuid4(),
            "inventory_count": 42,
            "barcode": b"135aefg8oj0ld58"
        }

    async def copy_table_from_table_to_blob(self):
        await self._setup_table()
        try:
            self.container_client = await self.blob_service_client.create_container(self.container_name)           
            # Upload in-memory table data to a blob that stays in a container
            async for entity in self.table_client.list_entities():
                # Convert type datetime, bytes, UUID values to string as they're not JSON serializable
                entity["last_updated"] = entity["last_updated"].isoformat()
                entity["product_id"] = entity["product_id"].hex
                entity["barcode"] = entity["barcode"].decode("utf-8")
                blob_name = entity["PartitionKey"] + entity["RowKey"]
                blob_client = self.blob_service_client.get_blob_client(self.container_name, blob_name)
                await blob_client.upload_blob(json.dumps(entity))
        finally:
            await self._tear_down()

    async def copy_table_from_blob_to_table(self):
        await self._setup_blob()
        try:
            # Download entities from blob to memory
            # Note: when entities size is too big, may need to do copy by chunk
            blob_list = self.container_client.list_blobs()
            # Upload entities to a table
            self.table_client = await self.table_service_client.get_table_client(self.table_name)
            await self.table_client.create_table()
            async for blob in blob_list:
                blob_client = self.container_client.get_blob_client(blob)
                blob_content = await blob_client.download_blob().readall()
                entities = json.loads(blob_content)
                async for entity in entities:
                    # Convert values back to their original types
                    entity["last_updated"] = datetime.fromisoformat(entity["last_updated"])
                    entity["product_id"] = UUID(entity["product_id"])
                    entity["barcode"] = entity["barcode"].encode("utf-8")
                    await self.table_client.upsert_entity(entity)
        finally:
            await self._tear_down()

    async def _setup_table(self):
        self.table_client = await self.table_service_client.get_table_client(self.table_name)
        await self.table_client.create_table()
        for i in range(10):
            self.entity["RowKey"] = str(i)
            await self.table_client.create_entity(self.entity)

    async def _setup_blob(self):
        self.container_client = await self.blob_service_client.create_container(self.container_name)
        entity = copy.deepcopy(self.entity)
        # Convert type datetime, bytes, UUID values to string as they're not JSON serializable
        entity["last_updated"] = entity["last_updated"].isoformat()
        entity["product_id"] = entity["product_id"].hex
        entity["barcode"] = entity["barcode"].decode("utf-8")
        for i in range(10):
            self.entity["RowKey"] = str(i)
            blob_name = entity["PartitionKey"] + entity["RowKey"]
            blob_client = self.blob_service_client.get_blob_client(self.container_name, blob_name)
            await blob_client.upload_blob(json.dumps(entity))

    async def _tear_down(self):
        await self.table_client.delete_table()
        await self.container_client.delete_container()


async def main():
    sample = CopyTableSamples()
    await sample.copy_table_from_table_to_blob()
    await sample.copy_table_from_blob_to_table()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
