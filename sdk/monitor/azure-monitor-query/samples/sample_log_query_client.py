# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import pandas as pd
from datetime import datetime
from azure.monitor.query import LogsQueryClient
from azure.identity import ClientSecretCredential

# [START client_auth_with_token_cred]
credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )

client = LogsQueryClient(credential)
# [END client_auth_with_token_cred]

# Response time trend 
# request duration over the last 12 hours. 
# [START send_logs_query]
query = """AppRequests | 
where TimeGenerated > ago(12h) | 
summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId"""

# returns LogsQueryResults 
response = client.query(os.environ['LOG_WORKSPACE_ID'], query, start_time=datetime(2021, 6, 2), end_time=datetime.now())

if not response.tables:
    print("No results for the query")

for table in response.tables:
    df = pd.DataFrame(table.rows, columns=[col.name for col in table.columns])
    print(df)
# [END send_logs_query]
"""
    TimeGenerated                                        _ResourceId          avgRequestDuration
0   2021-05-27T08:40:00Z  /subscriptions/faa080af-c1d8-40ad-9cce-e1a450c...  27.307699999999997
1   2021-05-27T08:50:00Z  /subscriptions/faa080af-c1d8-40ad-9cce-e1a450c...            18.11655
2   2021-05-27T09:00:00Z  /subscriptions/faa080af-c1d8-40ad-9cce-e1a450c...             24.5271
"""

# if you dont want to use pandas - here's how you can process it.

#response.tables is a LogsQueryResultTable
for table in response.tables:
    for col in table.columns: #LogsQueryResultColumn
        print(col.name + "/"+  col.type + " | ", end="")
    print("\n")
    for row in table.rows:
        for item in row:
            print(item + " | ", end="")
        print("\n")


"""
TimeGenerated/datetime | _ResourceId/string | avgRequestDuration/real | 

2021-05-11T08:20:00Z | /subscriptions/<subscription id>/resourcegroups/cobey-azuresdkshinydashboardgrp/providers/microsoft.insights/components/cobey-willthisbestatic | 10.8915 |

2021-05-11T08:30:00Z | /subscriptions/<subscription id>/resourcegroups/cobey-azuresdkshinydashboardgrp/providers/microsoft.insights/components/cobey-willthisbestatic | 33.23276666666667 |

2021-05-11T08:40:00Z | /subscriptions/<subscription id>/resourcegroups/cobey-azuresdkshinydashboardgrp/providers/microsoft.insights/components/cobey-willthisbestatic | 21.83535 |

2021-05-11T08:50:00Z | /subscriptions/<subscription id>/resourcegroups/cobey-azuresdkshinydashboardgrp/providers/microsoft.insights/components/cobey-willthisbestatic | 11.028649999999999 |
"""