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
import os
import asyncio
from datetime import datetime, timezone
from uuid import uuid4, UUID
from dotenv import find_dotenv, load_dotenv
from dataclasses import dataclass, asdict
from typing import Dict, Union, NamedTuple
from azure.data.tables import TableEntityEncoderABC, UpdateMode
from azure.data.tables.aio import TableClient


RGBColor = NamedTuple("RGBColor", [("Red", float), ("Green", float), ("Blue", float)])


@dataclass
class Car:
    color: RGBColor
    maker: str
    model: str
    production_date: datetime
    mileage: int


@dataclass
class Product:
    PartitionKey: str
    RowKey: str
    price: float
    last_updated: datetime
    product_id: UUID
    inventory_count: int
    barcode: bytes
    item_details: Car


class MyEncoder(TableEntityEncoderABC[Product]):
    def encode_entity(self, entity: Product) -> Dict[str, Union[str, int, float, bool]]:
        encoded = {}
        for key, value in asdict(entity).items():
            if isinstance(value, dict):
                for k, v in value.items():
                    if isinstance(v, RGBColor):
                        edm_type, v = self._prepare_value_in_rgb(v)
                    else:
                        edm_type, v = self.prepare_value(k, v)
                    if edm_type:
                        encoded[f"{k}@odata.type"] = edm_type.value if hasattr(edm_type, "value") else edm_type
                    encoded[k] = v
                continue
            edm_type, value = self.prepare_value(key, value)
            if edm_type:
                encoded[f"{key}@odata.type"] = edm_type.value if hasattr(edm_type, "value") else edm_type
            encoded[key] = value
        return encoded

    def _prepare_value_in_rgb(self, color):
        return None, f"{color[0]}, {color[1]}, {color[2]}"


class TableEntitySamples(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.environ["TABLES_PRIMARY_STORAGE_ACCOUNT_KEY"]
        self.endpoint_suffix = os.environ["TABLES_STORAGE_ENDPOINT_SUFFIX"]
        self.account_name = os.environ["TABLES_STORAGE_ACCOUNT_NAME"]
        self.connection_string = f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.access_key};EndpointSuffix={self.endpoint_suffix}"
        self.table_base = "UpdateUpsertMergeAsync"

    async def create_and_get_entities(self):
        # Instantiate a table client
        table = TableClient.from_connection_string(self.connection_string, table_name=self.table_base + "create")

        async with table:
            await table.create_table()

            my_entity = {
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
                print(f"Created entity: {created_entity}")

                # [START get_entity]
                # Get Entity by partition and row key
                got_entity = await table.get_entity(
                    partition_key=str(my_entity["PartitionKey"]), row_key=str(my_entity["RowKey"])
                )
                print(f"Received entity: {got_entity}")
                # [END get_entity]

            finally:
                await table.delete_table()

    async def list_all_entities(self):
        # Instantiate a table client
        table = TableClient.from_connection_string(self.connection_string, table_name=self.table_base + "list")

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
                    print(f"Entity #{i}: {entity}")
                    i += 1
                # [END list_entities]

            finally:
                await table.delete_table()

    async def update_entities(self):
        # Instantiate a table client
        table = TableClient.from_connection_string(self.connection_string, table_name=self.table_base + "update")

        async with table:
            await table.create_table()

            entity = Product(
                PartitionKey="PK",
                RowKey="RK",
                price=4.99,
                last_updated=datetime.today(),
                product_id=uuid4(),
                inventory_count=42,
                barcode=b"135aefg8oj0ld58",  # cspell:disable-line
                item_details=Car(
                    color=RGBColor("30.1", "40.1", "50.1"),
                    maker="maker",
                    model="model",
                    production_date=datetime(
                        year=2014, month=4, day=1, hour=9, minute=30, second=45, tzinfo=timezone.utc
                    ),
                    mileage=2**31,  # an int64 integer
                ),
            )
            entity1 = Product(
                PartitionKey="PK2",
                RowKey="RK2",
                price=3.99,
                last_updated=datetime.today(),
                product_id=uuid4(),
                inventory_count=42,
                barcode=b"135aefg8oj0ld59",  # cspell:disable-line
                item_details=Car(
                    color=RGBColor("40.1", "50.1", "60.1"),
                    maker="maker2",
                    model="model2",
                    production_date=datetime(
                        year=2014, month=4, day=1, hour=9, minute=30, second=45, tzinfo=timezone.utc
                    ),
                    mileage=2**31,  # an int64 integer
                ),
            )

            try:
                await table.create_entity(entity=entity, encoder=MyEncoder())
                created = await table.get_entity(partition_key=entity.PartitionKey, row_key=entity.RowKey)

                # [START upsert_entity]
                insert_entity = await table.upsert_entity(mode=UpdateMode.REPLACE, entity=entity1, encoder=MyEncoder())
                print(f"Inserted entity: {insert_entity}")

                merged_entity = await table.upsert_entity(mode=UpdateMode.MERGE, entity=entity, encoder=MyEncoder())
                print(f"Merged entity: {merged_entity}")
                # [END upsert_entity]

                # [START update_entity]
                # Update the entity
                created["maker"] = "NewMaker"
                await table.update_entity(mode=UpdateMode.REPLACE, entity=created)

                # Get the replaced entity
                replaced = await table.get_entity(partition_key=created["PartitionKey"], row_key=created["RowKey"])
                print(f"Replaced entity: {replaced}")

                # Merge the entity
                replaced["color"] = "70.1, 80.1, 90.1"
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
