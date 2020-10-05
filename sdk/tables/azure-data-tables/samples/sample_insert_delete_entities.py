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

class InsertDeleteEntity(object):
    connection_string = os.getenv("AZURE_TABLES_CONNECTION_STRING")
    access_key = os.getenv("AZURE_TABLES_KEY")
    account_url = os.getenv("AZURE_TABLES_ACCOUNT_KEY")
    table_name = "OfficeSupplies"

    entity = {
        'PartitionKey': 'color',
        'RowKey': 'brand',
        'text': 'Marker',
        'color': 'Purple',
        'price': '5'
    }

    def create_entity(self):
        from azure.data.tables import TableClient
        from azure.core.exceptions import ResourceExistsError, HttpResponseError

        table_client = TableClient.from_connection_string(self.connection_string, self.table_name)

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

        table_client = TableClient(account_url=self.account_url, credential=self.access_key, table_name=self.table_name)

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