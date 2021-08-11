# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import pandas as pd
from azure.monitor.query import LogsQueryClient
from azure.identity import DefaultAzureCredential


credential  = DefaultAzureCredential()

client = LogsQueryClient(credential)

requests = [
    {
        "id": "1",
        "headers": {
            "Content-Type": "application/json"
        },
        "body": {
            "query": "AzureActivity | summarize count()",
            "timespan": "PT1H"
        },
        "method": "POST",
        "path": "/query",
        "workspace": os.environ['LOG_WORKSPACE_ID']
    },
    {
        "id": "2",
        "headers": {
            "Content-Type": "application/json"
        },
        "body": {
            "query": "AzureActivity | summarize count()",
            "timespan": "PT1H"
        },
        "method": "POST",
        "path": "/fakePath",
        "workspace": os.environ['LOG_WORKSPACE_ID']
    }
]
responses = client.query_batch(requests)

for response in responses:
    try:
        table = response.tables[0]
        df = pd.DataFrame(table.rows, columns=[col.name for col in table.columns])
        print(df)
    except TypeError:
        print(response.error)