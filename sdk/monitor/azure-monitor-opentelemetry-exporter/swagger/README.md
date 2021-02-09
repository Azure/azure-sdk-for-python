# OpenTelemetry Exporter for Azure Monitor Client for Python

> see https://aka.ms/autorest

## Instructions

From `azure-monitor-opentelemetry-exporter/`:

```
rmdir ./azure/opentelemetry/exporter/azuremonitor/_generated
autorest ./swagger/README.md --python --v3
```

### Configuration

```yaml
title: AzureMonitorClient
description: OpenTelemetry Exporter for Azure Monitor
generated-metadata: false
license-header: MICROSOFT_MIT_NO_VERSION
no-namespace-folders: true
trace: false
output-folder: ../azure/opentelemetry/exporter/azuremonitor/_generated
source-code-folder-path: ./azure/opentelemetry/exporter/azuremonitor/_generated
input-file: 
    - https://github.com/Azure/azure-rest-api-specs/blob/master/specification/applicationinsights/data-plane/Monitor.Exporters/preview/2020-09-15_Preview/swagger.json

python: true
v3: true
use: "@autorest/python@5.5.0"
```
