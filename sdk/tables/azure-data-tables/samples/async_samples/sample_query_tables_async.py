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
    1) TABLES_STORAGE_ENDPOINT_SUFFIX - the Table service account URL suffix
    2) TABLES_STORAGE_ACCOUNT_NAME - the name of the storage account
    3) TABLES_PRIMARY_STORAGE_ACCOUNT_KEY - the storage account access key
"""

import asyncio
import os
from dotenv import find_dotenv, load_dotenv


class QueryTables(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        self.endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        self.account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        self.endpoint = "{}.table.{}".format(self.account_name, self.endpoint_suffix)
        self.connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            self.account_name, self.access_key, self.endpoint_suffix
        )

    async def tables_in_account(self):
        # Instantiate the TableServiceClient from a connection string
        from azure.data.tables.aio import TableServiceClient

        table_service = TableServiceClient.from_connection_string(conn_str=self.connection_string)

        async with table_service:
            await table_service.create_table("mytableasync1")
            await table_service.create_table("mytableasync2")

            try:
                # [START tsc_list_tables]
                # List all the tables in the service
                print("Listing tables:")
                async for table in table_service.list_tables():
                    print("\t{}".format(table.name))
                # [END tsc_list_tables]

                # [START tsc_query_tables]
                # Query for "table1" in the tables created
                table_name = "mytableasync1"
                name_filter = "TableName eq '{}'".format(table_name)
                print("Queried_tables")
                async for table in table_service.query_tables(name_filter):
                    print("\t{}".format(table.name))
                # [END tsc_query_tables]

            finally:
                await self.delete_tables()

    async def delete_tables(self):
        from azure.data.tables.aio import TableServiceClient

        ts = TableServiceClient.from_connection_string(conn_str=self.connection_string)
        async with ts:
            tables = ["mytableasync1", "mytableasync2"]
            for table in tables:
                try:
                    await ts.delete_table(table_name=table)
                except:
                    pass

    async def clean_up(self):
        from azure.data.tables.aio import TableServiceClient

        tsc = TableServiceClient.from_connection_string(self.connection_string)
        async with tsc:
            async for table in tsc.list_tables():
                await tsc.delete_table(table.name)

            print("Cleaned up")


async def main():
    sample = QueryTables()
    await sample.delete_tables()
    await sample.tables_in_account()
    await sample.clean_up()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
