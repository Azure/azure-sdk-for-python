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
    and deleting entities from a table.

USAGE:
    python sample_insert_delete_entities.py

    Set the environment variables with your own values before running the sample:
    1) TABLES_STORAGE_ENDPOINT_SUFFIX - the Table service account URL suffix
    2) TABLES_STORAGE_ACCOUNT_NAME - the name of the storage account
    3) TABLES_PRIMARY_STORAGE_ACCOUNT_KEY - the storage account access key
"""
import sys
from datetime import datetime
import os
from uuid import uuid4, UUID
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


class InsertDeleteEntity(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.environ["TABLES_PRIMARY_STORAGE_ACCOUNT_KEY"]
        self.endpoint_suffix = os.environ["TABLES_STORAGE_ENDPOINT_SUFFIX"]
        self.account_name = os.environ["TABLES_STORAGE_ACCOUNT_NAME"]
        self.endpoint = f"{self.account_name}.table.{self.endpoint_suffix}"
        self.connection_string = f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.access_key};EndpointSuffix={self.endpoint_suffix}"
        self.table_name = "SampleInsertDelete"

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

    def create_entity(self):
        from azure.data.tables import TableClient
        from azure.core.exceptions import ResourceExistsError, HttpResponseError

        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:

            # Create a table in case it does not already exist
            try:
                table_client.create_table()
            except HttpResponseError:
                print("Table already exists")

            # [START create_entity]
            try:
                resp = table_client.create_entity(entity=self.entity)
                print(resp)
            except ResourceExistsError:
                print("Entity already exists")
            # [END create_entity]

    def delete_entity(self):
        from azure.data.tables import TableClient
        from azure.core.exceptions import ResourceExistsError
        from azure.core.credentials import AzureNamedKeyCredential

        credential = AzureNamedKeyCredential(self.account_name, self.access_key)
        with TableClient(endpoint=self.endpoint, table_name=self.table_name, credential=credential) as table_client:

            # Create an entity to delete (to showcase etag)
            try:
                table_client.create_entity(entity=self.entity)
            except ResourceExistsError:
                print("Entity already exists!")

            # [START delete_entity]
            table_client.delete_entity(row_key=self.entity["RowKey"], partition_key=self.entity["PartitionKey"])
            print("Successfully deleted!")
            # [END delete_entity]


if __name__ == "__main__":
    ide = InsertDeleteEntity()
    ide.create_entity()
    ide.delete_entity()
