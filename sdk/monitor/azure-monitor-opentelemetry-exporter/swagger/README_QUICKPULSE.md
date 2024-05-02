# Quickpulse metrics exporter for Python

> see https://aka.ms/autorest

## Instructions

From `azure-monitor-opentelemetry-exporter/`:

```
rmdir ./azure/monitor/opentelemetry/exporter/quickpulse/_generated
autorest ./swagger/README_QUICKPULSE.md --python --v3
```

### Configuration

```yaml
title: QuickpulseClient
description: Quickpulse Client
generated-metadata: false
license-header: MICROSOFT_MIT_NO_VERSION
no-namespace-folders: true
output-folder: ../azure/monitor/opentelemetry/exporter/_quickpulse/_generated
source-code-folder-path: ./azure/monitor/opentelemetry/exporter/_quickpulse/_generated
input-file: https://github.com/Azure/azure-rest-api-specs/blob/665e7c3b6f26b148b3c05e55602621bc293cc0a4/specification/applicationinsights/data-plane/LiveMetrics/preview/2024-04-01-preview/livemetrics.json
python: true
models-mode: msrest
```
