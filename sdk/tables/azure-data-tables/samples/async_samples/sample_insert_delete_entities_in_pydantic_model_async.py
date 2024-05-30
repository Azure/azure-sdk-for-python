# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_insert_delete_entities_in_pydantic_model_async.py

DESCRIPTION:
    These samples demonstrate the following: inserting entities in pydantic model into a table
    and deleting tables from a table.

USAGE:
    python sample_insert_delete_entities_in_pydantic_model_async.py

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
from typing import Dict, Union
from pydantic import BaseModel
from azure.data.tables import TableEntityEncoderABC
from azure.data.tables.aio import TableClient
from azure.core.exceptions import ResourceExistsError, HttpResponseError


class EntityType(BaseModel):
    PartitionKey: str
    RowKey: str
    text: str
    color: str
    price: float
    last_updated: datetime
    product_id: UUID
    inventory_count: int
    barcode: bytes


class MyEncoder(TableEntityEncoderABC[EntityType]):
    def encode_entity(self, entity: EntityType) -> Dict[str, Union[str, int, float, bool]]:
        return entity.model_dump()


class InsertDeleteEntity(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.environ["TABLES_PRIMARY_STORAGE_ACCOUNT_KEY"]
        self.endpoint_suffix = os.environ["TABLES_STORAGE_ENDPOINT_SUFFIX"]
        self.account_name = os.environ["TABLES_STORAGE_ACCOUNT_NAME"]
        self.endpoint = f"{self.account_name}.table.{self.endpoint_suffix}"
        self.connection_string = f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.access_key};EndpointSuffix={self.endpoint_suffix}"
        self.table_name = "SampleInsertDeletePydanticAsync"

        self.entity = EntityType(
            PartitionKey="color",
            RowKey="brand",
            text="Marker",
            color="Purple",
            price=4.99,
            last_updated=datetime.today(),
            product_id=uuid4(),
            inventory_count=42,
            barcode=b"135aefg8oj0ld58",  # cspell:disable-line
        )

    async def create_delete_entity(self):
        table_client = TableClient.from_connection_string(self.connection_string, self.table_name)
        async with table_client:
            # Create a table in case it does not already exist
            try:
                await table_client.create_table()
            except HttpResponseError:
                print("Table already exists")

            # [START create_entity]
            try:
                resp = await table_client.create_entity(entity=self.entity, encoder=MyEncoder())
                print(resp)
            except ResourceExistsError:
                print("Entity already exists")
            # [END create_entity]

            # [START delete_entity]
            await table_client.delete_entity(
                partition_key=self.entity.PartitionKey, row_key=self.entity.RowKey, encoder=MyEncoder()
            )
            # [END delete_entity]
            print("Successfully deleted!")

            await table_client.delete_table()
            print("Cleaned up")


async def main():
    ide = InsertDeleteEntity()
    await ide.create_delete_entity()


if __name__ == "__main__":
    asyncio.run(main())
