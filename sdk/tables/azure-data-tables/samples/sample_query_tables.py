# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_query_tables.py

DESCRIPTION:
    These samples demonstrate the following: listing and querying all Tables within
    a storage account.

USAGE:
    python sample_query_tables.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

import os


class QueryTables(object):
    connection_string = os.getenv("AZURE_TABLES_CONNECTION_STRING")
    table_name = "OfficeSupplies"

    def tables_in_account(self):
        # Instantiate the TableServiceClient from a connection string
        from azure.data.tables import TableServiceClient
        table_service = TableServiceClient.from_connection_string(conn_str=self.connection_string)

        # [START tsc_create_table]
        table_service.create_table("mytable1")
        table_service.create_table("mytable2")
        # [END tsc_create_table]

        try:
            # [START tsc_list_tables]
            # List all the tables in the service
            list_tables = table_service.list_tables()
            print("Listing tables:")
            for table in list_tables:
                print("\t{}".format(table.table_name))
            # [END tsc_list_tables]

            # [START tsc_query_tables]
            table_name = "mytable1"
            name_filter = "TableName eq '{}'".format(table_name)
            queried_tables = table_service.query_tables(filter=name_filter)

            print("Queried_tables")
            for table in queried_tables:
                print("\t{}".format(table.table_name))
            # [END tsc_query_tables]

        finally:
            # [START tsc_delete_table]
            self.delete_tables()
            # [END tsc_delete_table]

    def delete_tables(self):
        from azure.data.tables import TableServiceClient
        ts = TableServiceClient.from_connection_string(conn_str=self.connection_string)
        tables = ["mytable1", "mytable2"]
        for table in tables:
            try:
                ts.delete_table(table_name=table)
            except:
                pass

if __name__ == '__main__':
    sample = QueryTables()
    sample.delete_tables()
    sample.tables_in_account()
