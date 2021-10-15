# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
FILE: sample_server_timeout.py
DESCRIPTION:
    This sample demostrates how to update a server timeout for a long running query.
USAGE:
    python sample_server_timeout.py
    Set the environment variables with your own values before running the sample:
    1) LOGS_WORKSPACE_ID - The first (primary) workspace ID.

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
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential

credential  = DefaultAzureCredential()

client = LogsQueryClient(credential)

query= "range x from 1 to 10000000000 step 1 | count"

try:
    response = client.query_workspace(
        os.environ['LOG_WORKSPACE_ID'],
        query,
        timespan=timedelta(days=1),
        server_timeout=3
    )
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
