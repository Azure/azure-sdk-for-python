# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_insert_delete_entities.py

DESCRIPTION:
    These samples demonstrate the following: inserting entities into a table
    and deleting tables from a table.

USAGE:
    python sample_insert_delete_entities.py

    Set the environment variables with your own values before running the sample:
    1) TABLES_STORAGE_ENDPOINT_SUFFIX - the Table service account URL suffix
    2) TABLES_STORAGE_ACCOUNT_NAME - the name of the storage account
    3) TABLES_PRIMARY_STORAGE_ACCOUNT_KEY - the storage account access key
"""
import os
from datetime import datetime, timezone
from uuid import uuid4, UUID
from dotenv import find_dotenv, load_dotenv
from dataclasses import dataclass, asdict
from typing import Dict, Union, NamedTuple
from azure.data.tables import TableClient, TableEntityEncoderABC
from azure.core.exceptions import ResourceExistsError, HttpResponseError


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


class InsertDeleteEntity(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.environ["TABLES_PRIMARY_STORAGE_ACCOUNT_KEY"]
        self.endpoint_suffix = os.environ["TABLES_STORAGE_ENDPOINT_SUFFIX"]
        self.account_name = os.environ["TABLES_STORAGE_ACCOUNT_NAME"]
        self.endpoint = f"{self.account_name}.table.{self.endpoint_suffix}"
        self.connection_string = f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.access_key};EndpointSuffix={self.endpoint_suffix}"
        self.table_name = "SampleInsertDelete"

        self.entity = Product(
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
                production_date=datetime(year=2014, month=4, day=1, hour=9, minute=30, second=45, tzinfo=timezone.utc),
                mileage=2**31,  # an int64 integer
            ),
        )

    def create_delete_entity(self):
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            # Create a table in case it does not already exist
            try:
                table_client.create_table()
            except HttpResponseError:
                print("Table already exists")

            # [START create_entity]
            try:
                resp = table_client.create_entity(entity=self.entity, encoder=MyEncoder())
                print(resp)
            except ResourceExistsError:
                print("Entity already exists")
            # [END create_entity]

            # [START delete_entity]
            table_client.delete_entity(partition_key=self.entity.PartitionKey, row_key=self.entity.RowKey)
            # [END delete_entity]
            print("Successfully deleted!")

            table_client.delete_table()
            print("Cleaned up")


if __name__ == "__main__":
    ide = InsertDeleteEntity()
    ide.create_delete_entity()
