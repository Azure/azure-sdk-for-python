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
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

import os
from dotenv import find_dotenv, load_dotenv

class InsertDeleteEntity(object):

    def __init__(self):
        load_dotenv(find_dotenv())
        # self.connection_string = os.getenv("AZURE_TABLES_CONNECTION_STRING")
        self.access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        self.endpoint = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        self.account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        self.account_url = "{}.table.{}".format(self.account_name, self.endpoint)
        self.connection_string = u"DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            self.account_name,
            self.access_key,
            self.endpoint
        )
        self.table_name = "SampleInsertDelete"

        self.entity = {
            u'PartitionKey': u'color',
            u'RowKey': u'brand',
            u'text': u'Marker',
            u'color': u'Purple',
            u'price': u'5'
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
                entity = table_client.create_entity(entity=self.entity)
                print(entity)
            except ResourceExistsError:
                print("Entity already exists")
        # [END create_entity]

    def delete_entity(self):
        from azure.data.tables import TableClient
        from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
        from azure.core import MatchConditions

        with TableClient(account_url=self.account_url, credential=self.access_key, table_name=self.table_name) as table_client:

            # Create entity to delete (to showcase etag)
            try:
                resp = table_client.create_entity(entity=self.entity)
            except ResourceExistsError:
                print("Entity already exists!")

            # [START delete_entity]
            try:
                table_client.delete_entity(
                    row_key=self.entity["RowKey"],
                    partition_key=self.entity["PartitionKey"]
                )
                print("Successfully deleted!")
            except ResourceNotFoundError:
                print("Entity does not exists")
            # [END delete_entity]


if __name__ == '__main__':
    ide = InsertDeleteEntity()
    ide.create_entity()
    ide.delete_entity()