# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_create_delete_table.py

DESCRIPTION:
    These samples demonstrate creating a table and deleting a table ffrom a storage account

USAGE:
    python sample_create_delete_table.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

import os
import logging

_LOGGER = logging.getLogger(__name__)

class CreateDeleteTable(object):
    connection_string = os.getenv("AZURE_TABLES_CONNECTION_STRING")
    access_key = os.getenv("AZURE_TABLES_KEY")
    account_url = os.getenv("AZURE_TABLES_ACCOUNT_URL")
    account_name = os.getenv("AZURE_TABLES_ACCOUNT_NAME")
    table_name = "OfficeSupplies"


    def create_table(self):
        from azure.data.tables import TableServiceClient
        from azure.core.exceptions import ResourceExistsError

        # [START create_table_from_tc]
        table_service_client = TableServiceClient.from_connection_string(self.connection_string)
        try:
            table_item = table_service_client.create_table(table_name=self.table_name)
            print("Created table {}!".format(table_item.table_name))
        except ResourceExistsError:
            print("Table already exists")
        # [END create_table_from_tc]

    def create_if_not_exists(self):
        from azure.data.tables import TableServiceClient

        # [START create_table_if_not_exists]
        table_service_client = TableServiceClient.from_connection_string(self.connection_string)
        table_item = TableServiceClient.create_table_if_not_exists(table_name=self.table_name)
        print("Table name: {}".format(table_item.table_name))
        # [END create_table_if_not_exists]

    def delete_table(self):
        from azure.data.tables import TableServiceClient
        from azure.core.exceptions import ResourceNotFoundError

        # [START delete_table_from_tc]
        table_service_client = TableServiceClient.from_connection_string(self.connection_string)
        try:
            table_service_client.delete_table(table_name=self.table_name)
            print("Deleted table {}!".format(self.table_name))
        except ResourceNotFoundError:
            print("Table could not be found")
        # [END delete_table_from_tc]

    def create_from_table_client(self):
        from azure.data.table import TableClient

        # [START create_table_from_table_client]
        table_client = TableClient.from_connection_string(
            conn_str=self.connection_string,
            table_name=self.table_name
        )
        try:
            table_item = table_client.create_table()
            print("Created table {}!".format(table_item.table_name))
        except ResourceExistsError:
            print("Table already exists")
        # [END create_table_from_table_client]

    def delete_from_table_client(self):
        from azure.data.table import TableClient

        # [START delete_table_from_table_client]
        table_client = TableClient.from_connection_string(
            conn_str=self.connection_string,
            table_name=self.table_name
        )
        try:
            table_client.delete_table()
            print("Deleted table {}!".format(self.table_name))
        except ResourceNotFoundError:
            print("Table could not be found")
        # [END delete_table_from_table_client]


if __name__ == '__main__':
    sample = CreateDeleteTable()
    sample.create_table()
    sample.delete_table()
