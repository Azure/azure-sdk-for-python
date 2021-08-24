# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import pandas as pd
from datetime import timedelta
from azure.monitor.query import LogsQueryClient
from azure.identity import DefaultAzureCredential

# [START client_auth_with_token_cred]
credential  = DefaultAzureCredential()

client = LogsQueryClient(credential)
# [END client_auth_with_token_cred]

# Response time trend 
# request duration over the last 12 hours. 
# [START send_logs_query]
query = """AppRequests |
summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId"""

# returns LogsQueryResult 
response = client.query(os.environ['LOG_WORKSPACE_ID'], query, timespan=timedelta(days=1))

if not response.tables:
    print("No results for the query")

for table in response.tables:
    try:
        df = pd.DataFrame(table.rows, columns=table.columns)
        print(df)
    except TypeError:
        print(response.error)
# [END send_logs_query]
"""
    TimeGenerated                                        _ResourceId          avgRequestDuration
0   2021-05-27T08:40:00Z  /subscriptions/faa080af-c1d8-40ad-9cce-e1a450c...  27.307699999999997
1   2021-05-27T08:50:00Z  /subscriptions/faa080af-c1d8-40ad-9cce-e1a450c...            18.11655
2   2021-05-27T09:00:00Z  /subscriptions/faa080af-c1d8-40ad-9cce-e1a450c...             24.5271
"""
