# Azure Monitor Query client library for Python

The Azure Monitor Query client library is used to execute read-only queries against [Azure Monitor][azure_monitor_overview]'s Logs data platform.

- [Logs](https://learn.microsoft.com/azure/azure-monitor/logs/data-platform-logs) - Collects and organizes log and performance data from monitored resources. Data from different sources such as platform logs from Azure services, log and performance data from virtual machines agents, and usage and performance data from apps can be consolidated into a single [Azure Log Analytics workspace](https://learn.microsoft.com/azure/azure-monitor/logs/data-platform-logs#log-analytics-and-workspaces). The various data types can be analyzed together using the [Kusto Query Language][kusto_query_language].

> **Important**: As of version 2.0.0, `MetricsClient` and `MetricsQueryClient` have been removed from the `azure-monitor-query` package. For metrics querying capabilities, please use the separate [`azure-monitor-querymetrics`](https://pypi.org/project/azure-monitor-querymetrics/) package which provides `MetricsClient`, or the [`azure-mgmt-monitor`](https://pypi.org/project/azure-mgmt-monitor/) package. For more details, see the [migration guide](https://aka.ms/azsdk/python/monitor/query/migration).

**Resources:**

- [Source code][source]
- [Package (PyPI)][package]
- [Package (Conda)](https://anaconda.org/microsoft/azure-monitor-query/)
- [API reference documentation][python-query-ref-docs]
- [Service documentation][azure_monitor_overview]
- [Samples][samples]
- [Change log][changelog]

## Getting started

### Prerequisites

- Python 3.9 or later
- An [Azure subscription][azure_subscription]
- To query Logs, you need one of the following things:
  - An [Azure Log Analytics workspace][azure_monitor_create_using_portal]
  - An Azure resource of any kind (Storage Account, Key Vault, Cosmos DB, etc.)

### Install the package

Install the Azure Monitor Query client library for Python with [pip][pip]:

```bash
pip install azure-monitor-query
```

### Create the client

An authenticated client is required to query Logs. The library includes both synchronous and asynchronous forms of the client. To authenticate, create an instance of a token credential. Use that instance when creating a `LogsQueryClient`. The following examples use `DefaultAzureCredential` from the [azure-identity](https://pypi.org/project/azure-identity/) package.

> **Note**: For Metrics querying capabilities, please use the separate `azure-monitor-querymetrics` package which provides `MetricsClient`, or the `azure-mgmt-monitor` package.

#### Synchronous clients

Consider the following example, which creates a synchronous client for Logs querying:

```python
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient

credential = DefaultAzureCredential()
logs_query_client = LogsQueryClient(credential)
```

#### Asynchronous clients

The asynchronous forms of the query client APIs are found in the `.aio`-suffixed namespace. For example:

```python
from azure.identity.aio import DefaultAzureCredential
from azure.monitor.query.aio import LogsQueryClient

credential = DefaultAzureCredential()
async_logs_query_client = LogsQueryClient(credential)
```

To use the asynchronous clients, you must also install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/).

```sh
pip install aiohttp
```

#### Configure client for Azure sovereign cloud

By default, the client is configured to use the Azure public cloud. To use a sovereign cloud, provide the correct `endpoint` argument when using `LogsQueryClient`. For example:

```python
from azure.identity import AzureAuthorityHosts, DefaultAzureCredential
from azure.monitor.query import LogsQueryClient

# Authority can also be set via the AZURE_AUTHORITY_HOST environment variable.
credential = DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_GOVERNMENT)

logs_query_client = LogsQueryClient(credential, endpoint="https://api.loganalytics.us")
```

### Execute the query

For examples of Logs queries, see the [Examples](#examples) section.

## Key concepts

### Logs query rate limits and throttling

The Log Analytics service applies throttling when the request rate is too high. Limits, such as the maximum number of rows returned, are also applied on the Kusto queries. For more information, see [Query API](https://learn.microsoft.com/azure/azure-monitor/service-limits#la-query-api).

If you're executing a batch logs query, a throttled request returns a `LogsQueryError` object. That object's `code` value is `ThrottledError`.

## Examples

- [Logs query](#logs-query)
  - [Resource-centric logs query](#resource-centric-logs-query)
  - [Specify timespan](#specify-timespan)
  - [Handle logs query response](#handle-logs-query-response)
- [Batch logs query](#batch-logs-query)
- [Advanced logs query scenarios](#advanced-logs-query-scenarios)
  - [Set logs query timeout](#set-logs-query-timeout)
  - [Query multiple workspaces](#query-multiple-workspaces)
  - [Include statistics](#include-statistics)
  - [Include visualization](#include-visualization)

### Logs query

This example shows how to query a Log Analytics workspace. To handle the response and view it in a tabular form, the [`pandas`](https://pypi.org/project/pandas/) library is used. See the [samples][samples] if you choose not to use `pandas`.

#### Resource-centric logs query

The following example demonstrates how to query logs directly from an Azure resource without the use of a Log Analytics workspace. Here, the `query_resource` method is used instead of `query_workspace`. Instead of a workspace ID, an Azure resource identifier is passed in. For example, `/subscriptions/{subscription-id}/resourceGroups/{resource-group-name}/providers/{resource-provider}/{resource-type}/{resource-name}`.

```python
import os
import pandas as pd
from datetime import timedelta
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential

credential  = DefaultAzureCredential()
client = LogsQueryClient(credential)

query = """AzureActivity | take 5"""

try:
    response = client.query_resource(os.environ['LOGS_RESOURCE_ID'], query, timespan=timedelta(days=1))
    if response.status == LogsQueryStatus.SUCCESS:
        data = response.tables
    else:
        # LogsQueryPartialResult
        error = response.partial_error
        data = response.partial_data
        print(error)

    for table in data:
        df = pd.DataFrame(data=table.rows, columns=table.columns)
        print(df)
except HttpResponseError as err:
    print("something fatal happened")
    print(err)
```

#### Specify timespan

The `timespan` parameter specifies the time duration for which to query the data. This value can take one of the following forms:

- a `timedelta`
- a `timedelta` and a start `datetime`
- a start `datetime`/end `datetime`

For example:

```python
import os
import pandas as pd
from datetime import datetime, timezone
from azure.monitor.query import LogsQueryClient, LogsQueryResult
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

credential = DefaultAzureCredential()
client = LogsQueryClient(credential)

query = """AppRequests | take 5"""

start_time=datetime(2021, 7, 2, tzinfo=timezone.utc)
end_time=datetime(2021, 7, 4, tzinfo=timezone.utc)

try:
    response = client.query_workspace(
        workspace_id=os.environ['LOG_WORKSPACE_ID'],
        query=query,
        timespan=(start_time, end_time)
        )
    if response.status == LogsQueryStatus.SUCCESS:
        data = response.tables
    else:
        # LogsQueryPartialResult
        error = response.partial_error
        data = response.partial_data
        print(error)

    for table in data:
        df = pd.DataFrame(data=table.rows, columns=table.columns)
        print(df)
except HttpResponseError as err:
    print("something fatal happened")
    print(err)
```

#### Handle logs query response

The `query_workspace` API returns either a `LogsQueryResult` or a `LogsQueryPartialResult` object. The `batch_query` API returns a list that can contain `LogsQueryResult`, `LogsQueryPartialResult`, and `LogsQueryError` objects. Here's a hierarchy of the response:

```
LogsQueryResult
|---statistics
|---visualization
|---tables (list of `LogsTable` objects)
    |---name
    |---rows
    |---columns
    |---columns_types

LogsQueryPartialResult
|---statistics
|---visualization
|---partial_error (a `LogsQueryError` object)
    |---code
    |---message
    |---details
    |---status
|---partial_data (list of `LogsTable` objects)
    |---name
    |---rows
    |---columns
    |---columns_types
```

The `LogsQueryResult` directly iterates over the table as a convenience. For example, to handle a logs query response with tables and display it using `pandas`:

```python
response = client.query(...)
for table in response:
    df = pd.DataFrame(table.rows, columns=[col.name for col in table.columns])
```

A full sample can be found [here](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_logs_single_query.py).

In a similar fashion, to handle a batch logs query response:

```python
for result in response:
    if result.status == LogsQueryStatus.SUCCESS:
        for table in result:
            df = pd.DataFrame(table.rows, columns=table.columns)
            print(df)
```

A full sample can be found [here](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_batch_query.py).

### Batch logs query

The following example demonstrates sending multiple queries at the same time using the batch query API. The queries can either be represented as a list of `LogsBatchQuery` objects or a dictionary. This example uses the former approach.

```python
import os
from datetime import timedelta, datetime, timezone
import pandas as pd
from azure.monitor.query import LogsQueryClient, LogsBatchQuery, LogsQueryStatus
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = LogsQueryClient(credential)
requests = [
    LogsBatchQuery(
        query="AzureActivity | summarize count()",
        timespan=timedelta(hours=1),
        workspace_id=os.environ['LOG_WORKSPACE_ID']
    ),
    LogsBatchQuery(
        query= """bad query""",
        timespan=timedelta(days=1),
        workspace_id=os.environ['LOG_WORKSPACE_ID']
    ),
    LogsBatchQuery(
        query= """let Weight = 92233720368547758;
        range x from 1 to 3 step 1
        | summarize percentilesw(x, Weight * 100, 50)""",
        workspace_id=os.environ['LOG_WORKSPACE_ID'],
        timespan=(datetime(2021, 6, 2, tzinfo=timezone.utc), datetime(2021, 6, 5, tzinfo=timezone.utc)), # (start, end)
        include_statistics=True
    ),
]
results = client.query_batch(requests)

for res in results:
    if res.status == LogsQueryStatus.PARTIAL:
        ## this will be a LogsQueryPartialResult
        print(res.partial_error)
        for table in res.partial_data:
            df = pd.DataFrame(table.rows, columns=table.columns)
            print(df)
    elif res.status == LogsQueryStatus.SUCCESS:
        ## this will be a LogsQueryResult
        table = res.tables[0]
        df = pd.DataFrame(table.rows, columns=table.columns)
        print(df)
    else:
        # this will be a LogsQueryError
        print(res.message)

```

### Advanced logs query scenarios

#### Set logs query timeout

The following example shows setting a server timeout in seconds. A gateway timeout is raised if the query takes more time than the mentioned timeout. The default is 180 seconds and can be set up to 10 minutes (600 seconds).

```python
import os
from datetime import timedelta
from azure.monitor.query import LogsQueryClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = LogsQueryClient(credential)

response = client.query_workspace(
    os.environ['LOG_WORKSPACE_ID'],
    "range x from 1 to 10000000000 step 1 | count",
    timespan=timedelta(days=1),
    server_timeout=600 # sets the timeout to 10 minutes
    )
```

#### Query multiple workspaces

The same logs query can be executed across multiple Log Analytics workspaces. In addition to the Kusto query, the following parameters are required:

- `workspace_id` - The first (primary) workspace ID
- `additional_workspaces` - A list of workspaces, excluding the workspace provided in the `workspace_id` parameter. The parameter's list items can consist of the following identifier formats:
  - Qualified workspace names
  - Workspace IDs
  - Azure resource IDs

For example, the following query executes in three workspaces:

```python
client.query_workspace(
    <workspace_id>,
    query,
    timespan=timedelta(days=1),
    additional_workspaces=['<workspace 2>', '<workspace 3>']
    )
```

A full sample can be found [here](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_log_query_multiple_workspaces.py).

#### Include statistics

To get logs query execution statistics, such as CPU and memory consumption:

1. Set the `include_statistics` parameter to `True`.
1. Access the `statistics` field inside the `LogsQueryResult` object.

The following example prints the query execution time:

```python
query = "AzureActivity | top 10 by TimeGenerated"
result = client.query_workspace(
    <workspace_id>,
    query,
    timespan=timedelta(days=1),
    include_statistics=True
    )

execution_time = result.statistics.get("query", {}).get("executionTime")
print(f"Query execution time: {execution_time}")
```

The `statistics` field is a `dict` that corresponds to the raw JSON response, and its structure can vary by query. The statistics are found within the `query` property. For example:

```python
{
  "query": {
    "executionTime": 0.0156478,
    "resourceUsage": {...},
    "inputDatasetStatistics": {...},
    "datasetStatistics": [{...}]
  }
}
```

#### Include visualization

To get visualization data for logs queries using the [render operator](https://learn.microsoft.com/azure/data-explorer/kusto/query/renderoperator?pivots=azuremonitor):

1. Set the `include_visualization` property to `True`.
1. Access the `visualization` field inside the `LogsQueryResult` object.

For example:

```python
query = (
    "StormEvents"
    "| summarize event_count = count() by State"
    "| where event_count > 10"
    "| project State, event_count"
    "| render columnchart"
)
result = client.query_workspace(
    <workspace_id>,
    query,
    timespan=timedelta(days=1),
    include_visualization=True
    )

print(f"Visualization result: {result.visualization}")
```

The `visualization` field is a `dict` that corresponds to the raw JSON response, and its structure can vary by query. For example:

```python
{
  "visualization": "columnchart",
  "title": "the chart title",
  "accumulate": False,
  "isQuerySorted": False,
  "kind": None,
  "legend": None,
  "series": None,
  "yMin": "NaN",
  "yMax": "NaN",
  "xAxis": None,
  "xColumn": None,
  "xTitle": "x axis title",
  "yAxis": None,
  "yColumns": None,
  "ySplit": None,
  "yTitle": None,
  "anomalyColumns": None
}
```

Interpretation of the visualization data is left to the library consumer. To use this data with the [Plotly graphing library](https://plotly.com/python/), see the [synchronous](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_logs_query_visualization.py) or [asynchronous](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/async_samples/sample_logs_query_visualization_async.py) code samples.

## Troubleshooting

See our [troubleshooting guide][troubleshooting_guide] for details on how to diagnose various failure scenarios.

## Next steps

To learn more about Azure Monitor, see the [Azure Monitor service documentation][azure_monitor_overview].

### Samples

The following code samples show common scenarios with the Azure Monitor Query client library.

#### Logs query samples

- [Send a single query with LogsQueryClient and handle the response as a table](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_logs_single_query.py) ([async sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/async_samples/sample_log_query_async.py))
- [Send a single query with LogsQueryClient and handle the response in key-value form](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_logs_query_key_value_form.py)
- [Send a single query with LogsQueryClient without pandas](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_single_log_query_without_pandas.py)
- [Send a single query with LogsQueryClient across multiple workspaces](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_log_query_multiple_workspaces.py)
- [Send multiple queries with LogsQueryClient](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_batch_query.py)
- [Send a single query with LogsQueryClient using server timeout](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_server_timeout.py)

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repositories using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[azure_core_exceptions]: https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions
[azure_core_ref_docs]: https://aka.ms/azsdk/python/core/docs
[azure_monitor_create_using_portal]: https://learn.microsoft.com/azure/azure-monitor/logs/quick-create-workspace
[azure_monitor_overview]: https://learn.microsoft.com/azure/azure-monitor/
[azure_subscription]: https://azure.microsoft.com/free/python/
[changelog]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-query/CHANGELOG.md
[kusto_query_language]: https://learn.microsoft.com/azure/data-explorer/kusto/query/
[package]: https://aka.ms/azsdk-python-monitor-query-pypi
[pip]: https://pypi.org/project/pip/
[python_logging]: https://docs.python.org/3/library/logging.html
[python-query-ref-docs]: https://aka.ms/azsdk/python/monitor-query/docs
[samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-query/samples
[source]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/
[troubleshooting_guide]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/TROUBLESHOOTING.md

[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
