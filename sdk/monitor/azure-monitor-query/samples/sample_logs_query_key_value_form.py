# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import pandas as pd
from datetime import datetime, timedelta
from msrest.serialization import UTC
from azure.monitor.query import LogsQueryClient
from azure.identity import DefaultAzureCredential

credential  = DefaultAzureCredential()
client = LogsQueryClient(credential)

# Response time trend 
# request duration over the last 12 hours. 
query = """AppRequests |
summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId"""

# returns LogsQueryResult 
response = client.query(os.environ['LOG_WORKSPACE_ID'], query, timespan=timedelta(days=1))

try:
    table = response.tables[0]
    df = pd.DataFrame(table.rows, columns=[col.name for col in table.columns])
    key_value = df.to_dict(orient='records')
    print(key_value)
except TypeError:
    print(response.error)

"""
[
    {
        'TimeGenerated': '2021-07-21T04:40:00Z',
        '_ResourceId': '/subscriptions/faa080af....',
        'avgRequestDuration': 19.7987
    },
    {
        'TimeGenerated': '2021-07-21T04:50:00Z',
        '_ResourceId': '/subscriptions/faa08....',
        'avgRequestDuration': 33.9654
    },
    {
        'TimeGenerated': '2021-07-21T05:00:00Z',
        '_ResourceId': '/subscriptions/faa080....',
        'avgRequestDuration': 44.13115
    }
]
"""
