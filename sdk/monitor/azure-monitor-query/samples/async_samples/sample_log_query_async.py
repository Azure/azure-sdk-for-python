# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
FILE: sample_logs_single_query_async.py
DESCRIPTION:
    This sample demonstrates authenticating the LogsQueryClient and executing a single
    Kusto query.
USAGE:
    python sample_logs_single_query_async.py
    Set the environment variables with your own values before running the sample:
    1) LOGS_WORKSPACE_ID - The first (primary) workspace ID.

This example uses DefaultAzureCredential, which requests a token from Azure Active Directory.
For more information on DefaultAzureCredential, see https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#defaultazurecredential.

**Note** - Although this example uses pandas to print the response, it's optional and
isn't a required package for querying. Alternatively, native Python can be used as well.
"""
import asyncio

# [START send_logs_query_async]
from datetime import timedelta
import os

from azure.core.exceptions import HttpResponseError
from azure.identity.aio import DefaultAzureCredential
from azure.monitor.query.aio import LogsQueryClient
from azure.monitor.query import LogsQueryStatus
import pandas as pd


async def logs_query():
    credential = DefaultAzureCredential()
    client = LogsQueryClient(credential)

    query = "AppRequests | take 5"

    async with client:
        try:
            response = await client.query_workspace(os.environ["LOGS_WORKSPACE_ID"], query, timespan=timedelta(days=1))
            if response.status == LogsQueryStatus.SUCCESS:
                data = response.tables
            else:
                # LogsQueryPartialResult - handle error here
                error = response.partial_error
                data = response.partial_data
                print(error)
            for table in data:
                df = pd.DataFrame(data=table.rows, columns=table.columns)
                print(df)
        except HttpResponseError as err:
            print("something fatal happened")
            print(err)
    await credential.close()


# [END send_logs_query_async]

if __name__ == "__main__":
    asyncio.run(logs_query())
