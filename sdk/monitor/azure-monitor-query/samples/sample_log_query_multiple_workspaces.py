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

    In order to use the DefaultAzureCredential, the following environment variables must be set:
    1) AZURE_CLIENT_ID - The client ID of a user-assigned managed identity.
    2) AZURE_TENANT_ID - Tenant ID to use when authenticating a user.
    3) AZURE_CLIENT_ID - The client secret to be used for authentication.

**Note** - Although this example uses pandas to prin the response, it is totally optional and is
not a required package for querying. Alternatively, native python can be used as well.
"""
import os
import pandas as pd
from datetime import timedelta
from azure.monitor.query import LogsQueryClient
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential

credential  = DefaultAzureCredential()

client = LogsQueryClient(credential)

query= """AppRequests | take 5"""

try:
    response = client.query_workspace(
        os.environ['LOG_WORKSPACE_ID'],
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
