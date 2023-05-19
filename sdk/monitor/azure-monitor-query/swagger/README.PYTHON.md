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
```

## Batch execution

```yaml
batch:
  - tag: release_query
  - tag: release_metrics
```

## Query

These settings apply only when `--tag=release_query` is specified on the command line.

```yaml $(tag) == 'release_query'
input-file:
  - https://github.com/Azure/azure-rest-api-specs/blob/605407bc0c1a133018285f550d01175469cb3c3a/specification/operationalinsights/data-plane/Microsoft.OperationalInsights/stable/2022-10-27/OperationalInsights.json
output-folder: ../azure/monitor/query/_generated
title: MonitorQueryClient
description: Azure Monitor Query Python Client
```

## Metrics

These settings apply only when `--tag=release_metrics` is specified on the command line.

```yaml $(tag) == 'release_metrics'
input-file:
    - https://github.com/Azure/azure-rest-api-specs/blob/605407bc0c1a133018285f550d01175469cb3c3a/specification/monitor/resource-manager/Microsoft.Insights/stable/2018-01-01/metricDefinitions_API.json
    - https://github.com/Azure/azure-rest-api-specs/blob/605407bc0c1a133018285f550d01175469cb3c3a/specification/monitor/resource-manager/Microsoft.Insights/stable/2018-01-01/metrics_API.json
    - https://github.com/Azure/azure-rest-api-specs/blob/605407bc0c1a133018285f550d01175469cb3c3a/specification/monitor/resource-manager/Microsoft.Insights/preview/2017-12-01-preview/metricNamespaces_API.json
output-folder: ../azure/monitor/query/_generated/metrics
title: MonitorMetricsClient
description: Azure Monitor Metrics Python Client
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
