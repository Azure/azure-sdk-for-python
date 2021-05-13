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

from dotenv import find_dotenv, load_dotenv


class InsertDeleteEntity(object):
    def __init__(self):
        load_dotenv(find_dotenv())

    def create_entity(self):
        # [START create_entity]
        import os

        from azure.data.tables import TableClient
        from azure.core.exceptions import ResourceExistsError, HttpResponseError

        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        connection_string = u"DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            account_name, access_key, endpoint_suffix
        )
        table_name = "SampleInsertDelete"

        entity = {
            u"PartitionKey": u"color",
            u"RowKey": u"brand",
            u"text": u"Marker",
            u"color": u"Purple",
            u"price": u"5",
        }

        with TableClient.from_connection_string(connection_string, table_name) as table_client:

            # Create a table in case it does not already exist
            try:
                table_client.create_table()
            except HttpResponseError:
                print("Table already exists")

            try:
                resp = table_client.create_entity(entity=entity)
                print(resp)
            except ResourceExistsError:
                print("Entity already exists")
        # [END create_entity]

    def delete_entity(self):
        # [START delete_entity]
        import os

        from azure.data.tables import TableClient
        from azure.core.exceptions import ResourceExistsError
        from azure.core.credentials import AzureNamedKeyCredential

        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        endpoint = "{}.table.{}".format(account_name, endpoint_suffix)
        table_name = "SampleInsertDelete"

        entity = {
            u"PartitionKey": u"color",
            u"RowKey": u"brand",
            u"text": u"Marker",
            u"color": u"Purple",
            u"price": u"5",
        }

        credential = AzureNamedKeyCredential(account_name, access_key)
        with TableClient(endpoint=endpoint, credential=credential, table_name=table_name) as table_client:

            # Create entity to delete (to showcase etag)
            try:
                resp = table_client.create_entity(entity=entity)
            except ResourceExistsError:
                print("Entity already exists!")

            table_client.delete_entity(row_key=entity["RowKey"], partition_key=entity["PartitionKey"])
            print("Successfully deleted!")
        # [END delete_entity]


if __name__ == "__main__":
    ide = InsertDeleteEntity()
    ide.create_entity()
    ide.delete_entity()
