# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from datetime import datetime, timedelta
import os
import pandas as pd
from azure.monitor.query import LogsQueryClient, LogsQueryRequest
from azure.identity import DefaultAzureCredential


credential  = DefaultAzureCredential()

client = LogsQueryClient(credential)

# [START send_batch_query]
requests = [
    LogsQueryRequest(
        query="AzureActivity | summarize count()",
        duration=timedelta(hours=1),
        workspace_id= os.environ['LOG_WORKSPACE_ID']
    ),
    LogsQueryRequest(
        query= """AppRequests | take 10  |
            summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId""",
        duration=timedelta(hours=1),
        start_time=datetime(2021, 6, 2),
        workspace_id= os.environ['LOG_WORKSPACE_ID']
    ),
    LogsQueryRequest(
        query= "AppRequests",
        workspace_id= os.environ['LOG_WORKSPACE_ID'],
        include_statistics=True
    ),
]
response = client.batch_query(requests)

for response in response.responses:
    body = response.body
    print(response.id)
    if not body.tables:
        print("Something is wrong")
    else:
        for table in body.tables:
            df = pd.DataFrame(table.rows, columns=[col.name for col in table.columns])
            print(df)

# [END send_batch_query]