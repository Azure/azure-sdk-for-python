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
    1) TABLES_STORAGE_ENDPOINT_SUFFIX - the Table storage service account URL suffix
    2) TABLES_STORAGE_ACCOUNT_NAME - the Tables storage account name
    3) TABLES_PRIMARY_STORAGE_ACCOUNT_KEY - the Tables storage account access key
"""
import asyncio
import json
import os
from azure.storage.blob.aio import BlobServiceClient
from azure.data.tables.aio import TableServiceClient
from datetime import datetime
from dotenv import find_dotenv, load_dotenv
from uuid import uuid4, UUID
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


class EntityTypeJSONSerializable(TypedDict, total=False):
    PartitionKey: str
    RowKey: str
    text: str
    color: str
    price: float
    last_updated: str
    product_id: str
    inventory_count: int
    barcode: str


class CopyTableSamples(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        self.endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        self.account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        self.storage_account_connection_string = f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.access_key};EndpointSuffix={self.endpoint_suffix}"
        self.copy_to_blob_table_name = "copytoblobtablename" + uuid4().hex
        self.copy_to_table_table_name = "copytotabletablename" + uuid4().hex
        self.blob_service_client = BlobServiceClient.from_connection_string(self.storage_account_connection_string)
        self.entity: EntityType = {
            "PartitionKey": "color",
            "text": "Marker",
            "color": "Purple",
            "price": 4.99,
            "last_updated": datetime.today(),
            "product_id": uuid4(),
            "inventory_count": 42,
            "barcode": b"135aefg8oj0ld58",  # cspell:disable-line
        }

    async def copy_table_from_table_to_blob(self):
        print("Start to copy table from Tables table to Storage blob.")
        print(f"Table name: {self.copy_to_blob_table_name}")
        await self._setup_table()
        try:
            self.container_client = await self.blob_service_client.create_container(self.copy_to_blob_table_name)
            # Upload in-memory table data to a blob that stays in a container
            async for entity in self.table_client.list_entities():
                # Convert type datetime, bytes, UUID values to string as they're not JSON serializable
                entity["last_updated"] = entity["last_updated"].isoformat()
                entity["product_id"] = entity["product_id"].hex
                entity["barcode"] = entity["barcode"].decode("utf-8")
                blob_name = f"{entity['PartitionKey']}{entity['RowKey']}"
                blob_client = self.blob_service_client.get_blob_client(self.copy_to_blob_table_name, blob_name)
                await blob_client.upload_blob(json.dumps(entity))
            print("Done!")
        finally:
            await self._tear_down()

    async def copy_table_from_blob_to_table(self):
        print("Start to copy table from Storage blob to Tables table.")
        print("Table name: " + self.copy_to_blob_table_name)
        await self._setup_blob()
        try:
            # Download entities from blob to memory
            # Note: when entities size is too big, may need to do copy by chunk
            blob_list = self.container_client.list_blobs()
            # Upload entities to a table
            table_service_client = TableServiceClient.from_connection_string(
                conn_str=self.storage_account_connection_string, table_name=self.copy_to_table_table_name
            )
            self.table_client = table_service_client.get_table_client(self.copy_to_table_table_name)
            await self.table_client.create_table()
            async for blob in blob_list:
                blob_client = self.container_client.get_blob_client(blob)
                blob_stream_downloader = await blob_client.download_blob()
                entity = json.loads(await blob_stream_downloader.readall())
                # Convert values back to their original types
                entity["last_updated"] = datetime.fromisoformat(entity["last_updated"])
                entity["product_id"] = UUID(entity["product_id"])
                entity["barcode"] = entity["barcode"].encode("utf-8")
                await self.table_client.upsert_entity(entity)
            print("Done!")
        finally:
            await self._tear_down()

    async def _setup_table(self):
        table_service_client = TableServiceClient.from_connection_string(
            conn_str=self.storage_account_connection_string, table_name=self.copy_to_blob_table_name
        )
        self.table_client = table_service_client.get_table_client(self.copy_to_blob_table_name)
        await self.table_client.create_table()
        for i in range(10):
            self.entity["RowKey"] = str(i)
            await self.table_client.create_entity(self.entity)

    async def _setup_blob(self):
        self.container_client = await self.blob_service_client.create_container(self.copy_to_table_table_name)
        # Convert type datetime, bytes, UUID values to string as they're not JSON serializable
        entity_serializable: EntityTypeJSONSerializable = {
            "PartitionKey": self.entity["PartitionKey"],
            "text": self.entity["text"],
            "color": self.entity["color"],
            "price": self.entity["price"],
            "last_updated": self.entity["last_updated"].isoformat(),
            "product_id": self.entity["product_id"].hex,
            "inventory_count": 42,
            "barcode": self.entity["barcode"].decode("utf-8"),
        }
        for i in range(10):
            entity_serializable["RowKey"] = str(i)
            blob_name = f"{entity_serializable['PartitionKey']}{entity_serializable['RowKey']}"
            blob_client = self.blob_service_client.get_blob_client(self.copy_to_table_table_name, blob_name)
            await blob_client.upload_blob(json.dumps(entity_serializable))

    async def _tear_down(self):
        await self.table_client.delete_table()
        await self.container_client.delete_container()


async def main():
    sample = CopyTableSamples()
    await sample.copy_table_from_table_to_blob()
    await sample.copy_table_from_blob_to_table()


if __name__ == "__main__":
    asyncio.run(main())
