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


class TableServiceSamples(object):
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    def table_service_properties(self):
        # Instantiate the TableServiceClient from a connection string
        from azure.table import TableServiceClient
        table_service = TableServiceClient.from_connection_string(conn_str=self.connection_string)

        # [START set_table_service_properties]
        # Create service properties
        from azure.table import TableAnalyticsLogging, Metrics, CorsRule, RetentionPolicy

        # Create logging settings
        logging = TableAnalyticsLogging(read=True, write=True, delete=True,
                                        retention_policy=RetentionPolicy(enabled=True, days=5))

        # Create metrics for requests statistics
        hour_metrics = Metrics(enabled=True, include_apis=True, retention_policy=RetentionPolicy(enabled=True, days=5))
        minute_metrics = Metrics(enabled=True, include_apis=True,
                                 retention_policy=RetentionPolicy(enabled=True, days=5))

        # Create CORS rules
        cors_rule1 = CorsRule(['www.xyz.com'], ['GET'])
        allowed_origins = ['www.xyz.com', "www.ab.com", "www.bc.com"]
        allowed_methods = ['GET', 'PUT']
        max_age_in_seconds = 500
        exposed_headers = ["x-ms-meta-data*", "x-ms-meta-source*", "x-ms-meta-abc", "x-ms-meta-bcd"]
        allowed_headers = ["x-ms-meta-data*", "x-ms-meta-target*", "x-ms-meta-xyz", "x-ms-meta-foo"]
        cors_rule2 = CorsRule(
            allowed_origins,
            allowed_methods,
            max_age_in_seconds=max_age_in_seconds,
            exposed_headers=exposed_headers,
            allowed_headers=allowed_headers
        )

        cors = [cors_rule1, cors_rule2]

        # Set the service properties
        table_service.set_service_properties(logging, hour_metrics, minute_metrics, cors)
        # [END set_table_service_properties]

        # [START get_table_service_properties]
        properties = table_service.get_service_properties()
        # [END get_table_service_properties]

    def tables_in_account(self):
        # Instantiate the TableServiceClient from a connection string
        from azure.table import TableServiceClient
        table_service = TableServiceClient.from_connection_string(conn_str=self.connection_string)

        # [START tsc_create_table]
        table_service.create_table("mytable1")
        # [END tsc_create_table]

        try:
            # [START tsc_list_tables]
            # List all the tables in the service
            list_tables = table_service.query_tables()
            for table in list_tables:
                print(table)

            # List the tables in the service that start with the name "my"
            list_my_tables = table_service.query_tables(select="my")
            for table in list_my_tables:
                print(table)
            # [END tsc_list_tables]

        finally:
            # [START tsc_delete_table]
            table_service.delete_table(table_name="mytable1")
            # [END tsc_delete_table]

    def get_table_client(self):
        # Instantiate the TableServiceClient from a connection string
        from azure.table import TableServiceClient, TableClient
        table_service = TableServiceClient.from_connection_string(conn_str=self.connection_string)

        # [START get_table_client]
        # Get the table client to interact with a specific table
        table = table_service.get_table_client(table="mytable2")
        # [END get_table_client]


if __name__ == '__main__':
    sample = TableServiceSamples()
    sample.table_service_properties()
    sample.tables_in_account()
    sample.get_table_client()
