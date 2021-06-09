# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from datetime import datetime
import os
import pandas as pd
from azure.monitor.query import LogsQueryClient, LogsQueryRequest
from azure.identity import ClientSecretCredential


credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )

client = LogsQueryClient(credential)

# [START send_batch_query]
requests = [
    LogsQueryRequest(
        query="AzureActivity | summarize count()",
        duration="PT1H",
        workspace= os.environ['LOG_WORKSPACE_ID']
    ),
    LogsQueryRequest(
        query= """AppRequests | take 10  |
            summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId""",
        duration="PT1H",
        start_time=datetime(2021, 6, 2),
        workspace= os.environ['LOG_WORKSPACE_ID']
    ),
    LogsQueryRequest(
        query= "AppRequests | take 2",
        workspace= os.environ['LOG_WORKSPACE_ID']
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