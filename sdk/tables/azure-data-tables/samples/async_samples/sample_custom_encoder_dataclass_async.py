# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_custom_encoder_dataclass_async.py

DESCRIPTION:
    These samples demonstrate the following: inserting entities into a table
    and deleting entities from a table.

USAGE:
    python sample_custom_encoder_dataclass_async.py

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
from typing import Dict, Union, Optional
from azure.data.tables import TableEntityEncoderABC, UpdateMode
from azure.data.tables.aio import TableClient


@dataclass
class Car:
    partition_key: str
    row_key: UUID
    price: Optional[float] = None
    last_updated: Optional[datetime] = None
    product_id: Optional[UUID] = None
    inventory_count: Optional[int] = None
    barcode: Optional[bytes] = None
    color: Optional[str] = None
    maker: Optional[str] = None
    model: Optional[str] = None
    production_date: Optional[datetime] = None
    mileage: Optional[int] = None
    is_second_hand: Optional[bool] = None


class MyEncoder(TableEntityEncoderABC[Car]):
    def prepare_key(self, key: UUID) -> str:  # type: ignore[override]
        return super().prepare_key(str(key))

    def encode_entity(self, entity: Car) -> Dict[str, Union[str, int, float, bool]]:
        encoded = {}
        for key, value in asdict(entity).items():
            if key == "partition_key":
                encoded["PartitionKey"] = value  # this property should be "PartitionKey" in encoded result
                continue
            if key == "row_key":
                encoded["RowKey"] = str(value)  # this property should be "RowKey" in encoded result
                continue
            edm_type, value = self.prepare_value(key, value)
            if edm_type:
                encoded[f"{key}@odata.type"] = edm_type.value if hasattr(edm_type, "value") else edm_type
            encoded[key] = value
        return encoded


class InsertUpdateDeleteEntity(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.environ["TABLES_PRIMARY_STORAGE_ACCOUNT_KEY"]
        self.endpoint_suffix = os.environ["TABLES_STORAGE_ENDPOINT_SUFFIX"]
        self.account_name = os.environ["TABLES_STORAGE_ACCOUNT_NAME"]
        self.endpoint = f"{self.account_name}.table.{self.endpoint_suffix}"
        self.connection_string = f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.access_key};EndpointSuffix={self.endpoint_suffix}"
        self.table_name = "CustomEncoderDataClassAsync"

        self.entity = Car(
            partition_key="PK",
            row_key=uuid4(),
            price=4.99,
            last_updated=datetime.today(),
            product_id=uuid4(),
            inventory_count=42,
            barcode=b"135aefg8oj0ld58",  # cspell:disable-line
            color="white",
            maker="maker",
            model="model",
            production_date=datetime(year=2014, month=4, day=1, hour=9, minute=30, second=45, tzinfo=timezone.utc),
            mileage=2**31,  # an int64 integer
            is_second_hand=True,
        )

    async def create_delete_entity(self):
        table_client = TableClient.from_connection_string(self.connection_string, self.table_name)
        async with table_client:
            await table_client.create_table()

            result = await table_client.create_entity(entity=self.entity, encoder=MyEncoder())
            print(f"Created entity: {result}")

            result = await table_client.get_entity(
                self.entity.partition_key,
                self.entity.row_key,  # type: ignore[arg-type] # intend to pass a non-string RowKey
                encoder=MyEncoder(),
            )
            print(f"Get entity result: {result}")

            await table_client.delete_entity(
                partition_key=self.entity.partition_key,
                row_key=self.entity.row_key,  # type: ignore[call-overload] # intend to pass a non-string RowKey
                encoder=MyEncoder(),
            )
            print("Successfully deleted!")

            await table_client.delete_table()
            print("Cleaned up")

    async def upsert_update_entities(self):
        table_client = TableClient.from_connection_string(
            self.connection_string, table_name=f"{self.table_name}UpsertUpdate"
        )

        async with table_client:
            await table_client.create_table()

            entity1 = Car(
                partition_key="PK",
                row_key=uuid4(),
                price=4.99,
                last_updated=datetime.today(),
                product_id=uuid4(),
                inventory_count=42,
                barcode=b"135aefg8oj0ld58",  # cspell:disable-line
            )
            entity2 = Car(
                partition_key=entity1.partition_key,
                row_key=entity1.row_key,
                color="red",
                maker="maker2",
                model="model2",
                production_date=datetime(year=2014, month=4, day=1, hour=9, minute=30, second=45, tzinfo=timezone.utc),
                mileage=2**31,  # an int64 integer
                is_second_hand=True,
            )

            await table_client.upsert_entity(mode=UpdateMode.REPLACE, entity=entity2, encoder=MyEncoder())
            inserted_entity = await table_client.get_entity(
                entity2.partition_key,
                entity2.row_key,  # type: ignore[arg-type] # intend to pass a non-string RowKey
                encoder=MyEncoder(),
            )
            print(f"Inserted entity: {inserted_entity}")

            await table_client.upsert_entity(mode=UpdateMode.MERGE, entity=entity1, encoder=MyEncoder())
            merged_entity = await table_client.get_entity(
                entity1.partition_key,
                entity1.row_key,  # type: ignore[arg-type] # intend to pass a non-string RowKey
                encoder=MyEncoder(),
            )
            print(f"Merged entity: {merged_entity}")

            entity3 = Car(
                partition_key=entity1.partition_key,
                row_key=entity2.row_key,
                color="white",
            )
            await table_client.update_entity(mode=UpdateMode.REPLACE, entity=entity3, encoder=MyEncoder())
            replaced_entity = await table_client.get_entity(
                entity3.partition_key,
                entity3.row_key,  # type: ignore[arg-type] # intend to pass a non-string RowKey
                encoder=MyEncoder(),
            )
            print(f"Replaced entity: {replaced_entity}")

            await table_client.update_entity(mode=UpdateMode.REPLACE, entity=entity2, encoder=MyEncoder())
            merged_entity = await table_client.get_entity(
                entity2.partition_key,
                entity2.row_key,  # type: ignore[arg-type] # intend to pass a non-string RowKey
                encoder=MyEncoder(),
            )
            print(f"Merged entity: {merged_entity}")

            await table_client.delete_table()
            print("Cleaned up")


async def main():
    ide = InsertUpdateDeleteEntity()
    await ide.create_delete_entity()
    await ide.upsert_update_entities()


if __name__ == "__main__":
    asyncio.run(main())
