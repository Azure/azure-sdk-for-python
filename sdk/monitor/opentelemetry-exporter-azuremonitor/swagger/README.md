# Opentelemtry Exporter for Azure Monitor Client for Python

> see https://aka.ms/autorest

## Instructions

From `opentelemetry-exporter-azuremonitor/`:

```
rmdir ./opentelemetry/exporter/azuremonitor/_generated
autorest ./swagger/README.md --python --v3
```

### Configuration

```yaml
title: AzureMonitorClient
description: Opentelemetry Exporter for Azure Monitor
generated-metadata: false
license-header: MICROSOFT_MIT_NO_VERSION
no-namespace-folders: true
output-folder: ../opentelemetry/exporter/azuremonitor/_generated
source-code-folder-path: ./opentelemetry/exporter/azuremonitor/_generated
input-file: 
    - https://github.com/Azure/azure-rest-api-specs/blob/master/specification/applicationinsights/data-plane/Monitor.Exporters/preview/2020-09-15_Preview/swagger.json

python: true
v3: true
use: "@autorest/python@5.1.0-preview.7"
```
