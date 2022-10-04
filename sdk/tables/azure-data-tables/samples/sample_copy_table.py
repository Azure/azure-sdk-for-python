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
    1) TABLES_STORAGE_ENDPOINT_SUFFIX - the Table storage service account URL suffix
    2) TABLES_STORAGE_ACCOUNT_NAME - the Tables storage account name
    3) TABLES_PRIMARY_STORAGE_ACCOUNT_KEY - the Tables storage account access key
    4) STORAGE_ACCOUNT_NAME - the blob storage account name
    5) STORAGE_ACCOUNT_KEY - the blob storage account key
"""


import copy
import json
import os
from azure.storage.blob import BlobServiceClient
from azure.data.tables import TableServiceClient
from datetime import datetime
from dotenv import find_dotenv, load_dotenv
from uuid import uuid4, UUID


class CopyTableSamples(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        self.endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        self.account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        self.table_connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            self.account_name, self.access_key, self.endpoint_suffix
        )
        self.copy_to_blob_table_name = "copytoblobtablename" + str(uuid4()).replace("-", "")
        self.copy_to_table_table_name = "copytotabletablename" + str(uuid4()).replace("-", "")
        self.blob_account_name = os.getenv("STORAGE_ACCOUNT_NAME")
        self.blob_account_key = os.getenv("STORAGE_ACCOUNT_KEY")
        self.blob_connection_string = "DefDefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix=core.windows.net".format(
            self.blob_account_name, self.blob_account_key
        )
        self.blob_service_client = BlobServiceClient.from_connection_string(self.blob_connection_string)
        self.entity = {
            "PartitionKey": "color",
            "text": "Marker",
            "color": "Purple",
            "price": 4.99,
            "last_updated": datetime.today(),
            "product_id": uuid4(),
            "inventory_count": 42,
            "barcode": b"135aefg8oj0ld58" # cspell:disable-line
        }

    def copy_table_from_table_to_blob(self):
        print("Start to copy table from Tables table to Storage blob.")
        print("Table name: " + self.copy_to_blob_table_name)
        self._setup_table()
        try:
            self.container_client = self.blob_service_client.create_container(self.copy_to_blob_table_name)
            # Upload in-memory table data to a blob that stays in a container
            for entity in self.table_client.list_entities():
                # Convert type datetime, bytes, UUID values to string as they're not JSON serializable
                entity["last_updated"] = entity["last_updated"].isoformat()
                entity["product_id"] = entity["product_id"].hex
                entity["barcode"] = entity["barcode"].decode("utf-8")
                blob_name = entity["PartitionKey"] + entity["RowKey"]
                blob_client = self.blob_service_client.get_blob_client(self.copy_to_blob_table_name, blob_name)
                blob_client.upload_blob(json.dumps(entity))
            print("Done!")
        finally:
            self._tear_down()

    def copy_table_from_blob_to_table(self):
        print("Start to copy table from Storage blob to Tables table.")
        print("Table name: " + self.copy_to_blob_table_name)
        self._setup_blob()
        try:
            # Download entities from blob to memory
            # Note: when entities size is too big, may need to do copy by chunk
            blob_list = self.container_client.list_blobs()
            # Upload entities to a table
            table_service_client = TableServiceClient.from_connection_string(conn_str=self.table_connection_string, table_name=self.copy_to_table_table_name)
            self.table_client = table_service_client.get_table_client(self.copy_to_table_table_name)
            self.table_client.create_table()
            for blob in blob_list:
                blob_client = self.container_client.get_blob_client(blob)
                blob_stream_downloader = blob_client.download_blob()
                entity = json.loads(blob_stream_downloader.readall())
                # Convert values back to their original types
                entity["last_updated"] = datetime.fromisoformat(entity["last_updated"])
                entity["product_id"] = UUID(entity["product_id"])
                entity["barcode"] = entity["barcode"].encode("utf-8")
                self.table_client.upsert_entity(entity)
            print("Done!")
        finally:
            self._tear_down()

    def _setup_table(self):
        table_service_client = TableServiceClient.from_connection_string(conn_str=self.table_connection_string, table_name=self.copy_to_blob_table_name)
        self.table_client = table_service_client.get_table_client(self.copy_to_blob_table_name)
        self.table_client.create_table()
        for i in range(10):
            self.entity["RowKey"] = str(i)
            self.table_client.create_entity(self.entity)

    def _setup_blob(self):
        self.container_client = self.blob_service_client.create_container(self.copy_to_table_table_name)
        entity = copy.deepcopy(self.entity)
        # Convert type datetime, bytes, UUID values to string as they're not JSON serializable
        entity["last_updated"] = entity["last_updated"].isoformat()
        entity["product_id"] = entity["product_id"].hex
        entity["barcode"] = entity["barcode"].decode("utf-8")
        for i in range(10):
            entity["RowKey"] = str(i)
            blob_name = entity["PartitionKey"] + entity["RowKey"]
            blob_client = self.blob_service_client.get_blob_client(self.copy_to_table_table_name, blob_name)
            blob_client.upload_blob(json.dumps(entity))

    def _tear_down(self):
        self.table_client.delete_table()
        self.container_client.delete_container()


if __name__ == "__main__":
    sample = CopyTableSamples()
    sample.copy_table_from_table_to_blob()
    sample.copy_table_from_blob_to_table()
