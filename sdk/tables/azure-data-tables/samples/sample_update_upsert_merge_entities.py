# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_update_upsert_merge_entities.py

DESCRIPTION:
    These samples demonstrate the following: updating, upserting, and merging entities.

USAGE:
    python sample_update_upsert_merge_entities.py

    Set the environment variables with your own values before running the sample:
    1) TABLES_STORAGE_ENDPOINT_SUFFIX - the Table service account URL suffix
    2) TABLES_STORAGE_ACCOUNT_NAME - the name of the storage account
    3) TABLES_PRIMARY_STORAGE_ACCOUNT_KEY - the storage account access key
"""
import sys
from datetime import datetime
from dotenv import find_dotenv, load_dotenv
import os
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


class TableEntitySamples(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.environ["TABLES_PRIMARY_STORAGE_ACCOUNT_KEY"]
        self.endpoint_suffix = os.environ["TABLES_STORAGE_ENDPOINT_SUFFIX"]
        self.account_name = os.environ["TABLES_STORAGE_ACCOUNT_NAME"]
        self.connection_string = f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.access_key};EndpointSuffix={self.endpoint_suffix}"
        self.table_base = "SampleUpdateUpsertMerge"

    def create_and_get_entities(self):
        # Instantiate a table client
        from azure.data.tables import TableClient

        with TableClient.from_connection_string(self.connection_string, table_name=self.table_base + "create") as table:

            # Create the Table
            table.create_table()

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
                # [START create_entity]
                created_entity = table.create_entity(entity=my_entity)
                print(f"Created entity: {created_entity}")
                # [END create_entity]

                # [START get_entity]
                # Get Entity by partition and row key
                got_entity = table.get_entity(partition_key=my_entity["PartitionKey"], row_key=my_entity["RowKey"])
                print(f"Received entity: {got_entity}")
                # [END get_entity]

            finally:
                # Delete the table
                table.delete_table()

    def list_all_entities(self):
        # Instantiate a table client
        from azure.data.tables import TableClient

        with TableClient.from_connection_string(self.connection_string, table_name=self.table_base + "list") as table:

            # Create the table
            table.create_table()

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
                table.create_entity(entity=entity)
                table.create_entity(entity=entity1)
                # [START list_entities]
                # Query the entities in the table
                entities = list(table.list_entities())
                for i, entity in enumerate(entities):
                    print(f"Entity #{entity}: {i}")
                # [END list_entities]

            finally:
                # Delete the table
                table.delete_table()

    def update_entities(self):
        # Instantiate a table client
        from azure.data.tables import TableClient
        from azure.data.tables import UpdateMode

        with TableClient.from_connection_string(self.connection_string, table_name=self.table_base + "update") as table:

            # Create the table and Table Client
            table.create_table()

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
                table.create_entity(entity=entity)
                created = table.get_entity(partition_key=str(entity["PartitionKey"]), row_key=str(entity["RowKey"]))

                # [START upsert_entity]
                # Try Replace and insert on fail
                insert_entity = table.upsert_entity(mode=UpdateMode.REPLACE, entity=entity1)
                print(f"Inserted entity: {insert_entity}")

                created["text"] = "NewMarker"
                merged_entity = table.upsert_entity(mode=UpdateMode.MERGE, entity=entity)
                print(f"Merged entity: {merged_entity}")
                # [END upsert_entity]

                # [START update_entity]
                # Update the entity
                created["text"] = "NewMarker"
                table.update_entity(mode=UpdateMode.REPLACE, entity=created)

                # Get the replaced entity
                replaced = table.get_entity(partition_key=str(created["PartitionKey"]), row_key=str(created["RowKey"]))
                print(f"Replaced entity: {replaced}")

                # Merge the entity
                replaced["color"] = "Blue"
                table.update_entity(mode=UpdateMode.MERGE, entity=replaced)

                # Get the merged entity
                merged = table.get_entity(partition_key=str(replaced["PartitionKey"]), row_key=str(replaced["RowKey"]))
                print(f"Merged entity: {merged}")
                # [END update_entity]

            finally:
                # Delete the table
                table.delete_table()


if __name__ == "__main__":
    sample = TableEntitySamples()
    sample.create_and_get_entities()
    sample.list_all_entities()
    sample.update_entities()
