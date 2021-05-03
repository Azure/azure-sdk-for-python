# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
from azure.monitor.query import LogQueryClient, LogQueryRequest
from azure.identity import ClientSecretCredential


credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )

client = LogQueryClient(credential)

requests = [
    LogQueryRequest(
        body= {
            "query": "AzureActivity | summarize count()",
            "timespan": "PT1H"
        },
        workspace= os.environ['LOG_WORKSPACE_ID']
    ),
    LogQueryRequest(
        body= {
            "query": "AzureActivity | summarize count()",
            "timespan": "PT1H"
        },
        workspace= os.environ['LOG_WORKSPACE_ID']
    ),
]
response = client.batch_query(requests)

print(response)
