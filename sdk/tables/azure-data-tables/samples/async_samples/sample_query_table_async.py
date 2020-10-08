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
import asyncio

class SampleTablesQuery(object):
    connection_string = os.getenv("AZURE_TABLES_CONNECTION_STRING")
    table_name = "OfficeSupplies"

    entity_name = "marker"

    name_filter = "Name eq '{}'".format(entity_name)

    async def _insert_random_entities(self):
        from azure.data.tables.aio import TableClient
        brands = ["Crayola", "Sharpie", "Chameleon"]
        colors = ["red", "blue", "orange", "yellow"]
        names = ["marker", "pencil", "pen"]
        entity_template = {
            "PartitionKey": "pk",
            "RowKey": "row",
        }

        table_client = TableClient.from_connection_string(self.connection_string, self.table_name)
        async with table_client:
            await table_client.create_table()

            for i in range(10):
                e = copy.deepcopy(entity_template)
                e["RowKey"] += str(i)
                e["Name"] = random.choice(names)
                e["Brand"] = random.choice(brands)
                e["Color"] = random.choice(colors)
                await table_client.create_entity(entity=e)


    async def sample_query_entities(self):
        await self._insert_random_entities()
        from azure.data.tables.aio import TableClient
        from azure.core.exceptions import HttpResponseError

        table_client = TableClient.from_connection_string(self.connection_string, self.table_name)
        # [START query_entities]
        async with table_client:
            try:
                entity_name = "marker"
                name_filter = "Name eq '{}'".format(entity_name)

                async for entity_chosen in table_client.query_entities(filter=name_filter, select=["Brand","Color"]):
                    print(entity_chosen)

            except HttpResponseError as e:
                pass
            # [END query_entities]
            finally:
                await table_client.delete_table()


async def main():
    stq = SampleTablesQuery()
    await stq.sample_query_entities()


if __name__ == '__main__':
    asyncio.run(main())
