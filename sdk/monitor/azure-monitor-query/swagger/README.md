# Azure Monitor Query Client for Python

> see https://aka.ms/autorest

### Configuration

```yaml
title: MonitorQueryClient
description: Azure Monitor Query Python Client
generated-metadata: false
license-header: MICROSOFT_MIT_NO_VERSION
package-name: azure-monitor-query
no-namespace-folders: true
python: true
version-tolerant: true
python3-only: true
black: true
clear-output-folder: true
modelerfour:
  lenient-model-deduplication: true
```

## Batch execution

```yaml
batch:
  - tag: release_query
  - tag: release_metrics
  - tag: release_metrics_batch
```

## Query

These settings apply only when `--tag=release_query` is specified on the command line.

```yaml $(tag) == 'release_query'
input-file:
  - https://github.com/Azure/azure-rest-api-specs/blob/0b64ca7cbe3af8cd13228dfb783a16b8272b8be2/specification/operationalinsights/data-plane/Microsoft.OperationalInsights/stable/2022-10-27/OperationalInsights.json
output-folder: ../azure/monitor/query/_generated
title: MonitorQueryClient
description: Azure Monitor Query Python Client
```

## Metrics

These settings apply only when `--tag=release_metrics` is specified on the command line.

```yaml $(tag) == 'release_metrics'
input-file:
    - https://github.com/Azure/azure-rest-api-specs/blob/0b64ca7cbe3af8cd13228dfb783a16b8272b8be2/specification/monitor/resource-manager/Microsoft.Insights/stable/2024-02-01/metricDefinitions_API.json
    - https://github.com/Azure/azure-rest-api-specs/blob/0b64ca7cbe3af8cd13228dfb783a16b8272b8be2/specification/monitor/resource-manager/Microsoft.Insights/stable/2024-02-01/metrics_API.json
    - https://github.com/Azure/azure-rest-api-specs/blob/0b64ca7cbe3af8cd13228dfb783a16b8272b8be2/specification/monitor/resource-manager/Microsoft.Insights/stable/2024-02-01/metricNamespaces_API.json
output-folder: ../azure/monitor/query/_generated/metrics
title: MonitorMetricsClient
description: Azure Monitor Metrics Python Client
```

### Metrics Batch

These settings apply only when `--tag=release_metrics` is specified on the command line.

```yaml $(tag) == 'release_metrics_batch'
input-file:
    - https://github.com/Azure/azure-rest-api-specs/blob/0b64ca7cbe3af8cd13228dfb783a16b8272b8be2/specification/monitor/data-plane/Microsoft.Insights/stable/2024-02-01/metricBatch.json
output-folder: ../azure/monitor/query/_generated/metrics/batch
title: MonitorBatchMetricsClient
description: Azure Monitor Batch Metrics Python Client
```

### Remove metadata operations

``` yaml
directive:
- from: swagger-document
  where: $
  transform: >
    delete $.securityDefinitions
```

### Make properties required

``` yaml
directive:
- from: swagger-document
  where: $.definitions.column
  transform: >
    $.required = ["name", "type"]
```

### Remove subscription scoped operations

``` yaml
directive:
  - remove-operation: MetricDefinitions_ListAtSubscriptionScope
  - remove-operation: Metrics_ListAtSubscriptionScope
  - remove-operation: Metrics_ListAtSubscriptionScopePost
```

### Interval adjustments

Currently, the value for `default`` is erroneously being set to the parameter default in the generated method: https://github.com/Azure/autorest.python/issues/2062
Also, the interval parameter in the spec does not use the "duration" format due to the need to support the "FULL" keyword which is not a valid ISO 8601 duration. In the Python SDK, we want the interval parameter to be `timedelta` only, so we add the "duration" format.

``` yaml
directive:
- from: swagger-document
  where: $.parameters[IntervalParameter]
  transform: >
    delete $.default;
    $.format = "duration";
```
