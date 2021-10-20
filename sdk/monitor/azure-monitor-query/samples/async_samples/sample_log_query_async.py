# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
FILE: sample_logs_single_query_async.py
DESCRIPTION:
    This sample demonstrates authenticating the LogsQueryClient and querying a single query.
USAGE:
    python sample_logs_single_query_async.py
    Set the environment variables with your own values before running the sample:
    1) LOGS_WORKSPACE_ID - The first (primary) workspace ID.

    In order to use the DefaultAzureCredential, the following environment variables must be set:
    1) AZURE_CLIENT_ID - The client ID of a user-assigned managed identity.
    2) AZURE_TENANT_ID - Tenant ID to use when authenticating a user.
    3) AZURE_CLIENT_ID - The client secret to be used for authentication.

**Note** - Although this example uses pandas to prin the response, it is totally optional and is
not a required package for querying. Alternatively, native python can be used as well.
"""
import asyncio
import os
import pandas as pd
from datetime import timedelta
from azure.monitor.query.aio import LogsQueryClient
from azure.monitor.query import LogsQueryStatus
from azure.core.exceptions import HttpResponseError
from azure.identity.aio import DefaultAzureCredential

async def logs_query():
    credential  = DefaultAzureCredential()

    client = LogsQueryClient(credential)

    query= """AppRequests | take 5"""

    try:
        response = await client.query_workspace(os.environ['LOG_WORKSPACE_ID'], query, timespan=timedelta(days=1))
        if response.status == LogsQueryStatus.PARTIAL:
            error = response.partial_error
            data = response.partial_data
            print(error.message)
        elif response.status == LogsQueryStatus.SUCCESS:
            data = response.tables
        for table in data:
            df = pd.DataFrame(data=table.rows, columns=table.columns)
            print(df)
    except HttpResponseError as err:
        print("something fatal happened")
        print (err)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(logs_query())