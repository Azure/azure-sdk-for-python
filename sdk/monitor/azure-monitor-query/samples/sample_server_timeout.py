# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import pandas as pd
from azure.monitor.query import LogsQueryClient
from azure.identity import ClientSecretCredential


credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )

client = LogsQueryClient(credential)

response = client.query(
    os.environ['LOG_WORKSPACE_ID'],
    "range x from 1 to 10000000000 step 1 | count",
    server_timeout=1,
    )

for table in response.tables:
    df = pd.DataFrame(table.rows, columns=[col.name for col in table.columns])
    print(df)