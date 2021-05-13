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

from dotenv import find_dotenv, load_dotenv


class QueryTables(object):
    def __init__(self):
        load_dotenv(find_dotenv())

    def tables_in_account(self):
        import os

        from azure.data.tables import TableServiceClient

        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        endpoint = "{}.table.{}".format(account_name, endpoint_suffix)
        connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            account_name, access_key, endpoint_suffix
        )
        table_name = "SampleQueryTables"

        # Instantiate the TableServiceClient from a connection string
        with TableServiceClient.from_connection_string(conn_str=connection_string) as table_service:

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
                    print("\t{}".format(table.name))
                # [END tsc_list_tables]

                # [START tsc_query_tables]
                table_name = "mytable1"
                name_filter = "TableName eq '{}'".format(table_name)
                queried_tables = table_service.query_tables(name_filter)

                print("Queried_tables")
                for table in queried_tables:
                    print("\t{}".format(table.name))
                # [END tsc_query_tables]

            finally:
                # [START tsc_delete_table]
                self.delete_tables()
                # [END tsc_delete_table]

    def delete_tables(self):
        import os

        from azure.data.tables import TableServiceClient

        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            account_name, access_key, endpoint_suffix
        )

        with TableServiceClient.from_connection_string(conn_str=connection_string) as ts:
            tables = ["mytable1", "mytable2"]
            for table in tables:
                try:
                    ts.delete_table(table_name=table)
                except:
                    pass


if __name__ == "__main__":
    sample = QueryTables()
    sample.delete_tables()
    sample.tables_in_account()
