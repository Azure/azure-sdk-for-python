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
output-folder: ../azure/monitor/opentelemetry/exporter/quickpulse/_generated
source-code-folder-path: ./azure/monitor/opentelemetry/exporter/quickpulse/_generated
input-file: https://quickpulsespecs.blob.core.windows.net/specs/swagger-v2-for%20sdk%20only.json
python: true
models-mode: msrest
```
