# Azure Monitor Query client library for Python

Azure Monitor helps you maximize the availability and performance of your apps. It delivers a comprehensive solution for collecting, analyzing, and acting on telemetry from your cloud and on-premises environments.

All data collected by Azure Monitor fits into one of two fundamental types:

- **Metrics** - Numerical values that describe some aspect of a system at a particular time. They're lightweight and can support near real-time scenarios.
- **Logs** - Disparate types of data organized into records with different sets of properties for each type. Performance data and telemetry such as events, exceptions, and traces are stored as logs.

To programmatically analyze these data sources, the Azure Monitor Query client library can be used.

[Source code][python-query-src] | [Package (PyPI)][python-query-pypi] | [API reference documentation][python-query-ref-docs] | [Product documentation][python-query-product-docs] | [Samples][python-query-samples] | [Changelog][python-query-changelog]

## Getting started

### Prerequisites

- Python 2.7, or 3.6 or later.
- An [Azure subscription][azure_subscription].

### Install the package

Install the Azure Monitor Query client library for Python with [pip][pip]:

```bash
pip install azure-monitor-query --pre
```

### Create the client

To interact with the Azure Monitor service, create an instance of a token credential. Use that instance when creating a `LogsQueryClient` or `MetricsQueryClient`.

#### Synchronous clients

Consider the following example, which creates synchronous clients for both logs and metrics querying:

```python
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient, MetricsQueryClient

credential = DefaultAzureCredential()
logs_client = LogsQueryClient(credential)
metrics_client = MetricsQueryClient(credential)
```

#### Asynchronous clients

The asynchronous forms of the query client APIs are found in the `.aio`-suffixed namespace. For example:

```python
from azure.identity.aio import DefaultAzureCredential
from azure.monitor.query.aio import LogsQueryClient, MetricsQueryClient

credential = DefaultAzureCredential()
async_logs_client = LogsQueryClient(credential)
async_metrics_client = MetricsQueryClient(credential)
```

## Key concepts

### Logs

Azure Monitor Logs collects and organizes log and performance data from monitored resources. Data from different sources can be consolidated into a single workspace. Examples of data sources include:

- Platform logs from Azure services.
- Log and performance data from virtual machine agents.
- Usage and performance data from apps.

#### Azure Log Analytics workspaces

Data collected by Azure Monitor Logs is stored in one or more [Log Analytics workspaces](https://docs.microsoft.com/azure/azure-monitor/logs/data-platform-logs#log-analytics-workspaces). The workspace defines the:

- Geographic location of the data.
- Access rights defining which users can access data.
- Configuration settings, such as the pricing tier and data retention.

#### Log queries

Data from the disparate sources can be analyzed together using [Kusto Query Language (KQL)](https://docs.microsoft.com/azure/data-explorer/kusto/query/)&mdash;the same query language used by [Azure Data Explorer](https://docs.microsoft.com/azure/data-explorer/data-explorer-overview). Data is retrieved from a Log Analytics workspace using a KQL query&mdash;a read-only request to process data and return results. For more information, see [Log queries in Azure Monitor](https://docs.microsoft.com/azure/azure-monitor/logs/log-query-overview).

### Metrics

Azure Monitor Metrics collects numeric data from monitored resources into a time series database. Metrics are collected at regular intervals and describe some aspect of a system at a particular time. Metrics in Azure Monitor are lightweight and can support near real-time scenarios. They're useful for alerting and fast detection of issues. Metrics can be:

- Analyzed interactively with [Metrics Explorer](https://docs.microsoft.com/azure/azure-monitor/essentials/metrics-getting-started).
- Used to receive notifications with an alert when a value crosses a threshold.
- Visualized in a workbook or dashboard.

#### Metrics data structure

Each set of metric values is a time series with the following characteristics:

- The time the value was collected
- The resource associated with the value
- A namespace that acts like a category for the metric
- A metric name
- The value itself
- Some metrics may have multiple dimensions as described in multi-dimensional metrics. Custom metrics can have up to 10 dimensions.

## Examples

- [Single logs query](#single-logs-query)
  - [Specify timespan](#specify-timespan)
  - [Set logs query timeout](#set-logs-query-timeout)
- [Batch logs query](#batch-logs-query)
- [Query metrics](#query-metrics)
- [Handle metrics response](#handle-metrics-response)
  - [Example of handling response](#example-of-handling-response)
- [Advanced scenarios](#advanced-scenarios)
  - [Query multiple workspaces](#query-multiple-workspaces)

### Single logs query

This example shows getting a log query. To handle the response and view it in a tabular form, the [pandas](https://pypi.org/project/pandas/) library is used. See the [samples][python-query-samples] if you choose not to use pandas.

#### Specify timespan

The `timespan` parameter specifies the time duration for which to query the data. The timespan for which to query the data. This can be a timedelta, a timedelta and a start datetime, or a start datetime/end datetime. For example:

```python
import os
import pandas as pd
from datetime import datetime
from azure.monitor.query import LogsQueryClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = LogsQueryClient(credential)

# Response time trend
# request duration over the last 12 hours
query = """AppRequests |
summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId"""

start_time=datetime(2021, 7, 2)
end_time=datetime.now()

# returns LogsQueryResult
response = client.query(
    os.environ['LOG_WORKSPACE_ID'],
    query,
    timespan=(start_time, end_time)
    )

if not response.tables:
    print("No results for the query")

for table in response.tables:
    df = pd.DataFrame(table.rows, columns=[col.name for col in table.columns])
    print(df)
```

#### Set logs query timeout

The following example shows setting a server timeout in seconds. A gateway timeout is raised if the query takes more time than the mentioned timeout. The default is 180 seconds and can be set up to 10 minutes (600 seconds).

```python
import os
import pandas as pd
from azure.monitor.query import LogsQueryClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = LogsQueryClient(credential)

response = client.query(
    os.environ['LOG_WORKSPACE_ID'],
    "range x from 1 to 10000000000 step 1 | count",
    server_timeout=1,
    )
```

### Batch logs query

The following example demonstrates sending multiple queries at the same time using batch query API. The queries can either be represented as a list of `LogQueryRequest` objects or a dictionary. This example uses the former approach.

```python
import os
from datetime import timedelta
import pandas as pd
from azure.monitor.query import LogsQueryClient, LogsQueryRequest
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
        query= """AppRequests | take 10  |
            summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId""",
        timespan=(datetime(2021, 6, 2), timedelta(hours=1)),
        workspace_id=os.environ['LOG_WORKSPACE_ID']
    ),
    LogsBatchQueryRequest(
        query= "AppRequests | take 2",
        workspace_id=os.environ['LOG_WORKSPACE_ID']
    ),
]
response = client.query_batch(requests)

for rsp in response:
    body = rsp.body
    if not body.tables:
        print("Something is wrong")
    else:
        for table in body.tables:
            df = pd.DataFrame(table.rows, columns=[col.name for col in table.columns])
            print(df)
```

#### Handling the response for Logs Query

The `query` API returns the `LogsQueryResult` while the `batch_query` API returns list of `LogsQueryResult`.

Here is a heirarchy of the response:

```
LogsQueryResult
|---statistics
|---visualization
|---error
|---tables (list of `LogsTable` objects)
    |---name
    |---rows
    |---columns (list of `LogsTableColumn` objects)
        |---name
        |---type
```

So, to handle a response with tables and display it using pandas,

```python
table = response.tables[0]
df = pd.DataFrame(table.rows, columns=[col.name for col in table.columns])
```
A full sample can be found [here](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_log_query_client.py).

In a very similar fashion, to handle a batch response, 

```python
for result in response:
    table = result.tables[0]
    df = pd.DataFrame(table.rows, columns=[col.name for col in table.columns])
```
A full sample can be found [here](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_batch_query.py).

### Query metrics

The following example gets metrics for an Event Grid subscription. The resource URI is that of an event grid topic.

The resource URI must be that of the resource for which metrics are being queried. It's normally of the format `/subscriptions/<id>/resourceGroups/<rg-name>/providers/<source>/topics/<resource-name>`.

To find the resource URI:

1. Navigate to your resource's page in the Azure portal.
2. From the **Overview** blade, select the **JSON View** link.
3. In the resulting JSON, copy the value of the `id` property.

```python
import os
from datetime import timedelta
from azure.monitor.query import MetricsQueryClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = MetricsQueryClient(credential)
start_time = datetime(2021, 5, 25)
duration = timedelta(days=1)
metrics_uri = os.environ['METRICS_RESOURCE_URI']
response = client.query(
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

### Handle metrics response

The metrics query API returns a `MetricsResult` object. The `MetricsResult` object contains properties such as a list of `Metric`-typed objects, `granularity`, `namespace`, and `timespan`. The `Metric` objects list can be accessed using the `metrics` param. Each `Metric` object in this list contains a list of `TimeSeriesElement` objects. Each `TimeSeriesElement` contains `data` and `metadata_values` properties. In visual form, the object hierarchy of the response resembles the following structure:

```
MetricsResult
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
from datetime import datetime, timedelta
from azure.monitor.query import MetricsQueryClient, MetricAggregationType
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = MetricsQueryClient(credential)

metrics_uri = os.environ['METRICS_RESOURCE_URI']
response = client.query(
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

### Advanced scenarios

#### Query multiple workspaces

The same log query can be executed across multiple Log Analytics workspaces. In addition to the KQL query, the following parameters are required:

- `workspace_id` - The first (primary) workspace ID.
- `additional_workspaces` - A list of workspaces, excluding the workspace provided in the `workspace_id` parameter. The parameter's list items may consist of the following identifier formats:
  - Qualified workspace names
  - Workspace IDs
  - Azure resource IDs

For example, the following query executes in three workspaces:

```python
client.query(
    <workspace_id>,
    query,
    additional_workspaces=['<workspace 2>', '<workspace 3>']
    )
```

A full sample can be found [here](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_log_query_multiple_workspaces.py).

## Troubleshooting

Enable the `azure.monitor.query` logger to collect traces from the library.

### General

Monitor Query client library will raise exceptions defined in [Azure Core][azure_core_exceptions].

### Logging

This library uses the standard [logging][python_logging] library for logging. Basic information about HTTP sessions, such as URLs and headers, is logged at the `INFO` level.

### Optional configuration

Optional keyword arguments can be passed in at the client and per-operation level. The `azure-core` [reference documentation][azure_core_ref_docs] describes available configurations for retries, logging, transport protocols, and more.

## Next steps

### Additional documentation

For more extensive documentation, see the [Azure Monitor Query documentation][python-query-product-docs].

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repositories using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[azure_cli_link]: https://pypi.org/project/azure-cli/
[python-query-src]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/
[python-query-pypi]: https://aka.ms/azsdk-python-monitor-query-pypi
[python-query-product-docs]: https://docs.microsoft.com/azure/azure-monitor/
[python-query-ref-docs]: https://docs.microsoft.com/python/api/overview/azure/monitor-query-readme?view=azure-python-preview
[python-query-samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-query/samples
[python-query-changelog]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-query/CHANGELOG.md
[pip]: https://pypi.org/project/pip/

[azure_core_exceptions]: https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions
[python_logging]: https://docs.python.org/3/library/logging.html
[azure_core_ref_docs]: https://aka.ms/azsdk/python/core/docs
[azure_subscription]: https://azure.microsoft.com/free/python/

[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
