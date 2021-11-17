# Azure Purview for Python

> see https://aka.ms/autorest

### Setup

Install Autorest v3

```ps
npm install -g autorest
```

### Generation

```ps
cd <swagger-folder>
autorest
```

### Settings

```yaml
input-file: https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/cognitiveservices/data-plane/MetricsAdvisor/stable/v1.0/MetricsAdvisor.json
output-folder: ../azure/ai/metricsadvisor/_generated
namespace: azure.ai.metricsadvisor
package-name: azure-ai-metricsadvisor
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
python: true
title: MetricsAdvisor
head-as-boolean: true
package-version: 1.0.0
add-credential: true
credential-scopes: https://cognitiveservices.azure.com/.default
```

### Make getRootCauseOfIncidentByAnomalyDetectionConfiguration pageable

```yaml
directive:
  - from: swagger-document
    where: $["paths"]["/enrichment/anomalyDetection/configurations/{configurationId}/incidents/{incidentId}/rootCause"].get
    transform: $["operationId"] = "HasPermission"
```
getRootCauseOfIncidentByAnomalyDetectionConfiguration