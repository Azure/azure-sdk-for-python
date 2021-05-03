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

response = client.batch_query("640bfb1c-9109-4569-8a1b-4d9c92cc0eb2", ["AppRequests | take 2", "AppRequests | take 3"])

for r in response:
    print(response)