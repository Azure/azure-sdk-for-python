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

# Response time trend 
# request duration over the last 12 hours. 
query = """AppRequests | 
where TimeGenerated > ago(12h) | 
summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId"""

# returns LogsQueryResults 
response = client.query(os.environ['LOG_WORKSPACE_ID'], query)

if not response.tables:
    print("No results for the query")


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