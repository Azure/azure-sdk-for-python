# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import pandas as pd
from datetime import datetime
from msrest.serialization import UTC
from azure.monitor.query import LogsQueryClient
from azure.identity import ClientSecretCredential

credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )

client = LogsQueryClient(credential)

# Response time trend 
# request duration over the last 12 hours. 
query = "union * | where TimeGenerated > ago(100d) | project TenantId | summarize count() by TenantId"

end_time = datetime.now(UTC())

# returns LogsQueryResults 
response = client.query(
    os.environ['LOG_WORKSPACE_ID'],
    query,
    additional_workspaces=[os.environ["SECONDARY_WORKSPACE_ID"]],
    )

if not response.tables:
    print("No results for the query")

for table in response.tables:
    df = pd.DataFrame(table.rows, columns=[col.name for col in table.columns])
    print(df)

