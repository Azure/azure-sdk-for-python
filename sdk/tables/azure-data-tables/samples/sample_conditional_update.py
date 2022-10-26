# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_conditional_update.py

DESCRIPTION:
    These samples demonstrate how to update Tables storage table conditionally. The way to update Tables cosmos table is similar.

USAGE:
    python sample_conditional_update.py

    Set the environment variables with your own values before running the sample:
    1) TABLES_STORAGE_ENDPOINT_SUFFIX - the Table storage service account URL suffix
    2) TABLES_STORAGE_ACCOUNT_NAME - the Tables storage account name
    3) TABLES_PRIMARY_STORAGE_ACCOUNT_KEY - the Tables storage account access key
"""
import os
from datetime import datetime
from dotenv import find_dotenv, load_dotenv
from uuid import uuid4
from azure.data.tables import TableClient
from azure.data.tables._models import UpdateMode
from azure.core import MatchConditions

class ConditionalUpdateSamples(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        self.endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        self.account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        self.endpoint = "{}.table.{}".format(self.account_name, self.endpoint_suffix)
        self.connection_string = (
            "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
                self.account_name, self.access_key, self.endpoint_suffix
            )
        )
        self.table_name = "SampleConditionalUpdate" + str(uuid4()).replace("-", "")
        self.entity1 = {
            "PartitionKey": "color",
            "RowKey": "brand",
            "text": "Marker",
            "color": "Purple",
            "price": 4.99,
            "last_updated": datetime.today(),
            "product_id": uuid4()
        }
        self.entity2 = {
            "PartitionKey": "color",
            "RowKey": "brand",
            "color": "Red",
            "inventory_count": 42,
            "barcode": b"135aefg8oj0ld58" # cspell:disable-line
        }

    def conditional_update(self):
        with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            table_client.create_table()
            metadata1 = table_client.create_entity(entity=self.entity1)
            entity1 = table_client.get_entity(partition_key=self.entity1["PartitionKey"], row_key=self.entity1["RowKey"])
            print("Entity:")
            print(entity1)

            metadata2 = table_client.update_entity(entity=self.entity2, mode=UpdateMode.MERGE, match_condition=MatchConditions.IfNotModified, etag=metadata1["etag"])
            entity2 = table_client.get_entity(partition_key=self.entity1["PartitionKey"], row_key=self.entity1["RowKey"])
            print("Entity after merge:")
            print(entity2)

            table_client.update_entity(entity=self.entity2, mode=UpdateMode.REPLACE, match_condition=MatchConditions.IfNotModified, etag=metadata2["etag"])
            entity3 = table_client.get_entity(partition_key=self.entity1["PartitionKey"], row_key=self.entity1["RowKey"])
            print("Entity after replace:")
            print(entity3)

            table_client.delete_table()


if __name__ == "__main__":
    sample = ConditionalUpdateSamples()
    sample.conditional_update()
