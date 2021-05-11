# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
from datetime import timedelta
from azure.monitor.query import LogsClient
from azure.identity import ClientSecretCredential


credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )

client = LogsClient(credential)

response = client.query(
    os.environ['LOG_WORKSPACE_ID'],
    "AppRequests | take 1",
    timeout=100,
    )

print(response)