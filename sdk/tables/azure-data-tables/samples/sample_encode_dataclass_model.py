# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_encode_dataclass_model.py

DESCRIPTION:
    These samples demonstrate the following: inserting entities into a table
    and deleting entities from a table.

USAGE:
    python sample_encode_dataclass_model.py

    Set the environment variables with your own values before running the sample:
    1) TABLES_COSMOS_ENDPOINT_SUFFIX - the Table cosmos DB service account URL suffix
    2) TABLES_COSMOS_ACCOUNT_NAME - the name of the cosmos DB account
    3) TABLES_PRIMARY_COSMOS_ACCOUNT_KEY - the cosmos DB account access key
"""
import os
from datetime import datetime, timezone
from uuid import uuid4, UUID
from enum import Enum
from dotenv import find_dotenv, load_dotenv
from dataclasses import dataclass, asdict
from typing import Optional
from azure.data.tables import TableClient, UpdateMode, EdmType


@dataclass
class Car:
    PartitionKey: str
    RowKey: UUID
    price: Optional[float] = None
    last_updated: Optional[datetime] = None
    product_id: Optional[UUID] = None
    inventory_count: Optional[int] = None
    barcode: Optional[bytes] = None
    color: Optional[str] = None
    maker: Optional[str] = None
    model: Optional[str] = None
    production_date: Optional[datetime] = None
    big_number: Optional[int] = None
    is_second_hand: Optional[bool] = None


class Color(str, Enum):
    WHITE = "white"
    GRAY = "gray"
    BLACK = "black"


def encode_int(value):
    return EdmType.STRING, str(value)


def encode_uuid(value):
    return None, str(value)


encoder_map = {
    int: encode_int,
    UUID: encode_uuid,
}


def decode_string(value):
    try:
        return int(value)
    except ValueError:
        try:
            return Color(value)
        except ValueError:
            try:
                return UUID(value)
            except ValueError:
                return value


decoder_map = {
    EdmType.STRING: decode_string,
}


class InsertUpdateDeleteEntity(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.environ["TABLES_PRIMARY_COSMOS_ACCOUNT_KEY"]
        self.endpoint_suffix = os.environ["TABLES_COSMOS_ENDPOINT_SUFFIX"]
        self.account_name = os.environ["TABLES_COSMOS_ACCOUNT_NAME"]
        self.endpoint = f"{self.account_name}.table.{self.endpoint_suffix}"
        self.connection_string = f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.access_key};EndpointSuffix={self.endpoint_suffix}"
        self.table_name = "CustomEncoderDataclassModel"

    def create_delete_entity(self):
        table_client = TableClient.from_connection_string(
            self.connection_string, self.table_name, encoder_map=encoder_map, decoder_map=decoder_map
        )
        with table_client:
            table_client.create_table()

            entity = Car(
                PartitionKey="PK",
                RowKey=uuid4(),
                price=4.99,
                last_updated=datetime.today(),
                product_id=uuid4(),
                inventory_count=42,
                barcode=b"135aefg8oj0ld58",  # cspell:disable-line
                color=Color.WHITE,
                model="model",
                production_date=datetime(year=2014, month=4, day=1, hour=9, minute=30, second=45, tzinfo=timezone.utc),
                big_number=2**63,  # an integer exceeds max int64
                is_second_hand=True,
            )

            result = table_client.create_entity(entity=asdict(entity))
            print(f"Created entity: {result}")

            result = table_client.get_entity(entity.PartitionKey, str(entity.RowKey))
            print(f"Get entity result: {result}")

            table_client.delete_entity(entity=asdict(entity))
            print("Successfully deleted!")

            table_client.delete_table()
            print("Cleaned up")

    def upsert_update_entities(self):
        table_client = TableClient.from_connection_string(
            self.connection_string,
            table_name=f"{self.table_name}UpsertUpdate",
            encoder_map=encoder_map,
            decoder_map=decoder_map,
        )

        with table_client:
            table_client.create_table()

            entity1 = Car(
                PartitionKey="PK",
                RowKey=uuid4(),
                price=4.99,
                last_updated=datetime.today(),
                product_id=uuid4(),
                inventory_count=42,
                barcode=b"135aefg8oj0ld58",  # cspell:disable-line
            )
            entity2 = Car(
                PartitionKey=entity1.PartitionKey,
                RowKey=entity1.RowKey,
                color="red",
                maker="maker2",
                model="model2",
                production_date=datetime(year=2014, month=4, day=1, hour=9, minute=30, second=45, tzinfo=timezone.utc),
                big_number=2**63,  # an integer exceeds max int64
                is_second_hand=True,
            )

            table_client.upsert_entity(mode=UpdateMode.REPLACE, entity=asdict(entity1))
            inserted_entity = table_client.get_entity(entity1.PartitionKey, str(entity1.RowKey))
            print(f"Inserted entity: {inserted_entity}")

            table_client.upsert_entity(mode=UpdateMode.MERGE, entity=asdict(entity2))
            merged_entity = table_client.get_entity(entity2.PartitionKey, str(entity2.RowKey))
            print(f"Merged entity: {merged_entity}")

            entity3 = Car(
                PartitionKey=entity1.PartitionKey,
                RowKey=entity2.RowKey,
                color="white",
            )
            table_client.update_entity(mode=UpdateMode.REPLACE, entity=asdict(entity3))
            replaced_entity = table_client.get_entity(entity3.PartitionKey, str(entity3.RowKey))
            print(f"Replaced entity: {replaced_entity}")

            table_client.update_entity(mode=UpdateMode.REPLACE, entity=asdict(entity2))
            merged_entity = table_client.get_entity(entity2.PartitionKey, str(entity2.RowKey))
            print(f"Merged entity: {merged_entity}")

            table_client.delete_entity(partition_key=entity1.PartitionKey, row_key=str(entity1.RowKey))
            print("Successfully deleted!")

            table_client.delete_table()
            print("Cleaned up")


if __name__ == "__main__":
    ide = InsertUpdateDeleteEntity()
    ide.create_delete_entity()
    ide.upsert_update_entities()
