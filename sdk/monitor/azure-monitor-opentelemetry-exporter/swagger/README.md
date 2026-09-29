# OpenTelemetry Exporter for Azure Monitor Client for Python

> see https://aka.ms/autorest

## Instructions

From `azure-monitor-opentelemetry-exporter/`:

```
rmdir ./azure/monitor/opentelemetry/exporter/_generated
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
output-folder: ../azure/monitor/opentelemetry/exporter/_generated
source-code-folder-path: ./azure/monitor/opentelemetry/exporter/_generated
input-file: 
    - https://github.com/Azure/azure-rest-api-specs/blob/main/specification/applicationinsights/data-plane/Monitor.Exporters/preview/v2.1/swagger.json

python: true
v3: true
```
