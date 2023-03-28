# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
FILE: sample_batch_query.py
DESCRIPTION:
    This sample demonstrates querying multiple queries in a batch.
USAGE:
    python sample_batch_query.py
    Set the environment variables with your own values before running the sample:
    1) LOGS_WORKSPACE_ID - The The first (primary) workspace ID.

This example uses DefaultAzureCredential, which requests a token from Azure Active Directory.
For more information on DefaultAzureCredential, see https://docs.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#defaultazurecredential.

**Note** - Although this example uses pandas to print the response, it's optional and
isn't a required package for querying. Alternatively, native Python can be used as well.
"""

from datetime import datetime, timedelta, timezone
import os
import pandas as pd
from azure.monitor.query import LogsQueryClient, LogsBatchQuery, LogsQueryStatus
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()

client = LogsQueryClient(credential)

# [START send_query_batch]
requests = [
    LogsBatchQuery(
        query="AzureActivity | summarize count()",
        timespan=timedelta(hours=1),
        workspace_id= os.environ['LOGS_WORKSPACE_ID']
    ),
    LogsBatchQuery(
        query= """bad query""",
        timespan=timedelta(days=1),
        workspace_id= os.environ['LOGS_WORKSPACE_ID']
    ),
    LogsBatchQuery(
        query= """let Weight = 92233720368547758;
        range x from 1 to 3 step 1
        | summarize percentilesw(x, Weight * 100, 50)""",
        workspace_id= os.environ['LOGS_WORKSPACE_ID'],
        timespan=(datetime(2021, 6, 2, tzinfo=timezone.utc), datetime(2021, 6, 5, tzinfo=timezone.utc)), # (start, end)
        include_statistics=True
    ),
]
results = client.query_batch(requests)

for res in results:
    if res.status == LogsQueryStatus.FAILURE:
        # this will be a LogsQueryError
        print(res)
    elif res.status == LogsQueryStatus.PARTIAL:
        ## this will be a LogsQueryPartialResult
        print(res.partial_error)
        for table in res.partial_data:
            df = pd.DataFrame(table.rows, columns=table.columns)
            print(df)
    elif res.status == LogsQueryStatus.SUCCESS:
        ## this will be a LogsQueryResult
        table = res.tables[0]
        df = pd.DataFrame(table.rows, columns=table.columns)
        print(df)


# [END send_query_batch]
