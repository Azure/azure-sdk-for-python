# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_query_table_async.py

DESCRIPTION:
    These samples demonstrate the following: querying a table for entities.

USAGE:
    python sample_query_table_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

import os
import copy
import random
from time import sleep
import asyncio
from dotenv import find_dotenv, load_dotenv


class SampleTablesQuery(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        self.endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        self.account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        self.endpoint = "{}.table.{}".format(self.account_name, self.endpoint_suffix)
        self.connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            self.account_name, self.access_key, self.endpoint_suffix
        )
        self.table_name = "OfficeSupplies"

    async def insert_random_entities(self):
        from azure.data.tables.aio import TableClient
        from azure.core.exceptions import ResourceExistsError

        brands = ["Crayola", "Sharpie", "Chameleon"]
        colors = ["red", "blue", "orange", "yellow"]
        names = ["marker", "pencil", "pen"]
        entity_template = {
            "PartitionKey": "pk",
            "RowKey": "row",
        }

        table_client = TableClient.from_connection_string(self.connection_string, self.table_name)
        async with table_client:
            try:
                await table_client.create_table()
            except ResourceExistsError:
                print("Table already exists")

            for i in range(25):
                e = copy.deepcopy(entity_template)
                e["RowKey"] += str(i)
                e["Name"] = random.choice(names)
                e["Brand"] = random.choice(brands)
                e["Color"] = random.choice(colors)
                e["Value"] = random.randint(0, 100)
                await table_client.create_entity(entity=e)

    async def sample_query_entities(self):
        from azure.data.tables.aio import TableClient
        from azure.core.exceptions import HttpResponseError

        # [START query_entities]
        async with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            try:
                print("Entities with name: marker and brand: Crayola")
                queried_entities1 = table_client.query_entities(
                    query_filter={"name": "marker", "brand": "Crayola"},
                    select=["Brand", "Color"],
                    parameters="Name eq @name and Brand eq @brand",
                    headers ={"Accept" : "application/json;odata=nometadata"}
                )
                async for entity_chosen in queried_entities1:
                    print(entity_chosen)

                print("Entities with 25 < Value < 50")
                queried_entities2 = table_client.query_entities(
                    query_filter="Value gt @lower and Value lt @upper",
                    select=["Value"],
                    parameters={"lower": 25, "upper": 50},
                    headers ={"Accept" : "application/json;odata=nometadata"}
                )
                async for entity_chosen in queried_entities2:
                    print(entity_chosen)

            except HttpResponseError as e:
                print(e.message)
        # [END query_entities]

    async def clean_up(self):
        print("cleaning up")
        from azure.data.tables.aio import TableClient

        async with TableClient.from_connection_string(self.connection_string, self.table_name) as table_client:
            await table_client.delete_table()


async def main():
    stq = SampleTablesQuery()
    try:
        await stq.insert_random_entities()
        await stq.sample_query_entities()
    except Exception as e:
        print(e)
    finally:
        await stq.clean_up()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
