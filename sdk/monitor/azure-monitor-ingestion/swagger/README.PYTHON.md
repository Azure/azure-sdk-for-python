# Azure Monitor Data Collection Client for Python

> see https://aka.ms/autorest

### Configuration

```yaml
title: LogsIngestionClient
description: Azure Monitor Data Collection Python Client
generated-metadata: false
package-name: azure-monitor-ingestion
license-header: MICROSOFT_MIT_NO_VERSION
no-namespace-folders: true
output-folder: ../azure/monitor/ingestion
source-code-folder-path: ./azure/monitor/ingestion
add-credential: true
credential-scopes: https://monitor.azure.com//.default
input-file:
    - https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/monitor/data-plane/ingestion/stable/2023-01-01/DataCollectionRules.json
python: true
version-tolerant: true
python3-only: true
black: true
```

## Customizations

### Make generated operation methods/overloads internal

```yaml
directive:
  - from: swagger-document
    where: '$["paths"]["/dataCollectionRules/{ruleId}/streams/{stream}"]["post"]'
    transform: >
      $["x-ms-internal"] = true;
```
