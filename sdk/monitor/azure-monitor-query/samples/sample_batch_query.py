# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from datetime import datetime, timedelta
import os
import pandas as pd
from azure.monitor.query import LogsQueryClient, LogsBatchQuery
from azure.identity import DefaultAzureCredential


credential  = DefaultAzureCredential()

client = LogsQueryClient(credential)

# [START send_query_batch]
requests = [
    LogsBatchQuery(
        query="AzureActivity | summarize count()",
        timespan=timedelta(hours=1),
        workspace_id= os.environ['LOG_WORKSPACE_ID']
    ),
    LogsBatchQuery(
        query= """AppRequestsss | take 10""",
        timespan=(datetime(2021, 6, 2), timedelta(days=1)),
        workspace_id= os.environ['LOG_WORKSPACE_ID']
    ),
    LogsBatchQuery(
        query= """let Weight = 92233720368547758;
        range x from 1 to 3 step 1
        | summarize percentilesw(x, Weight * 100, 50)""",
        workspace_id= os.environ['LOG_WORKSPACE_ID'],
        timespan=(datetime(2021, 6, 2), datetime(2021, 6, 3)),
        include_statistics=True
    ),
]
responses = client.query_batch(requests, allow_partial_errors=True)

for response in responses:
    if not response.is_error:
        table = response.tables[0]
        df = pd.DataFrame(table.rows, columns=table.columns)
        print(df)
        print("\n\n-------------------------\n\n")
    else:
        error = response
        print(error.innererror.message)


# [END send_query_batch]