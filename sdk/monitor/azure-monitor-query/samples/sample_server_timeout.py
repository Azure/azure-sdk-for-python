# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import pandas as pd
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
    "Perf | summarize count() by bin(TimeGenerated, 4h) | render barchart title='24H Perf events'",
    server_timeout=10,
    include_statistics=True,
    include_render=True
    )

for table in response.tables:
    df = pd.DataFrame(table.rows, columns=[col.name for col in table.columns])
    print(df)