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
from azure.core.exceptions import ResourceExistsError, ResourceModifiedError

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
        self.table_name_prefix = "SampleConditionalUpdate"
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

    def conditional_update_basic(self):
        with TableClient.from_connection_string(self.connection_string, self.table_name_prefix + uuid4().hex) as table_client:
            table_client.create_table()
            metadata1 = table_client.create_entity(entity=self.entity1)
            print("Entity:")
            print(self.entity1)

            # Merge properties of an entity with one that already existed in a table.
            # This operation will only succeed if the entity has not been modified since we last retrieved the Etag.
            try:
                metadata2 = table_client.update_entity(entity=self.entity2, mode=UpdateMode.MERGE, match_condition=MatchConditions.IfNotModified, etag=metadata1["etag"])
            except ResourceModifiedError:
                print("This entity has been altered and may no longer be in the expected state.")
            entity2 = table_client.get_entity(partition_key=self.entity1["PartitionKey"], row_key=self.entity1["RowKey"])
            print("Entity after merge:")
            print(entity2)

            # Update an existing entity by replacing all of its properties with those specified.
            # This operation will only succeed if the entity has not been modified since we last retrieved the Etag.
            try:
                table_client.update_entity(entity=self.entity2, mode=UpdateMode.REPLACE, match_condition=MatchConditions.IfNotModified, etag=metadata2["etag"])
            except ResourceModifiedError:
                print("This entity has been altered and may no longer be in the expected state.")
            entity3 = table_client.get_entity(partition_key=self.entity1["PartitionKey"], row_key=self.entity1["RowKey"])
            print("Entity after replace:")
            print(entity3)

            table_client.delete_table()
    
    def conditional_update_with_a_target_field(self):
        with TableClient.from_connection_string(self.connection_string, self.table_name_prefix + uuid4().hex) as table_client:
            table_client.create_table()
            table_client.create_entity(entity=self.entity1)
            target_field = "barcode"

            # In this scenario, will try to create an entity at first. If the entity with the same PartitionKey and RowKey already exists,
            # will update the existing entity when target field is missing.
            try:
                table_client.create_entity(entity=self.entity2)
            except ResourceExistsError:
                entity = table_client.get_entity(partition_key=self.entity2["PartitionKey"], row_key=self.entity2["RowKey"])
                if target_field not in entity:
                    table_client.update_entity(
                        entity={"PartitionKey": self.entity2["PartitionKey"], "RowKey": self.entity2["RowKey"], target_field: "foo"},
                        mode=UpdateMode.MERGE,
                        match_condition=MatchConditions.IfNotModified,
                        etag=entity.metadata["etag"]
                    )

            table_client.delete_table()


if __name__ == "__main__":
    sample = ConditionalUpdateSamples()
    sample.conditional_update_basic()
    sample.conditional_update_with_a_target_field()
