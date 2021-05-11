# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
from azure.monitor.query import LogsClient, LogQueryRequest
from azure.identity import ClientSecretCredential


credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )

client = LogsClient(credential)

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
            "query": "ApplicationInsights | limit 10",
            "timespan": "PT1H"
        },
        "method": "POST",
        "path": "/fakePath",
        "workspace": os.environ['LOG_WORKSPACE_ID']
    }
]
response = client.batch_query(requests)

print(response)
