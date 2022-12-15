# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
FILE: sample_logs_single_query_partial_result.py
DESCRIPTION:
    This sample demonstrates authenticating the LogsQueryClient and querying a single query
    and handling a partial query response.
USAGE:
    python sample_logs_single_query_partial_result.py
    Set the environment variables with your own values before running the sample:
    1) LOGS_WORKSPACE_ID - The first (primary) workspace ID.

This example uses DefaultAzureCredential, which requests a token from Azure Active Directory.
For more information on DefaultAzureCredential, see https://docs.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#defaultazurecredential.

**Note** - Although this example uses pandas to print the response, it's optional and
isn't a required package for querying. Alternatively, native Python can be used as well.
"""
import os
import pandas as pd
from datetime import timedelta
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()

client = LogsQueryClient(credential)

query= """let Weight = 92233720368547758;
            range x from 1 to 3 step 1
            | summarize percentilesw(x, Weight * 100, 50)"""


# this block of code is exactly the same whether the expected result is a success, a failure or a
# partial success
try:
    response = client.query_workspace(os.environ['LOGS_WORKSPACE_ID'], query, timespan=timedelta(days=1))
    if response.status == LogsQueryStatus.PARTIAL:
        # handle error here
        error = response.partial_error
        data = response.partial_data
        print(error)
    elif response.status == LogsQueryStatus.SUCCESS:
        data = response.tables

    for table in data:
        df = pd.DataFrame(data=table.rows, columns=table.columns)
        print(df)
except HttpResponseError as err:
    print("something fatal happened")
    print (err)

"""
    TimeGenerated                                        _ResourceId          avgRequestDuration
0   2021-05-27T08:40:00Z  /subscriptions/faa080af-c1d8-40ad-9cce-e1a450c...  27.307699999999997
1   2021-05-27T08:50:00Z  /subscriptions/faa080af-c1d8-40ad-9cce-e1a450c...            18.11655
2   2021-05-27T09:00:00Z  /subscriptions/faa080af-c1d8-40ad-9cce-e1a450c...             24.5271
"""
