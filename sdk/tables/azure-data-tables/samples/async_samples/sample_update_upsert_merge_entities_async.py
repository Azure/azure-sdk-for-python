# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_update_upsert_merge_entities_async.py

DESCRIPTION:
    These samples demonstrate the following: updating, upserting, and merging entities.

USAGE:
    python sample_update_upsert_merge_entities_async.py

    Set the environment variables with your own values before running the sample:
    1) TABLES_STORAGE_ENDPOINT_SUFFIX - the Table service account URL suffix
    2) TABLES_STORAGE_ACCOUNT_NAME - the name of the storage account
    3) TABLES_PRIMARY_STORAGE_ACCOUNT_KEY - the storage account access key
"""
import sys
from datetime import datetime
import os
from uuid import uuid4, UUID
import asyncio
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


class TableEntitySamples(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.environ["TABLES_PRIMARY_STORAGE_ACCOUNT_KEY"]
        self.endpoint_suffix = os.environ["TABLES_STORAGE_ENDPOINT_SUFFIX"]
        self.account_name = os.environ["TABLES_STORAGE_ACCOUNT_NAME"]
        self.connection_string = f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.access_key};EndpointSuffix={self.endpoint_suffix}"
        self.table_base = "UpdateUpsertMergeAsync"

    async def create_and_get_entities(self):
        # Instantiate a table service client
        from azure.data.tables.aio import TableClient

        table = TableClient.from_connection_string(self.connection_string, table_name=self.table_base + "create")

        async with table:
            await table.create_table()

            my_entity: EntityType = {
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

            try:
                created_entity = await table.create_entity(entity=my_entity)
                print("Created entity: {}".format(created_entity))

                # [START get_entity]
                # Get Entity by partition and row key
                got_entity = await table.get_entity(
                    partition_key=my_entity["PartitionKey"], row_key=my_entity["RowKey"]
                )
                print(f"Received entity: {got_entity}")
                # [END get_entity]

            finally:
                await table.delete_table()

    async def list_all_entities(self):
        # Instantiate a table service client
        from azure.data.tables.aio import TableClient

        table = TableClient.from_connection_string(self.connection_string, table_name=self.table_base + "list")

        # Create the table
        async with table:
            await table.create_table()

            entity = {
                "PartitionKey": "color2",
                "RowKey": "sharpie",
                "text": "Marker",
                "color": "Purple",
                "price": 5.99,
                "inventory": 42,
                "product_id": uuid4(),
            }
            entity1 = {
                "PartitionKey": "color2",
                "RowKey": "crayola",
                "text": "Marker",
                "color": "Red",
                "price": 3.99,
                "inventory": 42,
                "product_id": uuid4(),
            }

            try:
                # Create entities
                await table.create_entity(entity=entity)
                await table.create_entity(entity=entity1)
                # [START list_entities]
                # Query the entities in the table
                i = 0
                async for entity in table.list_entities():
                    print(f"Entity #{entity}: {i}")
                    i += 1
                # [END list_entities]

            finally:
                await table.delete_table()

    async def update_entities(self):
        # Instantiate a table service client
        from azure.data.tables.aio import TableClient
        from azure.data.tables import UpdateMode

        table = TableClient.from_connection_string(self.connection_string, table_name=self.table_base + "update")

        # Create the table and Table Client
        async with table:
            await table.create_table()

            entity = {
                "PartitionKey": "color2",
                "RowKey": "sharpie",
                "text": "Marker",
                "color": "Purple",
                "price": 5.99,
                "inventory": 42,
                "product_id": uuid4(),
            }
            entity1 = {
                "PartitionKey": "color2",
                "RowKey": "crayola",
                "text": "Marker",
                "color": "Red",
                "price": 3.99,
                "inventory": 42,
                "product_id": uuid4(),
            }

            try:
                # Create entities
                await table.create_entity(entity=entity)
                created = await table.get_entity(
                    partition_key=str(entity["PartitionKey"]), row_key=str(entity["RowKey"])
                )

                # [START upsert_entity]
                # Try Replace and insert on fail
                insert_entity = await table.upsert_entity(mode=UpdateMode.REPLACE, entity=entity1)
                print(f"Inserted entity: {insert_entity}")

                created["text"] = "NewMarker"
                merged_entity = await table.upsert_entity(mode=UpdateMode.MERGE, entity=entity)
                print(f"Merged entity: {merged_entity}")
                # [END upsert_entity]

                # [START update_entity]
                # Update the entity
                created["text"] = "NewMarker"
                await table.update_entity(mode=UpdateMode.REPLACE, entity=created)

                # Get the replaced entity
                replaced = await table.get_entity(partition_key=created["PartitionKey"], row_key=created["RowKey"])
                print(f"Replaced entity: {replaced}")

                # Merge the entity
                replaced["color"] = "Blue"
                await table.update_entity(mode=UpdateMode.MERGE, entity=replaced)

                # Get the merged entity
                merged = await table.get_entity(partition_key=replaced["PartitionKey"], row_key=replaced["RowKey"])
                print(f"Merged entity: {merged}")
                # [END update_entity]

            finally:
                await table.delete_table()


async def main():
    sample = TableEntitySamples()
    await sample.create_and_get_entities()
    await sample.list_all_entities()
    await sample.update_entities()


if __name__ == "__main__":
    asyncio.run(main())
