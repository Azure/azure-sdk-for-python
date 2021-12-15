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
title: MetricsAdvisorClient
head-as-boolean: true
package-version: 1.0.0
add-credential: true
credential-scopes: https://cognitiveservices.azure.com/.default
```

### Make get_root_cause_of_incident_by_anomaly_detection_configuration pageable

```yaml
directive:
- from: swagger-document
  where: '$.paths["/enrichment/anomalyDetection/configurations/{configurationId}/incidents/{incidentId}/rootCause"].get'
  transform: >
    $["x-ms-pageable"] = {"nextLinkName": null};
```

### Make get_series_by_anomaly_detection_configuration pageable

```yaml
directive:
- from: swagger-document
  where: '$.paths["/enrichment/anomalyDetection/configurations/{configurationId}/series/query"].post'
  transform: >
    $["x-ms-pageable"] = {"nextLinkName": null};
```

### Make get_metric_data pageable

```yaml
directive:
- from: swagger-document
  where: '$.paths["/metrics/{metricId}/data/query"].post'
  transform: >
    $["x-ms-pageable"] = {"nextLinkName": null};
```

### createMetricFeedback -> addFeedback

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/feedback/metric"]["post"]
  transform: >
    $["operationId"] = "addFeedback";
```

### getMetricFeedback -> getFeedback

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/feedback/metric/{feedbackId}"]["get"]
  transform: >
    $["operationId"] = "getFeedback";
```

### listMetricFeedbacks -> listFeedback

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/feedback/metric/query"]["post"]
  transform: >
    $["operationId"] = "listFeedback";
```

### getRootCauseOfIncidentByAnomalyDetectionConfiguration -> listIncidentRootCauses

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/enrichment/anomalyDetection/configurations/{configurationId}/incidents/{incidentId}/rootCause"]["get"]
  transform: >
    $["operationId"] = "listIncidentRootCauses";
```

### getSeriesByAnomalyDetectionConfiguration -> listMetricEnrichedSeriesData

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/enrichment/anomalyDetection/configurations/{configurationId}/series/query"]["post"]
  transform: >
    $["operationId"] = "listMetricEnrichedSeriesData";
```

### getAlertsByAnomalyAlertingConfiguration -> listAlerts

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/alert/anomaly/configurations/{configurationId}/alerts/query"]["post"]
  transform: >
    $["operationId"] = "listAlerts";
```

### getDimensionOfAnomaliesByAnomalyDetectionConfiguration -> listAnomalyDimensionValues

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/enrichment/anomalyDetection/configurations/{configurationId}/anomalies/dimension/query"]["post"]
  transform: >
    $["operationId"] = "listAnomalyDimensionValues";
```

### getMetricDimension -> listMetricDimensionValues

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/metrics/{metricId}/dimension/query"]["post"]
  transform: >
    $["operationId"] = "listMetricDimensionValues";
```

### getMetricData -> listMetricSeriesData

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/metrics/{metricId}/data/query"]["post"]
  transform: >
    $["operationId"] = "listMetricSeriesData";
```

### getMetricSeries -> listMetricSeriesDefinitions

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/metrics/{metricId}/series/query"]["post"]
  transform: >
    $["operationId"] = "listMetricSeriesDefinitions";
```

### getEnrichmentStatusByMetric -> listMetricEnrichmentStatus

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/metrics/{metricId}/status/enrichment/anomalyDetection/query"]["post"]
  transform: >
    $["operationId"] = "listMetricEnrichmentStatus";
```




### createAnomalyAlertingConfiguration -> createAlertingConfiguration

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/alert/anomaly/configurations"]["post"]
  transform: >
    $["operationId"] = "createAlertingConfiguration";
```

### createAnomalyDetectionConfiguration -> createDetectionConfiguration

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/enrichment/anomalyDetection/configurations"]["post"]
  transform: >
    $["operationId"] = "createDetectionConfiguration";
```

### getDataFeedById -> getDataFeed

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/dataFeeds/{dataFeedId}"]["get"]
  transform: >
    $["operationId"] = "getDataFeed";
```

### getAnomalyAlertingConfiguration -> getAlertConfiguration

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/alert/anomaly/configurations/{configurationId}"]["get"]
  transform: >
    $["operationId"] = "getAlertConfiguration";
```

### getAnomalyDetectionConfiguration -> getDetectionConfiguration

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/metrics/{metricId}/enrichment/anomalyDetection/configurations"]["get"]
  transform: >
    $["operationId"] = "getDetectionConfiguration";
```

### getIngestionProgress -> getDataFeedIngestionProgress

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/dataFeeds/{dataFeedId}/ingestionProgress"]["get"]
  transform: >
    $["operationId"] = "getDataFeedIngestionProgress";
```

### resetDataFeedIngestionStatus -> refreshDataFeedIngestion

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/dataFeeds/{dataFeedId}/ingestionProgress/reset"]["post"]
  transform: >
    $["operationId"] = "refreshDataFeedIngestion";
```

### deleteAnomalyAlertingConfiguration -> deleteAlertConfiguration

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/alert/anomaly/configurations/{configurationId}"]["delete"]
  transform: >
    $["operationId"] = "deleteAlertConfiguration";
```


### deleteAnomalyDetectionConfiguration -> deleteDetectionConfiguration

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/enrichment/anomalyDetection/configurations/{configurationId}"]["delete"]
  transform: >
    $["operationId"] = "deleteDetectionConfiguration";
```

### updateAnomalyAlertingConfiguration -> updateAlertConfiguration

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/alert/anomaly/configurations/{configurationId}"]["patch"]
  transform: >
    $["operationId"] = "updateAlertConfiguration";
```

### updateAnomalyDetectionConfiguration -> updateDetectionConfiguration

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/enrichment/anomalyDetection/configurations/{configurationId}"]["patch"]
  transform: >
    $["operationId"] = "updateDetectionConfiguration";
```

### getAnomalyAlertingConfigurationsByAnomalyDetectionConfiguration -> listAlertConfigurations

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/enrichment/anomalyDetection/configurations/{configurationId}/alert/anomaly/configurations"]["get"]
  transform: >
    $["operationId"] = "listAlertConfigurations";
```

### getAnomalyDetectionConfigurationsByMetric -> listDetectionConfigurations

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/metrics/{metricId}/enrichment/anomalyDetection/configurations"]["get"]
  transform: >
    $["operationId"] = "listDetectionConfigurations";
```

### getDataFeedIngestionStatus -> listDataFeedIngestionStatus

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/dataFeeds/{dataFeedId}/ingestionStatus/query"]["post"]
  transform: >
    $["operationId"] = "listDataFeedIngestionStatus";
```


### getCredential -> getDatasourceCredential

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/credentials/{credentialId}"]["get"]
  transform: >
    $["operationId"] = "getDatasourceCredential";
```

### createCredential -> createDatasourceCredential

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/credentials"]["post"]
  transform: >
    $["operationId"] = "createDatasourceCredential";
```


### listCredentials -> listDatasourceCredentials

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/credentials"]["get"]
  transform: >
    $["operationId"] = "listDatasourceCredentials";
```

### updateCredential -> updateDatasourceCredential

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/credentials/{credentialId}"]["patch"]
  transform: >
    $["operationId"] = "updateDatasourceCredential";
```

### deleteCredential -> deleteDatasourceCredential

```yaml
directive:
- from: swagger-document
  where: $["paths"]["/credentials/{credentialId}"]["delete"]
  transform: >
    $["operationId"] = "deleteDatasourceCredential";
```

### anomalyScopeType enum -> metricAnomalyAlertScopeType, change enum values

```yaml
directive:
- from: swagger-document
  where: $["definitions"]["MetricAlertingConfiguration"]["properties"]["anomalyScopeType"]
  transform: >
    $["x-ms-enum"]["name"] = "metricAnomalyAlertScopeType";
    $["enum"] = ["WholeSeries", "SeriesGroup", "TopN"];
```

### NeedRollupEnum -> DataFeedRollupType, change enum values

```yaml
directive:
- from: swagger-document
  where: $["definitions"]["DataFeedDetail"]["properties"]["needRollup"]
  transform: >
    $["x-ms-enum"]["name"] = "DataFeedRollupType";
    $["enum"] = ["NoRollup", "AutoRollup", "AlreadyRollup"];
```
