# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import pandas as pd
from azure.monitor.query import LogsClient, LogsQueryRequest
from azure.identity import ClientSecretCredential


credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )

client = LogsClient(credential)

requests = [
    LogsQueryRequest(
        query="AzureActivity | summarize count()",
        timespan="PT1H",
        workspace= os.environ['LOG_WORKSPACE_ID']
    ),
    LogsQueryRequest(
        query= """AppRequests | take 10  |
            summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId""",
        timespan="PT1H",
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
    if not body.tables:
        print("Something is wrong")
    else:
        for table in body.tables:
            df = pd.DataFrame(table.rows, columns=[col.name for col in table.columns])
            print(df)