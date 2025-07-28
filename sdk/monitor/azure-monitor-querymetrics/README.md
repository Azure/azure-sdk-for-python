# Azure Monitor Query Metrics client library for Python

The Azure Monitor Query Metrics client library enables you to perform read-only queries against [Azure Monitor][azure_monitor_overview]'s metrics data platform. It is designed for retrieving numerical metrics from Azure resources, supporting scenarios such as monitoring, alerting, and troubleshooting.

- [Metrics](https://learn.microsoft.com/azure/azure-monitor/essentials/data-platform-metrics): Numeric data collected from resources at regular intervals, stored as time series. Metrics provide insights into resource health and performance, and are optimized for near real-time analysis.

This library interacts with the Azure Monitor Metrics Data Plane API, allowing you to query metrics for multiple resources in a single request. For details on batch querying, see [Batch API migration guide](https://learn.microsoft.com/azure/azure-monitor/metrics/migrate-to-batch-api?tabs=individual-response).

**Resources:**

<!-- TODO: Add Conda-->
- [Source code][source]
- [Package (PyPI)][package]
- [API reference documentation][python-querymetrics-ref-docs]
- [Service documentation][azure_monitor_overview]
- [Samples][samples]
- [Change log][changelog]

## Getting started

### Prerequisites

- Python 3.9 or later
- An [Azure subscription][azure_subscription]
- Authorization to read metrics data at the Azure subscription level. For example, the [Monitoring Reader role](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles/monitor#monitoring-reader) on the subscription containing the resources to be queried.
- An Azure resource of any kind (Storage Account, Key Vault, Cosmos DB, etc.).

### Install the package

Install the Azure Monitor Query Metrics client library for Python with [pip][pip]:

```bash
pip install azure-monitor-querymetrics
```

### Create the client

An authenticated client is required to query Metrics. The library includes both synchronous and asynchronous forms of the client. To authenticate, create an instance of a token credential. Use that instance when creating a `MetricsClient`. The following examples use `DefaultAzureCredential` from the [azure-identity](https://pypi.org/project/azure-identity/) package.

#### Synchronous client

Consider the following example, which creates a synchronous client for Metrics querying:

```python
from azure.identity import DefaultAzureCredential
from azure.monitor.querymetrics import MetricsClient

credential = DefaultAzureCredential()
metrics_client = MetricsClient("https://<regional endpoint>", credential)
```

#### Asynchronous client

The asynchronous form of the client API is found in the `.aio`-suffixed namespace. For example:

```python
from azure.identity.aio import DefaultAzureCredential
from azure.monitor.querymetrics.aio import MetricsClient

credential = DefaultAzureCredential()
async_metrics_client = MetricsClient("https://<regional endpoint>", credential)
```

To use the asynchronous clients, you must also install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/).

```sh
pip install aiohttp
```

#### Configure client for Azure sovereign cloud

By default, the client is configured to use the Azure public cloud. To use a sovereign cloud, provide the correct `audience` argument when creating the `MetricsClient`. For example:

```python
from azure.identity import AzureAuthorityHosts, DefaultAzureCredential
from azure.monitor.querymetrics import MetricsClient

# Authority can also be set via the AZURE_AUTHORITY_HOST environment variable.
credential = DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_GOVERNMENT)

metrics_client = MetricsClient(
    "https://usgovvirginia.metrics.monitor.azure.us", credential, audience="https://metrics.monitor.azure.us"
)
```

### Execute the query

For examples of Metrics queries, see the [Examples](#examples) section.

## Key concepts

### Metrics data structure

Each set of metric values is a time series with the following characteristics:

- The time the value was collected
- The resource associated with the value
- A namespace that acts like a category for the metric
- A metric name
- The value itself
- Some metrics have multiple dimensions as described in multi-dimensional metrics.

## Examples

- [Metrics query](#metrics-query)
  - [Handle metrics query response](#handle-metrics-query-response)

### Metrics query

To query metrics for one or more Azure resources, use the `query_resources` method of `MetricsClient`. This method requires a regional endpoint when creating the client. For example, "https://westus3.metrics.monitor.azure.com".

Each Azure resource must reside in:

- The same region as the endpoint specified when creating the client.
- The same Azure subscription.

The resource IDs must be that of the resources for which metrics are being queried. It's normally of the format `/subscriptions/<id>/resourceGroups/<rg-name>/providers/<source>/topics/<resource-name>`.

To find the resource ID/URI:

1. Navigate to your resource's page in the Azure portal.
1. Select the **JSON View** link in the **Overview** section.
1. Copy the value in the **Resource ID** text box at the top of the JSON view.

Furthermore:

- The user must be authorized to read monitoring data at the Azure subscription level. For example, the [Monitoring Reader role](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles/monitor#monitoring-reader) on the subscription to be queried.
- The metric namespace containing the metrics to be queried must be provided. For a list of metric namespaces, see [Supported metrics and log categories by resource type][metric_namespaces].

```python
from datetime import timedelta
import os

from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.monitor.querymetrics import MetricsClient, MetricAggregationType

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
    metric_names=["UsedCapacity"],
    timespan=timedelta(hours=2),
    granularity=timedelta(minutes=5),
    aggregations=[MetricAggregationType.AVERAGE],
)

for metrics_query_result in response:
    for metric in metrics_query_result.metrics:
        print(f"Metric: {metric.name}")
        for time_series in metric.timeseries:
            for metric_value in time_series.data:
                if metric_value.average is not None:
                    print(f"Average: {metric_value.average}")
```

#### Handle metrics query response

The metrics query API returns a list of `MetricsQueryResult` objects. The `MetricsQueryResult` object contains properties such as a list of `Metric`-typed objects, `granularity`, `namespace`, and `timespan`. The `Metric` objects list can be accessed using the `metrics` param. Each `Metric` object in this list contains a list of `TimeSeriesElement` objects. Each `TimeSeriesElement` object contains `data` and `metadata_values` properties. In visual form, the object hierarchy of the response resembles the following structure:

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
        |---data (list of data points)
```

**Note:** Each `MetricsQueryResult` is returned in the same order as the corresponding resource in the `resource_ids` parameter. If multiple different metrics are queried, the metrics are returned in the order of the `metric_names` sent.

**Example of handling response**

```python
import os
from azure.monitor.querymetrics import MetricsClient, MetricAggregationType
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = MetricsClient("https://<regional endpoint>", credential)

metrics_uri = os.environ['METRICS_RESOURCE_URI']
response = client.query_resource(
    metrics_uri,
    metric_names=["PublishSuccessCount"],
    aggregations=[MetricAggregationType.AVERAGE]
)

for metrics_query_result in response:
    for metric in metrics_query_result.metrics:
        print(f"Metric: {metric.name}")
        for time_series in metric.timeseries:
            for metric_value in time_series.data:
                if metric_value.average is not None:
                    print(f"Average: {metric_value.average}")
```

## Troubleshooting

See our [troubleshooting guide][troubleshooting_guide] for details on how to diagnose various failure scenarios.

## Next steps

To learn more about Azure Monitor, see the [Azure Monitor service documentation][azure_monitor_overview].

### Samples

The following code samples show common scenarios with the Azure Monitor Query Metrics client library.

#### Metrics query samples

To be added.

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repositories using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[azure_core_exceptions]: https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions
[azure_core_ref_docs]: https://aka.ms/azsdk/python/core/docs
[azure_monitor_overview]: https://learn.microsoft.com/azure/azure-monitor/
[azure_subscription]: https://azure.microsoft.com/free/python/
[changelog]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-querymetrics/CHANGELOG.md
[metric_namespaces]: https://learn.microsoft.com/azure/azure-monitor/reference/supported-metrics/metrics-index#supported-metrics-and-log-categories-by-resource-type
[package]: https://aka.ms/azsdk-python-monitor-querymetrics-pypi
[pip]: https://pypi.org/project/pip/
[python_logging]: https://docs.python.org/3/library/logging.html
[python-querymetrics-ref-docs]: https://aka.ms/azsdk/python/querymetrics/docs
[samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-querymetrics/samples
[source]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-querymetrics/
[troubleshooting_guide]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-querymetrics/TROUBLESHOOTING.md

[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
