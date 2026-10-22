# Guide to migrating from v1 to v2

Version 2.0.0 of `azure-monitor-query` removes the metrics querying capabilities, which are now handled by separate packages.
This guide assists you in the migration from [azure-monitor-query](https://pypi.org/project/azure-monitor-query/) versions 1.x to 2.x, and outlines how to adapt your code to leverage the new packages for metrics querying.

## Table of contents

- [Quick migration decision tree](#quick-migration-decision-tree)
- [Motivation for v2](#motivation-for-v2)
- [Key changes](#key-changes)
  - [Logs querying with LogsQueryClient](#logs-querying-with-logsqueryclient)
  - [Metrics querying with MetricsClient](#metrics-querying-with-metricsclient)
  - [Metrics operations with MetricsQueryClient](#metrics-operations-with-metricsqueryclient)
    - [Querying metrics](#querying-metrics)
    - [Listing metric definitions](#listing-metric-definitions)
    - [Listing metric namespaces](#listing-metric-namespaces)
- [Common migration tasks](#common-migration-tasks)

## Quick migration decision tree

**Which client are you currently using?**

- **`LogsQueryClient`** → **No changes needed** - continue using `azure-monitor-query` package
- **`MetricsClient`** → **Simple migration** - switch to `azure-monitor-querymetrics` package (same API, different import)
- **`MetricsQueryClient`** → **Choose your path:**
  - For **metrics querying**: Use `MetricsClient` from `azure-monitor-querymetrics` (recommended - higher query limits)
  - For **full metrics management capabilities**: Use `MonitorManagementClient` from `azure-mgmt-monitor` package (requires code changes)

## Motivation for v2

Historically, the Azure Monitor Query library was a monolithic package that included both Log Analytics and Metrics querying capabilities across 5 different services/endpoints. While this may have seemed convenient, it introduced challenges for users. A single package combining multiple services meant customers couldn’t upgrade one service independently of others. Any breaking change in one service forced updates across all services in the package, disrupting customer workflows.

To address these issues, Azure adopted a formal definition of a service as a set of operations that version uniformly. Each service version now has a dedicated package, documentation, and API contract. This structure allows libraries to be generated directly from [TypeSpec](https://typespec.io/) definitions, improving consistency, reducing manual intervention, and aligning with Azure’s long-term tooling strategy.

With this in mind, the `azure-monitor-query` package will now focus solely on logs querying, while resource metrics querying will be handled by the new `azure-monitor-querymetrics` package and `azure-mgmt-monitor`.

## Key changes

### Logs querying with `LogsQueryClient`

There is **no change** in the way you query logs using the `LogsQueryClient`. The client remains the same, and you can continue to use it as before.

### Metrics querying with `MetricsClient`

The `MetricsClient` has been moved to a separate package called `azure-monitor-querymetrics`. You can install it using:

```bash
pip install azure-monitor-querymetrics
```

The only code change that needs to be made is the import path:

```diff
- from azure.monitor.query import MetricsClient, MetricAggregationType
+ from azure.monitor.querymetrics import MetricsClient, MetricAggregationType
```

### Metrics operations with `MetricsQueryClient`

`MetricsQueryClient` has been removed from `azure-monitor-query`, and its functionality is **not included** in the `azure-monitor-querymetrics` package.

`MetricsQueryClient` provided three functions: `query_resource`, `list_metric_definitions`, and `list_metric_namespaces`. If you were using it for querying metrics from resources, you should consider switching to `MetricsClient` from the [`azure-monitor-querymetrics`](https://pypi.org/project/azure-monitor-querymetrics/) package, which provides similar functionality and higher query limits compared to the [Azure Resource Manager (ARM) APIs](https://learn.microsoft.com/azure/azure-resource-manager/management/request-limits-and-throttling) that `MetricsQueryClient` used.

Otherwise, you can switch to using the `MonitorManagementClient` from the `azure-mgmt-monitor` package, which provides comprehensive Azure Monitor resource management capabilities.

You can install it using:

```bash
pip install azure-mgmt-monitor
```

The APIs are similar, but there are some differences in method names, parameters, and responses. Below are comparisons for each operation.

#### Querying metrics

**Migration**: Use `client.metrics.list()` instead of `client.query_resource()`.

***With `azure-monitor-query 1.x`:***

```python
import os
from datetime import timedelta

from azure.identity import DefaultAzureCredential
from azure.monitor.query import MetricsQueryClient, MetricAggregationType

credential = DefaultAzureCredential()
client = MetricsQueryClient(credential)

resource_uri = os.environ["METRICS_RESOURCE_URI"]

# Query metrics for a specific resource
response = client.query_resource(
    resource_uri,
    metric_names=["cacheWrite"],
    timespan=timedelta(hours=2),
    granularity=timedelta(minutes=5),
    aggregations=[MetricAggregationType.AVERAGE],
    max_results=10,
    order_by="average desc",
    filter="ShardId eq '0'",
    metric_namespace="Microsoft.Cache/Redis",
)

# Process resource metrics query response
for metric in response.metrics:
    print(f"Metric Name: {metric.name}")
    for timeseries in metric.timeseries:
        for data in timeseries.data:
            print(f"Timestamp: {data.timestamp}, Average: {data.average}")
```

***With `azure-mgmt-monitor`:***

```python
import os

from azure.identity import DefaultAzureCredential
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.monitor.models import AggregationType

resource_uri = os.environ["METRICS_RESOURCE_URI"]

# If only using non-subscription scoped operations like the ones provided by MetricsQueryClient,
# you can pass in an arbitrary placeholder subscription ID.
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

credential = DefaultAzureCredential()
client = MonitorManagementClient(credential, subscription_id)

# Query metrics for a specific resource
response = client.metrics.list(
    resource_uri,
    metricnames="cacheWrite",
    timespan="2025-07-20T09:00:00Z/2025-07-20T14:00:00Z",  # <ISO 8601 Start Time>/<ISO 8601 End Time>
    interval="PT5M",  # ISO 8601 duration format
    aggregation=AggregationType.AVERAGE,
    top=10,
    orderby="average desc",
    filter="ShardId eq '0'",
    metricnamespace="Microsoft.Cache/Redis",
)

# Process resource metrics query response
for metric in response.value:
    print(f"Metric Name: {metric.name.value}")
    for timeseries in metric.timeseries:
        for data in timeseries.data:
            print(f"Timestamp: {data.time_stamp}, Average: {data.average}")
```

**Parameter changes**:
- `metric_names` becomes `metricnames`
- `timespan` is now an ISO 8601 duration string (e.g., `"PT2H"` for past 2 hours) or a time range (e.g., `"2025-07-20T09:00:00Z/2025-07-20T14:00:00Z"`)
  - For guide on converting `timedelta` to ISO 8601, see [Converting datetime and timedelta objects](#converting-datetime-and-timedelta-objects).
- `granularity` is replaced with `interval`, which is also an ISO 8601 duration string
- `aggregations` is replaced with `aggregation`, which is a comma-separated string of aggregation types (e.g., `"Average"`)
- `max_results` is replaced with `top`, which specifies the maximum number of results to return
- `order_by` is replaced with `orderby`, which specifies the order of results
- `metric_namespace` becomes `metricnamespace`, which specifies the namespace of the metrics in string format

**Response structure comparison**:

The response structure has a few minor differences. Below is a comparison of the key attributes in the response.

[comment]: # ( cspell:ignore thead )

<div style="overflow-x: auto; border: 1px solid #ccc; border-radius: 8px; padding: 10px;">
  <table style="width: 100%; border-collapse: collapse; min-width: 300px;">
    <thead>
      <tr>
        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-family: 'Inter', sans-serif; border-top-left-radius: 4px; border-top-right-radius: 4px;">MetricsQueryResult (azure-monitor-query)</th>
        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-family: 'Inter', sans-serif;">Response (azure-mgmt-monitor)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td style="padding: 12px; border-bottom: 1px solid #eee; vertical-align:top;">
        <pre>
MetricsQueryResult
|---timespan: str
|---granularity: timedelta
|---cost: int
|---namespace: str
|---resource_region: str
|---metrics: List[Metric]
    |---id: str
    |---type: str
    |---name: str
    |---unit: str
    |---display_description: str
    |---timeseries: List[TimeSeriesElement]
        |---metadata_values: dict
        |---data: List[MetricValue]
            |---timestamp: datetime
            |---average: float
            |---maximum: float
            |---minimum: float
            |---total: float
            |---count: float
        </pre>
        </td>
        <td style="padding: 12px; border-bottom: 1px solid #eee; vertical-align:top;">
    <pre>
Response
|---timespan: str
|---interval: str
|---cost: int
|---namespace: str
|---resourceregion: str
|---metrics List[Metric]
    |---id: str
    |---type: str
    |---name: LocalizableString
    |   |---value: str
    |---unit: str | MetricUnit
    |---display_description: str
    |---timeseries: List[TimeSeriesElement]
        |---metadata_values: List[MetadataValue]
        |   |---name: LocalizableString
        |       |---value: str
        |   |---value: str
        |---data: List[MetricValue]
            |---time_stamp: datetime
            |---average: float
            |---maximum: float
            |---minimum: float
            |---total: float
            |---count: float
        </pre>
        </td>
      </tr>
    </tbody>
  </table>
</div>

#### Listing metric definitions

**Migration**: Use `client.metric_definitions.list()` instead of `client.list_metric_definitions()`.

***With `azure-monitor-query 1.x`:***

```python
# Query metric definitions for a specific resource
metric_definitions = client.list_metric_definitions(
    resource_uri, namespace="Microsoft.Cache/Redis"
)

for definition in metric_definitions:
    print(f"Metric Definition: {definition.name}")
    if definition.metric_availabilities:
        for availability in definition.metric_availabilities:
            print(f"Granularity: {availability.granularity}, Retention: {availability.retention}")
```

***With `azure-mgmt-monitor`:***

```python
# Query metric definitions for a specific resource
metric_definitions = client.metric_definitions.list(resource_uri, metricnamespace="Microsoft.Cache/Redis")

for definition in metric_definitions:
    print(f"Metric Definition: {definition.name.value}")
    if definition.metric_availabilities:
        for availability in definition.metric_availabilities:
            print(f"Granularity: {availability.time_grain}, Retention: {availability.retention}")
```

**Parameter changes**:
- `namespace` becomes `metricnamespace`

#### Listing metric namespaces

**Migration**: Use `client.metric_namespaces.list()` instead of `client.list_metric_namespaces()`.

***With `azure-monitor-query 1.x`:***

```python
# Query metric namespaces for a specific resource
metric_namespaces = client.list_metric_namespaces(resource_uri)

for namespace in metric_namespaces:
    print(f"Metric Namespace: {namespace.name}")
    print(f"Type: {namespace.type}")
    print(f"Classification: {namespace.namespace_classification}")
```

***With `azure-mgmt-monitor`:***

```python
# Query metric namespaces for a specific resource
metric_namespaces = client.metric_namespaces.list(resource_uri)

for namespace in metric_namespaces:
    print(f"Metric Namespace: {namespace.name}")
    print(f"Type: {namespace.type}")
    print(f"Classification: {namespace.classification}")
```

## Common migration tasks

### Converting datetime and timedelta objects

When migrating from `MetricsQueryClient` to `MonitorManagementClient`, you'll need to convert Python datetime objects to ISO 8601 strings:

```python
from datetime import datetime, timedelta

# Converting timedelta to ISO 8601 duration
old_timespan = timedelta(hours=2)
new_timespan = f"PT{int(old_timespan.total_seconds()//3600)}H"  # "PT2H"

old_granularity = timedelta(minutes=5)
new_interval = f"PT{int(old_granularity.total_seconds()//60)}M"  # "PT5M"

# Converting datetime range to ISO 8601 timespan
end_time = datetime.now()
start_time = end_time - timedelta(hours=2)
new_timespan = f"{start_time.isoformat()}/{end_time.isoformat()}"

# For more complex conversions, consider using the isodate package:
# pip install isodate
# import isodate
# new_interval = isodate.duration_isoformat(old_granularity)
```

### Getting help

- **Package documentation**:
  - [azure-monitor-query](https://pypi.org/project/azure-monitor-query/)
  - [azure-monitor-querymetrics](https://pypi.org/project/azure-monitor-querymetrics/)
  - [azure-mgmt-monitor](https://pypi.org/project/azure-mgmt-monitor/)
- **GitHub issues**: [azure-sdk-for-python](https://github.com/Azure/azure-sdk-for-python/issues)
