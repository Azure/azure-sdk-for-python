# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_query_tables_async.py

DESCRIPTION:
    These samples demonstrate the following: listing and querying all Tables within
    a storage account.

USAGE:
    python sample_query_tables_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

import os
import asyncio

class QueryTables(object):
    connection_string = os.getenv("AZURE_TABLES_CONNECTION_STRING")
    table_name = "OfficeSupplies"

    async def tables_in_account(self):
        # Instantiate the TableServiceClient from a connection string
        from azure.data.tables.aio import TableServiceClient
        table_service = TableServiceClient.from_connection_string(conn_str=self.connection_string)

        async with table_service:
            await table_service.create_table("mytable1")
            await table_service.create_table("mytable2")

            try:
                # [START tsc_list_tables]
                # List all the tables in the service
                print("Listing tables:")
                async for table in table_service.list_tables():
                    print("\t{}".format(table.table_name))
                # [END tsc_list_tables]

                # [START tsc_query_tables]
                # Query for "table1" in the tables created
                table_name = "mytable1"
                name_filter = "TableName eq '{}'".format(table_name)
                print("Queried_tables")
                async for table in table_service.query_tables(filter=name_filter):
                    print("\t{}".format(table.table_name))
                # [END tsc_query_tables]

            finally:
                await self.delete_tables()

    async def delete_tables(self):
        from azure.data.tables.aio import TableServiceClient
        ts = TableServiceClient.from_connection_string(conn_str=self.connection_string)
        async with ts:
            tables = ["mytable1", "mytable2"]
            for table in tables:
                try:
                    await ts.delete_table(table_name=table)
                except:
                    pass


async def main():
    sample = QueryTables()
    await sample.delete_tables()
    await sample.tables_in_account()


if __name__ == '__main__':
    asyncio.run(main())
