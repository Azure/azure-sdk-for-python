# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
from azure.monitor.query import LogQueryClient
from azure.identity import ClientSecretCredential


credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )

client = LogQueryClient(credential)

# Response time trend 
# request duration over the last 12 hours. 
query = """AppRequests | 
where TimeGenerated > ago(12h) | 
summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId"""

response = client.query("640bfb1c-9109-4569-8a1b-4d9c92cc0eb2", query)

for item in response.tables:
    print(item.rows,len(item.rows))
    print("\n\n\n\n\n\n")
