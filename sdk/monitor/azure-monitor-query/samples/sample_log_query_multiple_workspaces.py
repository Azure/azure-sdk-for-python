# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
FILE: sample_logs_query_multiple_workspaces.py
DESCRIPTION:
    This sample demonstrates authenticating the LogsQueryClient and querying a single query
    on multiple workspaces using the additional_workspaces param.
USAGE:
    python sample_logs_query_multiple_workspaces.py
    Set the environment variables with your own values before running the sample:
    1) LOGS_WORKSPACE_ID - The first (primary) workspace ID.
    2) SECONDARY_WORKSPACE_ID - An additional workspace.

This example uses DefaultAzureCredential, which requests a token from Azure Active Directory.
For more information on DefaultAzureCredential, see https://docs.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#defaultazurecredential.

**Note** - Although this example uses pandas to print the response, it's optional and
isn't a required package for querying. Alternatively, native Python can be used as well.
"""
import os
import pandas as pd
from datetime import timedelta
from azure.monitor.query import LogsQueryClient
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()

client = LogsQueryClient(credential)

query= """AppRequests | take 5"""

try:
    response = client.query_workspace(
        os.environ['LOGS_WORKSPACE_ID'],
        query,
        timespan=timedelta(days=1),
        additional_workspaces=[os.environ['SECONDARY_WORKSPACE_ID']]
        )
    for table in response:
        df = pd.DataFrame(data=table.rows, columns=table.columns)
        print(df)
except HttpResponseError as err:
    print("something fatal happened")
    print (err)
