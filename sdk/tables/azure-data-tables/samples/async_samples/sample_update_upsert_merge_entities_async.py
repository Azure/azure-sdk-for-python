# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_update_upsert_merge_entities_async.py

DESCRIPTION:
    These samples demonstrate the following: updating, upserting, and merging entities.

USAGE:
    python sample_update_upsert_merge_entities_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

import asyncio
from dotenv import find_dotenv, load_dotenv


class TableEntitySamples(object):
    def __init__(self):
        load_dotenv(find_dotenv())

    async def create_and_get_entities(self):
        # Instantiate a table service client
        import os
        from azure.data.tables.aio import TableClient

        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            account_name, access_key, endpoint_suffix
        )

        table_base = "UpdateUpsertMergeAsync"

        table = TableClient.from_connection_string(connection_string, table_name=table_base + "create")

        async with table:
            await table.create_table()

            my_entity = {
                "PartitionKey": "color",
                "RowKey": "crayola",
                "text": "Marker",
                "color": "Purple",
                "price": "5",
            }
            try:
                created_entity = await table.create_entity(entity=my_entity)
                print("Created entity: {}".format(created_entity))

                # [START get_entity]
                # Get Entity by partition and row key
                got_entity = await table.get_entity(
                    partition_key=my_entity["PartitionKey"], row_key=my_entity["RowKey"]
                )
                print("Received entity: {}".format(got_entity))
                # [END get_entity]

            finally:
                await table.delete_table()

    async def list_all_entities(self):
        # Instantiate a table service client
        import os

        from azure.data.tables.aio import TableClient

        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            account_name, access_key, endpoint_suffix
        )

        table_base = "UpdateUpsertMergeAsync"

        table = TableClient.from_connection_string(connection_string, table_name=table_base + "list")

        # Create the table
        async with table:
            await table.create_table()

            entity = {"PartitionKey": "color2", "RowKey": "sharpie", "text": "Marker", "color": "Purple", "price": "5"}
            entity1 = {"PartitionKey": "color2", "RowKey": "crayola", "text": "Marker", "color": "Red", "price": "3"}

            try:
                # Create entities
                await table.create_entity(entity=entity)
                await table.create_entity(entity=entity1)
                # [START list_entities]
                # Query the entities in the table
                i = 0
                async for entity in table.list_entities():
                    print("Entity #{}: {}".format(i, entity))
                    i += 1
                # [END list_entities]

            finally:
                await table.delete_table()

    async def update_entities(self):
        # Instantiate a table service client
        import os

        from azure.data.tables.aio import TableClient
        from azure.data.tables import UpdateMode

        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            account_name, access_key, endpoint_suffix
        )

        table_base = "UpdateUpsertMergeAsync"

        table = TableClient.from_connection_string(connection_string, table_name=table_base + "update")

        # Create the table and Table Client
        async with table:
            await table.create_table()

            entity = {"PartitionKey": "color", "RowKey": "sharpie", "text": "Marker", "color": "Purple", "price": "5"}
            entity1 = {"PartitionKey": "color2", "RowKey": "crayola", "text": "Marker", "color": "Red", "price": "3"}

            try:
                # Create entities
                await table.create_entity(entity=entity)
                created = await table.get_entity(partition_key=entity["PartitionKey"], row_key=entity["RowKey"])

                # [START upsert_entity]
                # Try Replace and insert on fail
                insert_entity = await table.upsert_entity(mode=UpdateMode.REPLACE, entity=entity1)
                print("Inserted entity: {}".format(insert_entity))

                created["text"] = "NewMarker"
                merged_entity = await table.upsert_entity(mode=UpdateMode.MERGE, entity=entity)
                print("Merged entity: {}".format(merged_entity))
                # [END upsert_entity]

                # [START update_entity]
                # Update the entity
                created["text"] = "NewMarker"
                await table.update_entity(mode=UpdateMode.REPLACE, entity=created)

                # Get the replaced entity
                replaced = await table.get_entity(partition_key=created["PartitionKey"], row_key=created["RowKey"])
                print("Replaced entity: {}".format(replaced))

                # Merge the entity
                replaced["color"] = "Blue"
                await table.update_entity(mode=UpdateMode.MERGE, entity=replaced)

                # Get the merged entity
                merged = await table.get_entity(partition_key=replaced["PartitionKey"], row_key=replaced["RowKey"])
                print("Merged entity: {}".format(merged))
                # [END update_entity]

            finally:
                await table.delete_table()

    async def clean_up(self):
        import os
        from azure.data.tables.aio import TableServiceClient

        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            account_name, access_key, endpoint_suffix
        )
        async with TableServiceClient.from_connection_string(connection_string) as tsc:
            async for table in tsc.list_tables():
                await tsc.delete_table(table.name)


async def main():
    sample = TableEntitySamples()
    await sample.create_and_get_entities()
    await sample.list_all_entities()
    await sample.update_entities()
    await sample.clean_up()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
