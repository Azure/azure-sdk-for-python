# Azure Monitor Query client library for Python

The Azure Monitor Query client library is used to execute read-only queries against [Azure Monitor][azure_monitor_overview]'s two data platforms:

- [Logs](https://learn.microsoft.com/azure/azure-monitor/logs/data-platform-logs) - Collects and organizes log and performance data from monitored resources. Data from different sources such as platform logs from Azure services, log and performance data from virtual machines agents, and usage and performance data from apps can be consolidated into a single [Azure Log Analytics workspace](https://learn.microsoft.com/azure/azure-monitor/logs/data-platform-logs#log-analytics-and-workspaces). The various data types can be analyzed together using the [Kusto Query Language][kusto_query_language].
- [Metrics](https://learn.microsoft.com/azure/azure-monitor/essentials/data-platform-metrics) - Collects numeric data from monitored resources into a time series database. Metrics are numerical values that are collected at regular intervals and describe some aspect of a system at a particular time. Metrics are lightweight and capable of supporting near real-time scenarios, making them useful for alerting and fast detection of issues.

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

- Python 3.8 or later
- An [Azure subscription][azure_subscription]
- A [TokenCredential](https://learn.microsoft.com/python/api/azure-core/azure.core.credentials.tokencredential?view=azure-python) implementation, such as an [Azure Identity library credential type](https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes).
- To query Logs, you need one of the following things:
  - An [Azure Log Analytics workspace][azure_monitor_create_using_portal]
  - An Azure resource of any kind (Storage Account, Key Vault, Cosmos DB, etc.)
- To query Metrics, you need an Azure resource of any kind (Storage Account, Key Vault, Cosmos DB, etc.).

### Install the package

Install the Azure Monitor Query client library for Python with [pip][pip]:

```bash
pip install azure-monitor-query
```

### Create the client

An authenticated client is required to query Logs or Metrics. The library includes both synchronous and asynchronous forms of the clients. To authenticate, create an instance of a token credential. Use that instance when creating a `LogsQueryClient`, `MetricsQueryClient`, or `MetricsClient`. The following examples use `DefaultAzureCredential` from the [azure-identity](https://pypi.org/project/azure-identity/) package.

#### Synchronous clients

Consider the following example, which creates synchronous clients for both Logs and Metrics querying:

```python
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient, MetricsQueryClient, MetricsClient

credential = DefaultAzureCredential()
logs_query_client = LogsQueryClient(credential)
metrics_query_client = MetricsQueryClient(credential)
metrics_client = MetricsClient("https://<regional endpoint>", credential)
```

#### Asynchronous clients

The asynchronous forms of the query client APIs are found in the `.aio`-suffixed namespace. For example:

```python
from azure.identity.aio import DefaultAzureCredential
from azure.monitor.query.aio import LogsQueryClient, MetricsQueryClient, MetricsClient

credential = DefaultAzureCredential()
async_logs_query_client = LogsQueryClient(credential)
async_metrics_query_client = MetricsQueryClient(credential)
async_metrics_client = MetricsClient("https://<regional endpoint>", credential)
```

#### Configure client for Azure sovereign cloud

By default, all clients are configured to use the Azure public cloud. To use a sovereign cloud, provide the correct `endpoint` argument when using `LogsQueryClient` or `MetricsQueryClient`. For `MetricsClient`, provide the correct `audience` argument instead. For example:

```python
from azure.identity import AzureAuthorityHosts, DefaultAzureCredential
from azure.monitor.query import LogsQueryClient, MetricsQueryClient, MetricsClient

# Authority can also be set via the AZURE_AUTHORITY_HOST environment variable.
credential = DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_GOVERNMENT)

logs_query_client = LogsQueryClient(credential, endpoint="https://api.loganalytics.us/v1")
metrics_query_client = MetricsQueryClient(credential, endpoint="https://management.usgovcloudapi.net")
metrics_client = MetricsClient(
    "https://usgovvirginia.metrics.monitor.azure.us", credential, audience="https://metrics.monitor.azure.us"
)
```

**Note**: Currently, `MetricsQueryClient` uses the Azure Resource Manager (ARM) endpoint for querying metrics. You need the corresponding management endpoint for your cloud when using this client. This detail is subject to change in the future.

### Execute the query

For examples of Logs and Metrics queries, see the [Examples](#examples) section.

## Key concepts

### Logs query rate limits and throttling

The Log Analytics service applies throttling when the request rate is too high. Limits, such as the maximum number of rows returned, are also applied on the Kusto queries. For more information, see [Query API](https://learn.microsoft.com/azure/azure-monitor/service-limits#la-query-api).

If you're executing a batch logs query, a throttled request returns a `LogsQueryError` object. That object's `code` value is `ThrottledError`.

### Metrics data structure

Each set of metric values is a time series with the following characteristics:

- The time the value was collected
- The resource associated with the value
- A namespace that acts like a category for the metric
- A metric name
- The value itself
- Some metrics have multiple dimensions as described in multi-dimensional metrics. Custom metrics can have up to 10 dimensions.

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
- [Metrics query](#metrics-query)
  - [Handle metrics query response](#handle-metrics-query-response)
  - [Example of handling response](#example-of-handling-response)
  - [Query metrics for multiple resources](#query-metrics-for-multiple-resources)

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

### Metrics query

The following example gets metrics for an Event Grid subscription. The resource ID (also known as resource URI) is that of an Event Grid topic.

The resource ID must be that of the resource for which metrics are being queried. It's normally of the format `/subscriptions/<id>/resourceGroups/<rg-name>/providers/<source>/topics/<resource-name>`.

To find the resource ID/URI:

1. Navigate to your resource's page in the Azure portal.
1. Select the **JSON View** link in the **Overview** section.
1. Copy the value in the **Resource ID** text box at the top of the JSON view.

**NOTE**: The metrics are returned in the order of the `metric_names` sent.

```python
import os
from datetime import timedelta, datetime
from azure.monitor.query import MetricsQueryClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = MetricsQueryClient(credential)
start_time = datetime(2021, 5, 25)
duration = timedelta(days=1)
metrics_uri = os.environ['METRICS_RESOURCE_URI']
response = client.query_resource(
    metrics_uri,
    metric_names=["PublishSuccessCount"],
    timespan=(start_time, duration)
    )

for metric in response.metrics:
    print(metric.name)
    for time_series_element in metric.timeseries:
        for metric_value in time_series_element.data:
            print(metric_value.time_stamp)
```

#### Handle metrics query response

The metrics query API returns a `MetricsQueryResult` object. The `MetricsQueryResult` object contains properties such as a list of `Metric`-typed objects, `granularity`, `namespace`, and `timespan`. The `Metric` objects list can be accessed using the `metrics` param. Each `Metric` object in this list contains a list of `TimeSeriesElement` objects. Each `TimeSeriesElement` object contains `data` and `metadata_values` properties. In visual form, the object hierarchy of the response resembles the following structure:

```
MetricsQueryResult
|---granularity
|---timespan
|---cost
|---namespace
|---resource_region
|---metrics (list of `Metric` objects)
    |---id
    |---type
    |---name
    |---unit
    |---timeseries (list of `TimeSeriesElement` objects)
        |---metadata_values
        |---data (list of data points represented by `MetricValue` objects)
```

#### Example of handling response

```python
import os
from azure.monitor.query import MetricsQueryClient, MetricAggregationType
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = MetricsQueryClient(credential)

metrics_uri = os.environ['METRICS_RESOURCE_URI']
response = client.query_resource(
    metrics_uri,
    metric_names=["MatchedEventCount"],
    aggregations=[MetricAggregationType.COUNT]
    )

for metric in response.metrics:
    print(metric.name)
    for time_series_element in metric.timeseries:
        for metric_value in time_series_element.data:
            if metric_value.count != 0:
                print(
                    "There are {} matched events at {}".format(
                        metric_value.count,
                        metric_value.time_stamp
                    )
                )
```

#### Query metrics for multiple resources

To query metrics for multiple Azure resources in a single request, use the `query_resources` method of `MetricsClient`. This method:

- Calls a different API than the `MetricsQueryClient` methods.
- Requires a regional endpoint when creating the client. For example, "https://westus3.metrics.monitor.azure.com".

Each Azure resource must reside in:

- The same region as the endpoint specified when creating the client.
- The same Azure subscription.

Furthermore:

- The user must be authorized to read monitoring data at the Azure subscription level. For example, the [Monitoring Reader role](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles/monitor#monitoring-reader) on the subscription to be queried.
- The metric namespace containing the metrics to be queried must be provided. For a list of metric namespaces, see [Supported metrics and log categories by resource type][metric_namespaces].

```python
from datetime import timedelta
import os

from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.monitor.query import MetricsClient, MetricAggregationType

endpoint = "https://westus3.metrics.monitor.azure.com"
credential = DefaultAzureCredential()
client = MetricsClient(endpoint, credential)

resource_ids = [
    "/subscriptions/<id>/resourceGroups/<rg-name>/providers/<source>/storageAccounts/<resource-name-1>",
    "/subscriptions/<id>/resourceGroups/<rg-name>/providers/<source>/storageAccounts/<resource-name-2>"
]

response = client.query_resources(
    resource_ids=resource_ids,
    metric_namespace="Microsoft.Storage/storageAccounts",
    metric_names=["Ingress"],
    timespan=timedelta(hours=2),
    granularity=timedelta(minutes=5),
    aggregations=[MetricAggregationType.AVERAGE],
)

for metrics_query_result in response:
    print(metrics_query_result.timespan)
```

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

#### Metrics query samples

- [Send a query using MetricsQueryClient](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_metrics_query.py) ([async sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/async_samples/sample_metrics_query_async.py))
- [Send a query to multiple resources in a region and subscription using MetricsClient](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_metrics_query_multiple.py) ([async sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/async_samples/sample_metrics_query_multiple_async.py))
- [Get a list of metric namespaces](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_metric_namespaces.py) ([async sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/async_samples/sample_metric_namespaces_async.py))
- [Get a list of metric definitions](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_metric_definitions.py) ([async sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/async_samples/sample_metric_definitions_async.py))

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
[metric_namespaces]: https://learn.microsoft.com/azure/azure-monitor/reference/supported-metrics/metrics-index#supported-metrics-and-log-categories-by-resource-type
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
