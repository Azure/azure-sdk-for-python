# Azure Monitor Query Client for Python

> see https://aka.ms/autorest

### Configuration

```yaml
title: MonitorQueryClient
description: Azure Monitor Query Python Client
generated-metadata: false

license-header: MICROSOFT_MIT_NO_VERSION
no-namespace-folders: true
output-folder: ../azure/monitor/query/_generated
source-code-folder-path: ./azure/monitor/query/_generated
input-file: 
    - https://github.com/Azure/azure-rest-api-specs/blob/dba6ed1f03bda88ac6884c0a883246446cc72495/specification/operationalinsights/data-plane/Microsoft.OperationalInsights/preview/2021-05-19_Preview/OperationalInsights.json
    - https://github.com/Azure/azure-rest-api-specs/blob/dba6ed1f03bda88ac6884c0a883246446cc72495/specification/monitor/resource-manager/Microsoft.Insights/stable/2018-01-01/metricDefinitions_API.json
    - https://github.com/Azure/azure-rest-api-specs/blob/dba6ed1f03bda88ac6884c0a883246446cc72495/specification/monitor/resource-manager/Microsoft.Insights/stable/2018-01-01/metrics_API.json
    - https://github.com/Azure/azure-rest-api-specs/blob/dba6ed1f03bda88ac6884c0a883246446cc72495/specification/monitor/resource-manager/Microsoft.Insights/preview/2017-12-01-preview/metricNamespaces_API.json
modelerfour:
    lenient-model-deduplication: true
python: true
v3: true
use: "@autorest/python@5.6.4"
```

### Remove metadata operations

``` yaml
directive:
- from: swagger-document
  where: $
  transform: >
    delete $.securityDefinitions
```

### Add statistics and render

``` yaml
directive:
- from: swagger-document
  where: $.definitions.logQueryResult
  transform: >
    $.properties["statistics"] = { "type": "object" };
    $.properties["render"] = { "type": "object" };
```

``` yaml
directive:
- from: swagger-document
  where: $.definitions.queryResults
  transform: >
    $.properties["statistics"] = { "type": "object" };
    $.properties["render"] = { "type": "object" };
```

### Make properties required

``` yaml
directive:
- from: swagger-document
  where: $.definitions.column
  transform: >
    $.required = ["name", "type"]
```
