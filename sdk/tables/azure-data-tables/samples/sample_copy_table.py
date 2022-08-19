# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_copy_table.py

DESCRIPTION:
    These samples demonstrate how to copy tables between table and blob storage.

USAGE:
    python sample_copy_table.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
    2) TABLES_STORAGE_ENDPOINT_SUFFIX - the Table service account URL suffix
    3) TABLES_STORAGE_ACCOUNT_NAME - the name of the storage account
    4) TABLES_PRIMARY_STORAGE_ACCOUNT_KEY - the storage account access key
"""


from datetime import datetime
from uuid import uuid4
import os
import json
from azure.storage.blob import BlobServiceClient
from azure.data.tables import TableClient
from dotenv import find_dotenv, load_dotenv


class CopyTableSamples(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        self.endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        self.account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        self.table_connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            self.account_name, self.access_key, self.endpoint_suffix
        )
        self.table_client = TableClient.from_connection_string(conn_str=self.table_connection_string, table_name="mytable")
        self.blob_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.blob_service_client = BlobServiceClient.from_connection_string(self.blob_connection_string)
        self.container_name = "mycontainer"
        self.blob_name = "myblob"
        self.entity = {
            "PartitionKey": "color",
            "text": "Marker",
            "color": "Purple",
            "price": 4.99,
            "last_updated": datetime.today(),
            "product_id": uuid4(),
            "inventory_count": 42,
            "barcode": b"135aefg8oj0ld58"
        }

    def copy_table_from_table_to_blob(self):
        self._setup_table()
        try:
            self.container = self.blob_service_client.create_container(self.container_name)
            blob_client = self.blob_service_client.get_blob_client(self.container_name, self.blob_name)
            # Download entities from table to memory
            entities = self.table_client.list_entities()
            # Upload in-memory table data to a blob that stays in a container
            for i in range(10):
                entity = json.dumps(entities[i])
                blob_client.upload_blob(name=self.blob_name+str(i), data=entity)
        finally:
            self._tear_down()

    def copy_table_from_blob_to_table(self):
        self._setup_blob()
        try:
            # Download entities from blob to memory
            # Note: when entities size is too big, may need to do copy by chunk
            blob_content = self.blob_client.download_blob().readall()
            entities = json.load(blob_content)
            # Upload entities to a table
            self.table_client.create_table()
            for entity in entities:
                self.table_client.upsert_entity(entity)
        finally:
            self._tear_down()
    
    def _setup_table(self):
        self.table_client.create_table()
        for i in range(10):
            self.entity["RowKey"] = str(i)
            self.table_client.create_entity(self.entity)
    
    def _setup_blob(self):
        self.blob_service_client.create_container(self.container_name)
        self.blob_client = self.blob_service_client.get_blob_client(self.container_name, self.blob_name)
        for i in range(10):
            self.entity["RowKey"] = str(i)
            entity = json.dumps(self.entity)
            self.blob_client.upload_blob(name=self.blob_name+str(i), data=entity)

    def _tear_down(self):
        self.table_client.delete_table()
        self.blob_client.delete_blob()
        self.container.delete_container()

if __name__ == "__main__":
    sample = CopyTableSamples()
    sample.copy_table_from_table_to_blob()
    sample.copy_table_from_blob_to_table()
