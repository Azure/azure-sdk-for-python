# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_entity_etag_and_timestamp_async.py

DESCRIPTION:
    These samples demonstrate how to get etag and timestamp of an entity.

USAGE:
    python sample_get_entity_etag_and_timestamp_async.py

    Set the environment variables with your own values before running the sample:
    1) TABLES_STORAGE_ENDPOINT_SUFFIX - the Table service account URL suffix
    2) TABLES_STORAGE_ACCOUNT_NAME - the name of the storage account
    3) TABLES_PRIMARY_STORAGE_ACCOUNT_KEY - the storage account access key
"""
import os
import asyncio
from datetime import datetime
from uuid import uuid4, UUID
from dotenv import find_dotenv, load_dotenv
from azure.data.tables.aio import TableClient
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


class SampleGetEntityMetadata(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        self.endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        self.account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        self.endpoint = "{}.table.{}".format(self.account_name, self.endpoint_suffix)
        self.connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            self.account_name, self.access_key, self.endpoint_suffix
        )
        self.table_name = "SampleGetEntityMetadataAsync"
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

    async def get_entity_metadata(self):
        async with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            # Prepare a table and add an entity into it
            await table_client.create_table()
            await table_client.create_entity(entity=self.entity)

            entity = await table_client.get_entity(self.entity["PartitionKey"], self.entity["RowKey"])
            print("Entity metadata:")
            print(f"etag: {entity.metadata['etag']}")
            print(f"timestamp: {entity.metadata['timestamp']}")

            # Cleanup
            await table_client.delete_table()


async def main():
    sample = SampleGetEntityMetadata()
    await sample.get_entity_metadata()


if __name__ == "__main__":
    asyncio.run(main())
