# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: table_samples_service.py

DESCRIPTION:
    These samples demonstrate the following: setting and getting table service properties,
    listing the tables in the service, and getting a TableClient from a TableServiceClient.

USAGE:
    python table_samples_service.py

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

        # [START tsc_create_table]
        await table_service.create_table("mytable1")
        await table_service.create_table("mytable2")
        await table_service.create_table("mytable3")
        await table_service.create_table("table4")
        await table_service.create_table("table5")
        # [END tsc_create_table]

        try:
            # [START tsc_list_tables]
            # List all the tables in the service
            list_tables = table_service.list_tables()
            print("Listing tables:")
            for table in list_tables:
                print("\t{}".format(table.table_name))

            # Query for "table4" in the tables created
            table_name = "mytable1"
            name_filter = "TableName eq '{}'".format(table_name)
            queried_tables = table_service.query_tables(filter=name_filter, results_per_page=10)

            print("Queried_tables")
            for table in queried_tables:
                print("\t{}".format(table.table_name))
            # [END tsc_list_tables]

        finally:
            # [START tsc_delete_table]
            await self.delete_tables()
            # [END tsc_delete_table]

    async def delete_tables(self):
        from azure.data.tables.aio import TableServiceClient
        ts = TableServiceClient.from_connection_string(conn_str=self.connection_string)
        tables = ["mytable1", "mytable2", "mytable3", "table4", "table5"]
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
