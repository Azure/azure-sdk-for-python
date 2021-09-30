# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
FILE: sample_single_log_query_without_pandas.py
DESCRIPTION:
    This sample demonstrates authenticating the LogsQueryClient and querying a single query
    and handling a query response without using pandas.
USAGE:
    python sample_single_log_query_without_pandas.py
    Set the environment variables with your own values before running the sample:
    1) LOGS_WORKSPACE_ID - The first (primary) workspace ID.

    In order to use the DefaultAzureCredential, the following environment variables must be set:
    1) AZURE_CLIENT_ID - The client ID of a user-assigned managed identity.
    2) AZURE_TENANT_ID - Tenant ID to use when authenticating a user.
    3) AZURE_CLIENT_ID - The client secret to be used for authentication.
"""
import os
from datetime import timedelta
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential

credential  = DefaultAzureCredential()

client = LogsQueryClient(credential)

query= """AppRequests | take 5"""


try:
    response = client.query_workspace(os.environ['LOG_WORKSPACE_ID'], query, timespan=timedelta(days=1))
    if response.status == LogsQueryStatus.PARTIAL:
        # handle error here
        error = response.partial_error
        data = response.partial_data
        print(error.message)
    elif response.status == LogsQueryStatus.SUCCESS:
        data = response.tables
    for table in data:
        for col in table.columns:
            print(col + "    ", end="")
        for row in table.rows:
            for item in row:
                print(item, end="")
            print('\n')
except HttpResponseError as err:
    print("something fatal happened")
    print (err)
