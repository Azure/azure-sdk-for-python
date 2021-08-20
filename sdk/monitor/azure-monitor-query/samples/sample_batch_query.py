# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from datetime import datetime, timedelta
import os
import pandas as pd
from azure.monitor.query import LogsQueryClient, LogsBatchQuery
from azure.identity import DefaultAzureCredential


credential  = DefaultAzureCredential()

client = LogsQueryClient(credential)

# [START send_query_batch]
requests = [
    LogsBatchQuery(
        query="AzureActivity | summarize count()",
        duration=timedelta(hours=1),
        workspace_id= os.environ['LOG_WORKSPACE_ID']
    ),
    LogsBatchQuery(
        query= """AppRequests | take 10  |
            summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId""",
        duration=timedelta(hours=1),
        start_time=datetime(2021, 6, 2),
        workspace_id= os.environ['LOG_WORKSPACE_ID']
    ),
    LogsBatchQuery(
        query= "AppRequestss | take 5",
        workspace_id= os.environ['LOG_WORKSPACE_ID'],
        include_statistics=True
    ),
]
responses = client.query_batch(requests)

for response in responses:
    try:
        table = response.tables[0]
        df = pd.DataFrame(table.rows, columns=[col.name for col in table.columns])
        print(df)
    except TypeError:
        print(response.error)

# [END send_query_batch]