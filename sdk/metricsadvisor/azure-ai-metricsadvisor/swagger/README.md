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
want-operation-metadata: false
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

### createAnomalyAlertingConfiguration -> createAlertConfiguration

```yaml
directive:
  - from: swagger-document
    where: $["paths"]["/alert/anomaly/configurations"]["post"]
    transform: >
      $["operationId"] = "createAlertConfiguration";
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
    where: $["definitions"]["DataFeed"]["properties"]["needRollup"]
    transform: >
      $["x-ms-enum"]["name"] = "DataFeedRollupType";
      $["enum"] = ["NoRollup", "AutoRollup", "AlreadyRollup"];
```

### MetricAlertingConfiguration -> MetricAlertConfiguration

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["MetricAlertingConfiguration"]
    transform: >
      $["x-ms-client-name"] = "MetricAlertConfiguration";
```

### Severity -> AnomalySeverity

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]
    transform: >
      $["SeverityCondition"]["properties"]["minAlertSeverity"]["x-ms-enum"]["name"] = "AnomalySeverity";
      $["SeverityCondition"]["properties"]["maxAlertSeverity"]["x-ms-enum"]["name"] = "AnomalySeverity";
      $["AnomalyProperty"]["properties"]["anomalySeverity"]["x-ms-enum"]["name"] = "AnomalySeverity";
      $["IncidentProperty"]["properties"]["maxSeverity"]["x-ms-enum"]["name"] = "AnomalySeverity";
      $["SeverityFilterCondition"]["properties"]["min"]["x-ms-enum"]["name"] = "AnomalySeverity";
      $["SeverityFilterCondition"]["properties"]["max"]["x-ms-enum"]["name"] = "AnomalySeverity";
```

### DataSourceType -> DatasourceType

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]
    transform: >
      $["DataFeedDetail"]["properties"]["dataSourceType"]["x-ms-enum"]["name"] = "DatasourceType";
      $["DataFeedDetailPatch"]["properties"]["dataSourceType"]["x-ms-enum"]["name"] = "DatasourceType";
```

### ViewMode -> DataFeedAccessMode

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]
    transform: >
      $["DataFeedDetail"]["properties"]["viewMode"]["x-ms-enum"]["name"] = "DataFeedAccessMode";
      $["DataFeedDetailPatch"]["properties"]["viewMode"]["x-ms-enum"]["name"] = "DataFeedAccessMode";
```

### RollUpMethod -> DataFeedAutoRollupMethod

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]
    transform: >
      $["DataFeedDetail"]["properties"]["rollUpMethod"]["x-ms-enum"]["name"] = "DataFeedAutoRollupMethod";
      $["DataFeedDetailPatch"]["properties"]["rollUpMethod"]["x-ms-enum"]["name"] = "DataFeedAutoRollupMethod";
```

### FillMissingPointType -> DatasourceMissingDataPointFillType

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]
    transform: >
      $["DataFeedDetail"]["properties"]["fillMissingPointType"]["x-ms-enum"]["name"] = "DatasourceMissingDataPointFillType";
      $["DataFeedDetailPatch"]["properties"]["fillMissingPointType"]["x-ms-enum"]["name"] = "DatasourceMissingDataPointFillType";
```

### IncidentStatus -> AnomalyIncidentStatus

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["IncidentProperty"]["properties"]["incidentStatus"]["x-ms-enum"]
    transform: >
      $["name"] = "AnomalyIncidentStatus";
```

### Granularity -> DataFeedGranularityType

```yaml
directive:
  - from: swagger-document
    where: $["paths"]["/dataFeeds"]["get"]["parameters"][2]["x-ms-enum"]
    transform: >
      $["name"] = "DataFeedGranularityType";
```

### EntityStatus -> DataFeedStatus

```yaml
directive:
  - from: swagger-document
    where: $["paths"]
    transform: >
      $["/dataFeeds"]["get"]["parameters"][3]["x-ms-enum"]["name"] = "DataFeedStatus";
```

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]
    transform: >
      $["DataFeedDetail"]["properties"]["status"]["x-ms-enum"]["name"] = "DataFeedStatus";
      $["DataFeedDetailPatch"]["properties"]["status"]["x-ms-enum"]["name"] = "DataFeedStatus";
```

### TimeMode -> AlertQueryTimeMode

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["AlertingResultQuery"]["properties"]["timeMode"]["x-ms-enum"]
    transform: >
      $["name"] = "AlertQueryTimeMode";
```

### DataSourceCredentialType -> DatasourceCredentialType

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]
    transform: >
      $["DataSourceCredential"]["properties"]["dataSourceCredentialType"]["x-ms-enum"]["name"] = "DatasourceCredentialType";
      $["DataSourceCredentialPatch"]["properties"]["dataSourceCredentialType"]["x-ms-enum"]["name"] = "DatasourceCredentialType";
```

### AuthenticationTypeEnum -> DatasourceAuthenticationType

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]
    transform: >
      $["DataFeedDetail"]["properties"]["authenticationType"]["x-ms-enum"]["name"] = "DatasourceAuthenticationType";
      $["DataFeedDetailPatch"]["properties"]["authenticationType"]["x-ms-enum"]["name"] = "DatasourceAuthenticationType";
```

### MetricSeriesItem -> MetricSeriesDefinition

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["MetricSeriesItem"]
    transform: >
      $["x-ms-client-name"] = "MetricSeriesDefinition";
```

### IngestionStatus -> DataFeedIngestionStatus

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["IngestionStatus"]
    transform: >
      $["x-ms-client-name"] = "DataFeedIngestionStatus";
```

### AlertSnoozeCondition -> MetricAnomalyAlertSnoozeCondition

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["AlertSnoozeCondition"]
    transform: >
      $["x-ms-client-name"] = "MetricAnomalyAlertSnoozeCondition";
```

### AnomalyAlertingConfiguration -> AnomalyAlertConfiguration

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["AnomalyAlertingConfiguration"]
    transform: >
      $["x-ms-client-name"] = "AnomalyAlertConfiguration";
```

### DataFeedDetail -> DataFeedSource

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["DataFeedDetail"]
    transform: >
      $["x-ms-client-name"] = "DataFeedSource";
```

### AzureApplicationInsightsDataFeed -> AzureApplicationInsightsDataFeedSource

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["AzureApplicationInsightsDataFeed"]
    transform: >
      $["x-ms-client-name"] = "AzureApplicationInsightsDataFeedSource";
```

### AzureBlobDataFeed -> AzureBlobDataFeedSource

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["AzureBlobDataFeed"]
    transform: >
      $["x-ms-client-name"] = "AzureBlobDataFeedSource";
```

### AzureBlobDataFeed -> AzureCosmosDbDataFeedSource

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["AzureCosmosDBDataFeed"]
    transform: >
      $["x-ms-client-name"] = "AzureCosmosDbDataFeedSource";
```

### AzureDataExplorerDataFeed -> AzureDataExplorerDataFeedSource

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["AzureDataExplorerDataFeed"]
    transform: >
      $["x-ms-client-name"] = "AzureDataExplorerDataFeedSource";
```

### AzureTableDataFeed -> AzureTableDataFeedSource

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["AzureTableDataFeed"]
    transform: >
      $["x-ms-client-name"] = "AzureTableDataFeedSource";
```

### AzureEventHubsDataFeed -> AzureEventHubsDataFeedSource

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["AzureEventHubsDataFeed"]
    transform: >
      $["x-ms-client-name"] = "AzureEventHubsDataFeedSource";
```

### InfluxDBDataFeed -> InfluxDbDataFeedSource

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["InfluxDBDataFeed"]
    transform: >
      $["x-ms-client-name"] = "InfluxDbDataFeedSource";
```

### MySqlDataFeed -> MySqlDataFeedSource

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["MySqlDataFeed"]
    transform: >
      $["x-ms-client-name"] = "MySqlDataFeedSource";
```

### PostgreSqlDataFeed -> PostgreSqlDataFeedSource

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["PostgreSqlDataFeed"]
    transform: >
      $["x-ms-client-name"] = "PostgreSqlDataFeedSource";
```

### SQLServerDataFeed -> SqlServerDataFeedSource

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["SQLServerDataFeed"]
    transform: >
      $["x-ms-client-name"] = "SqlServerDataFeedSource";
```

### AzureDataLakeStorageGen2DataFeed -> AzureDataLakeStorageGen2DataFeedSource

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["AzureDataLakeStorageGen2DataFeed"]
    transform: >
      $["x-ms-client-name"] = "AzureDataLakeStorageGen2DataFeedSource";
```

### AzureLogAnalyticsDataFeed -> AzureLogAnalyticsDataFeedSource

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["AzureLogAnalyticsDataFeed"]
    transform: >
      $["x-ms-client-name"] = "AzureLogAnalyticsDataFeedSource";
```

### MongoDBDataFeed -> MongoDbDataFeedSource

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["MongoDBDataFeed"]
    transform: >
      $["x-ms-client-name"] = "MongoDbDataFeedSource";
```

### HookInfo -> NotificationHook

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["HookInfo"]
    transform: >
      $["x-ms-client-name"] = "NotificationHook";
```

### EmailHookInfo -> EmailNotificationHook

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["EmailHookInfo"]
    transform: >
      $["x-ms-client-name"] = "EmailNotificationHook";
```

### WebhookHookInfo -> WebNotificationHook

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["WebhookHookInfo"]
    transform: >
      $["x-ms-client-name"] = "WebNotificationHook";
```

### WholeMetricConfiguration -> MetricDetectionCondition

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["WholeMetricConfiguration"]
    transform: >
      $["x-ms-client-name"] = "MetricDetectionCondition";
```

### DimensionGroupConfiguration -> MetricSeriesGroupDetectionCondition

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["DimensionGroupConfiguration"]
    transform: >
      $["x-ms-client-name"] = "MetricSeriesGroupDetectionCondition";
```

### SeriesConfiguration -> MetricSingleSeriesDetectionCondition

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["SeriesConfiguration"]
    transform: >
      $["x-ms-client-name"] = "MetricSingleSeriesDetectionCondition";
```

### Metric -> DataFeedMetric

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["Metric"]
    transform: >
      $["x-ms-client-name"] = "DataFeedMetric";
```

### Dimension -> DataFeedDimension

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["Dimension"]
    transform: >
      $["x-ms-client-name"] = "DataFeedDimension";
```

### SeriesResult -> MetricEnrichedSeriesData

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["SeriesResult"]
    transform: >
      $["x-ms-client-name"] = "MetricEnrichedSeriesData";
```

### AlertResult -> AnomalyAlert

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["AlertResult"]
    transform: >
      $["x-ms-client-name"] = "AnomalyAlert";
```

### AnomalyResult -> DataPointAnomaly

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["AnomalyResult"]
    transform: >
      $["x-ms-client-name"] = "DataPointAnomaly";
```

### IncidentResult -> AnomalyIncident

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["IncidentResult"]
    transform: >
      $["x-ms-client-name"] = "AnomalyIncident";
```

### RootCause -> IncidentRootCause

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["RootCause"]
    transform: >
      $["x-ms-client-name"] = "IncidentRootCause";
```

### AzureSQLConnectionStringCredential -> DatasourceSqlConnectionString

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["AzureSQLConnectionStringCredential"]
    transform: >
      $["x-ms-client-name"] = "DatasourceSqlConnectionString";
```

### DataLakeGen2SharedKeyCredential -> DatasourceDataLakeGen2SharedKey

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["DataLakeGen2SharedKeyCredential"]
    transform: >
      $["x-ms-client-name"] = "DatasourceDataLakeGen2SharedKey";
```

### ServicePrincipalCredential -> DatasourceDataLakeGen2SharedKey

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["ServicePrincipalCredential"]
    transform: >
      $["x-ms-client-name"] = "DatasourceServicePrincipal";
```

### ServicePrincipalInKVCredential -> DatasourceServicePrincipalInKeyVault

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["ServicePrincipalInKVCredential"]
    transform: >
      $["x-ms-client-name"] = "DatasourceServicePrincipalInKeyVault";
```
