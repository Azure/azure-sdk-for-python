# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: table_samples_client.py

DESCRIPTION:
    These samples demonstrate the following: creating and setting an access policy to generate a
    sas token, getting a table client from a table URL, setting and getting table
    metadata, sending messages and receiving them individually, deleting and
    clearing all messages, and peeking and updating messages.

USAGE:
    python table_samples_client.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

from datetime import datetime, timedelta
import os


class TableEntitySamples(object):
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    def set_access_policy(self):
        # [START create_table_client_from_connection_string]
        from azure.table import TableClient
        table = TableClient.from_connection_string(self.connection_string, table_name="mytable1")
        # [END create_table_client_from_connection_string]

        # Create the Table
        table.create_table()

        try:
            # [START set_access_policy]
            # Create an access policy
            from azure.table import AccessPolicy, TableSasPermissions
            access_policy = AccessPolicy()
            access_policy.start = datetime.utcnow() - timedelta(hours=1)
            access_policy.expiry = datetime.utcnow() + timedelta(hours=1)
            access_policy.permission = TableSasPermissions(add=True)
            identifiers = {'my-access-policy-id': access_policy}

            # Set the access policy
            table.set_table_access_policy(identifiers)
            # [END set_access_policy]

            # Use the access policy to generate a SAS token
            # [START table_client_sas_token]
            from azure.table import generate_table_sas
            sas_token = generate_table_sas(
                table.account_name,
                table.table_name,
                table.credential.account_key,
                policy_id='my-access-policy-id'
            )
            # [END table_client_sas_token]

            # Authenticate with the sas token
            # [START create_table_client]
           # token_auth_table = table.from_table_url(
          #      table_url=table.url,
          #      credential=sas_token
         #   )
            # [END create_table_client]

        finally:
            # Delete the table
            table.delete_table()

    def create_and_get_entities(self):
        # Instantiate a table service client
        from azure.table import TableClient
        table = TableClient.from_connection_string(self.connection_string, table_name="mytable3")

        # Create the Table
        table.create_table()

        my_entity = {
            'PartitionKey': 'color',
            'RowKey': 'crayola',
            'text': 'Marker',
            'color': 'Purple',
            'price': '5'
        }
        try:
            # [START create_entity]
            created_entity = table.create_entity(table_entity_properties=my_entity)
            print(created_entity)
            # [END create_entity]

            # [START get_entity]
            # Get Entity by partition and row key
            got_entity = table.get_entity(partition_key=my_entity['PartitionKey'],
                                                                         row_key=my_entity['RowKey'])
            print(got_entity)
            # [END get_entity]

        finally:
            # Delete the table
            table.delete_table()

    def query_entities(self):
        # Instantiate a table service client
        from azure.table import TableClient
        table = TableClient.from_connection_string(self.connection_string, table_name="mytable4")

        # Create the table
        table.create_table()

        entity = {'PartitionKey': 'color2', 'RowKey': 'sharpie', 'text': 'Marker', 'color': 'Purple', 'price': '5'}
        entity1 = {'PartitionKey': 'color2', 'RowKey': 'crayola', 'text': 'Marker', 'color': 'Red', 'price': '3'}

        try:
            # Create entities
            table.create_entity(table_entity_properties=entity)
            table.create_entity(table_entity_properties=entity1)
            # [START query_entities]
            # Query the entities in the table
            entities = list(table.query_entities())

            for e in entities:
                print(e)
            # [END query_entities]

        finally:
            # Delete the table
            table.delete_table()

    def upsert_entities(self):
        # Instantiate a table service client
        from azure.table import TableClient, UpdateMode
        table = TableClient.from_connection_string(self.connection_string, table_name="mytable5")

        # Create the table
        table.create_table()

        entity = {'PartitionKey': 'color', 'RowKey': 'sharpie', 'text': 'Marker', 'color': 'Purple', 'price': '5'}
        entity1 = {'PartitionKey': 'color', 'RowKey': 'crayola', 'text': 'Marker', 'color': 'Red', 'price': '3'}

        try:
            # Create entities
            created = table.create_entity(table_entity_properties=entity)

            # [START upsert_entity]
            # Try Replace and then Insert on Fail
            insert_entity = table.upsert_entity(mode=UpdateMode.replace, table_entity_properties=entity1)
            print(insert_entity)

            # Try merge, and merge since already in table
            created.text = "NewMarker"
            merged_entity = table.upsert_entity(mode=UpdateMode.merge, table_entity_properties=entity)
            print(merged_entity)
            # [END upsert_entity]

        finally:
            # Delete the table
            table.delete_table()

    def update_entities(self):
        # Instantiate a table service client
        from azure.table import TableClient, UpdateMode
        table = TableClient.from_connection_string(self.connection_string, table_name="mytable6")

        # Create the table and Table Client
        table.create_table()

        entity = {'PartitionKey': 'color', 'RowKey': 'sharpie', 'text': 'Marker', 'color': 'Purple', 'price': '5'}

        try:
            # Create entity
            created = table.create_entity(table_entity_properties=entity)

            # [START update_entity]
            # Update the entity
            created.text = "NewMarker"
            table.update_entity(mode=UpdateMode.replace, table_entity_properties=created)

            # Get the replaced entity
            replaced = table.get_entity(
                partition_key=created.PartitionKey, row_key=created.RowKey)
            print(replaced)

            # Merge the entity
            replaced.color = "Blue"
            table.update_entity(mode=UpdateMode.merge, table_entity_properties=replaced)

            # Get the merged entity
            merged = table.get_entity(
                partition_key=replaced.PartitionKey, row_key=replaced.RowKey)
            print(merged)
            # [END update_entity]

        finally:
            # Delete the table
            table.delete_table()


if __name__ == '__main__':
    sample = TableEntitySamples()
    sample.set_access_policy()
    sample.create_and_get_entities()
    sample.query_entities()
    sample.upsert_entities()
    sample.update_entities()
