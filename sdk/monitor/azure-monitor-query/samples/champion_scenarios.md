## Azure Monitor Query Champion Scenarios

This document covers the basic champion Scenarios to use the package.

### Authenticate the client

Consider the following example, which creates and authenticates clients for both logs and metrics querying:

```python
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient, MetricsQueryClient

credential = DefaultAzureCredential()
logs_client = LogsQueryClient(credential)
metrics_client = MetricsQueryClient(credential)
```

### Make a simple query to the service

* Each row is converted into a native python data type. For example, time is a datetime object instead of string.

#### Results in tabular form

```python
import os
import pandas as pd
from datetime import timedelta
from azure.monitor.query import LogsQueryClient
from azure.identity import DefaultAzureCredential

def query():
    query = """AppRequests |
    summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId"""

    try:
        response = client.query(os.environ['LOG_WORKSPACE_ID'], query, timespan=timedelta(days=1))
        for table in response:
            df = pd.DataFrame(data=table.rows, columns=table.columns)
            print(df)
    except QueryPartialErrorException as err:
        print("this is a partial error")
    except HttpResponseError as err:
        print("something fatal happened")

if __name__ == '__main__':
    print(query())

"""
    TimeGenerated                                        _ResourceId          avgRequestDuration
0   2021-05-27T08:40:00Z  /subscriptions/<subscription id>...  27.307699999999997
1   2021-05-27T08:50:00Z  /subscriptions/<subscription id>...            18.11655
2   2021-05-27T09:00:00Z  /subscriptions/<subscription id>...             24.5271
"""

```

#### Results in tabular form with partial_error

```python
import os
import pandas as pd
from datetime import timedelta
from azure.monitor.query import LogsQueryClient
from azure.identity import DefaultAzureCredential

def query():
    query = """let Weight = 92233720368547758; range x from 1 to 3 step 1
               | summarize percentilesw(x, Weight * 100, 50)"""
    try:
        response = client.query(
            os.environ['LOG_WORKSPACE_ID'],
            query,
            timespan=timedelta(days=1),
            allow_partial_errors=True
        )
        if response.partial_error:
            # handle LogsQuery Error
        for table in response:
            df = pd.DataFrame(data=table.rows, columns=table.columns)
            print(df)
    except HttpResponseError as err:
        print("something fatal happened")

if __name__ == '__main__':
    print(query())

"""
    TimeGenerated                                        _ResourceId          avgRequestDuration
0   2021-05-27T08:40:00Z  /subscriptions/<subscription id>...  27.307699999999997
1   2021-05-27T08:50:00Z  /subscriptions/<subscription id>...            18.11655
2   2021-05-27T09:00:00Z  /subscriptions/<subscription id>...             24.5271
"""

```


### Run multiple queries in 1 api call

* batch_query returns the results as a list in the same order in which the requests were sent.
* Each item in the result will have an error attribute if there is an error.

#### Results in tabular form

```python
from datetime import datetime, timedelta
import os
import pandas as pd
from azure.monitor.query import LogsQueryClient, LogsBatchQuery
from azure.identity import DefaultAzureCredential


credential  = DefaultAzureCredential()

client = LogsQueryClient(credential)

requests = [
    LogsBatchQuery(
        query="AzureActivity | summarize count()",
        timespan=timedelta(hours=1),
        workspace_id= os.environ['LOG_WORKSPACE_ID']
    ),
    LogsBatchQuery(
        query= """let Weight = 92233720368547758; range x from 1 to 3 step 1 | summarize percentilesw(x, Weight * 100, 50)""",
        timespan=(datetime(2021, 6, 2), timedelta(hours=1)),
        workspace_id= os.environ['LOG_WORKSPACE_ID']
    ),
    LogsBatchQuery(
        query= """This is a bad query""",
        workspace_id= os.environ['LOG_WORKSPACE_ID'],
        timespan=(datetime(2021, 6, 2), datetime(2021, 6, 3)),
    ),
]
results = client.query_batch(requests)

for ind, res in enumerate(results):
    if res.is_error:
        print(ind) # prints 2, 3
        # handle LogsQueryError
        return
    elif not response.is_error:
        print(ind) # prints 1
        # handle table LogsQueryTable
        for table in res: # directly iterates over tables
            for item in table.row: # iterates directly over row type
                print(item)
        print(res.statistics)
        print(res.visualization)
        return


```
#### Results in tabular form with partial_error

```python
from datetime import datetime, timedelta
import os
import pandas as pd
from azure.monitor.query import LogsQueryClient, LogsBatchQuery
from azure.identity import DefaultAzureCredential


credential  = DefaultAzureCredential()

client = LogsQueryClient(credential)

requests = [
    LogsBatchQuery(
        query="AzureActivity | summarize count()",
        timespan=timedelta(hours=1),
        workspace_id= os.environ['LOG_WORKSPACE_ID'],
    ),
    LogsBatchQuery(
        query= """let Weight = 92233720368547758; range x from 1 to 3 step 1 | summarize percentilesw(x, Weight * 100, 50)""",
        timespan=(datetime(2021, 6, 2), timedelta(hours=1)),
        workspace_id= os.environ['LOG_WORKSPACE_ID']
    ),
    LogsBatchQuery(
        query= """This is a bad query""",
        workspace_id= os.environ['LOG_WORKSPACE_ID'],
        timespan=(datetime(2021, 6, 2), datetime(2021, 6, 3)),
    ),
]
results = client.query_batch(requests, allow_partial_errors=True)

for ind, res in enumerate(results):
    if res.is_error:
        print(ind) # prints 3
        # handle LogsQueryError
        return
    elif not res.is_error:
        print(ind) # prints 1, 2
        if res.partial_error:
            # handle partial error
            print(res.partial_error)
        # handle table LogsQueryTable
        for table in res: # directly iterates over tables
            for item in table.row: # iterates directly over row type
                print(item)
        print(res.statistics)
        print(res.visualization)
        return


```

### Run a complex query to set server timeout for more than 3 minutes.

```python
import os
import pandas as pd
from azure.core.serialization import NULL
from azure.monitor.query import LogsQueryClient
from azure.identity import DefaultAzureCredential


credential  = DefaultAzureCredential()

client = LogsQueryClient(credential)

response = client.query(
    os.environ['LOG_WORKSPACE_ID'],
    "range x from 1 to 10000000000 step 1 | count",
    timespan=NULL, # can pass None too
    server_timeout=600
    )

### results in server timeout
```

### Run a metrics Query

```python
import os
from datetime import timedelta
from azure.monitor.query import MetricsQueryClient, MetricAggregationType
from azure.identity import DefaultAzureCredential

credential  = DefaultAzureCredential()

client = MetricsQueryClient(credential)

metrics_uri = os.environ['METRICS_RESOURCE_URI']
response = client.query(
    metrics_uri,
    metric_names=["Ingress"],
    timespan=timedelta(hours=2),
    granularity=timedelta(minutes=5),
    aggregations=[MetricAggregationType.AVERAGE],
    )

for metric in response.metrics:
    print(metric.name + ' -- ' + metric.display_description)
    for time_series_element in metric.timeseries:
        for metric_value in time_series_element.data:
            print('The ingress at {} is {}'.format(
                metric_value.timestamp,
                metric_value.average
            ))

"""
Ingress -- The amount of ingress data, in bytes. This number includes ingress from an external client into Azure Storage as well as ingress within Azure.
The ingress at 2021-08-23 23:58:00+00:00 is 567.4285714285714 
The ingress at 2021-08-24 00:03:00+00:00 is 812.0
The ingress at 2021-08-24 00:08:00+00:00 is 812.0
The ingress at 2021-08-24 00:13:00+00:00 is 812.0
The ingress at 2021-08-24 00:18:00+00:00 is 812.0
The ingress at 2021-08-24 00:23:00+00:00 is 3623.3333333333335
The ingress at 2021-08-24 00:28:00+00:00 is 1082.75
The ingress at 2021-08-24 00:33:00+00:00 is 1160.6666666666667
The ingress at 2021-08-24 00:38:00+00:00 is 1060.75
The ingress at 2021-08-24 00:43:00+00:00 is 1081.75
The ingress at 2021-08-24 00:48:00+00:00 is 1061.25
The ingress at 2021-08-24 00:53:00+00:00 is 1160.3333333333333
The ingress at 2021-08-24 00:58:00+00:00 is 1082.0
The ingress at 2021-08-24 01:03:00+00:00 is 1628.6666666666667
The ingress at 2021-08-24 01:08:00+00:00 is 794.6666666666666
The ingress at 2021-08-24 01:13:00+00:00 is 1060.25
The ingress at 2021-08-24 01:18:00+00:00 is 1160.0
The ingress at 2021-08-24 01:23:00+00:00 is 1082.0
The ingress at 2021-08-24 01:28:00+00:00 is 1060.5
The ingress at 2021-08-24 01:33:00+00:00 is 1630.0
The ingress at 2021-08-24 01:38:00+00:00 is 795.0
The ingress at 2021-08-24 01:43:00+00:00 is 827.6
The ingress at 2021-08-24 01:48:00+00:00 is 1250.5
The ingress at 2021-08-24 01:53:00+00:00 is 1061.75
"""
```