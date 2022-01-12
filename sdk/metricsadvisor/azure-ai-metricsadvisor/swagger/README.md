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

```yaml
directive:
    - rename-operation:
        from: createMetricFeedback
        to: addFeedback
    - rename-operation:
        from: getMetricFeedback
        to: getFeedback
    - rename-operation:
        from: listMetricFeedbacks
        to: listFeedback
    - rename-operation:
        from: getRootCauseOfIncidentByAnomalyDetectionConfiguration
        to: listIncidentRootCauses
    - rename-operation:
        from: getSeriesByAnomalyDetectionConfiguration
        to: listMetricEnrichedSeriesData
    - rename-operation:
        from: getAlertsByAnomalyAlertingConfiguration
        to: listAlerts
    - rename-operation:
        from: getDimensionOfAnomaliesByAnomalyDetectionConfiguration
        to: listAnomalyDimensionValues
    - rename-operation:
        from: getMetricDimension
        to: listMetricDimensionValues
    - rename-operation:
        from: getMetricData
        to: listMetricSeriesData
    - rename-operation:
        from: getMetricSeries
        to: listMetricSeriesDefinitions
    - rename-operation:
        from: getEnrichmentStatusByMetric
        to: listMetricEnrichmentStatus
    - rename-operation:
        from: createAnomalyAlertingConfiguration
        to: createAlertConfiguration
    - rename-operation:
        from: createAnomalyDetectionConfiguration
        to: createDetectionConfiguration
    - rename-operation:
        from: getDataFeedById
        to: getDataFeed
    - rename-operation:
        from: getAnomalyAlertingConfiguration
        to: getAlertConfiguration
    - rename-operation:
        from: getAnomalyDetectionConfiguration
        to: getDetectionConfiguration
    - rename-operation:
        from: getIngestionProgress
        to: getDataFeedIngestionProgress
    - rename-operation:
        from: resetDataFeedIngestionStatus
        to: refreshDataFeedIngestion
    - rename-operation:
        from: deleteAnomalyAlertingConfiguration
        to: deleteAlertConfiguration
    - rename-operation:
        from: deleteAnomalyDetectionConfiguration
        to: deleteDetectionConfiguration
    - rename-operation:
        from: updateAnomalyAlertingConfiguration
        to: updateAlertConfiguration
    - rename-operation:
        from: getAnomalyAlertingConfigurationsByAnomalyDetectionConfiguration
        to: listAlertConfigurations
    - rename-operation:
        from: getAnomalyDetectionConfigurationsByMetric
        to: listDetectionConfigurations
    - rename-operation:
        from: getDataFeedIngestionStatus
        to: listDataFeedIngestionStatus
    - rename-operation:
        from: getCredential
        to: getDatasourceCredential
    - rename-operation:
        from: createCredential
        to: createDatasourceCredential
    - rename-operation:
        from: listCredentials
        to: listDatasourceCredentials
    - rename-operation:
        from: updateCredential
        to: updateDatasourceCredential
    - rename-operation:
        from: deleteCredential
        to: deleteDatasourceCredential
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

```yaml
declare-directive:
    rename-model: >-
        [{
            from: 'swagger-document',
            where: `$.definitions[${JSON.stringify($.from)}]`,
            transform: `$["x-ms-client-name"] = ${JSON.stringify($.to)}`
        }]
```

### Rename models

```yaml
directive:
    - rename-model:
        from: MetricSeriesItem
        to: MetricSeriesDefinition
    - rename-model:
        from: IngestionStatus
        to: DataFeedIngestionStatus
    - rename-model:
        from: AlertSnoozeCondition
        to: MetricAnomalyAlertSnoozeCondition
    - rename-model:
        from: AnomalyAlertingConfiguration
        to: AnomalyAlertConfiguration
    - rename-model:
        from: DataFeedDetail
        to: DataFeedSource
    - rename-model:
        from: AzureApplicationInsightsDataFeed
        to: AzureApplicationInsightsDataFeedSource
    - rename-model:
        from: AzureBlobDataFeed
        to: AzureBlobDataFeedSource
    - rename-model:
        from: AzureCosmosDBDataFeed
        to: AzureCosmosDbDataFeedSource
    - rename-model:
        from: AzureDataExplorerDataFeed
        to: AzureDataExplorerDataFeedSource
    - rename-model:
        from: AzureTableDataFeed
        to: AzureTableDataFeedSource
    - rename-model:
        from: AzureEventHubsDataFeed
        to: AzureEventHubsDataFeedSource
    - rename-model:
        from: InfluxDBDataFeed
        to: InfluxDbDataFeedSource
    - rename-model:
        from: MySqlDataFeed
        to: MySqlDataFeedSource
    - rename-model:
        from: PostgreSqlDataFeed
        to: PostgreSqlDataFeedSource
    - rename-model:
        from: SQLServerDataFeed
        to: SqlServerDataFeedSource
    - rename-model:
        from: AzureDataLakeStorageGen2DataFeed
        to: AzureDataLakeStorageGen2DataFeedSource
    - rename-model:
        from: AzureLogAnalyticsDataFeed
        to: AzureLogAnalyticsDataFeedSource
    - rename-model:
        from: MongoDBDataFeed
        to: MongoDbDataFeedSource
    - rename-model:
        from: HookInfo
        to: NotificationHook
    - rename-model:
        from: EmailHookInfo
        to: EmailNotificationHook
    - rename-model:
        from: WebhookHookInfo
        to: WebNotificationHook
    - rename-model:
        from: WholeMetricConfiguration
        to: MetricDetectionCondition
    - rename-model:
        from: DimensionGroupConfiguration
        to: MetricSeriesGroupDetectionCondition
    - rename-model:
        from: SeriesConfiguration
        to: MetricSingleSeriesDetectionCondition
    - rename-model:
        from: Metric
        to: DataFeedMetric
    - rename-model:
        from: Dimension
        to: DataFeedDimension
    - rename-model:
        from: SeriesResult
        to: MetricEnrichedSeriesData
    - rename-model:
        from: AlertResult
        to: AnomalyAlert
    - rename-model:
        from: AnomalyResult
        to: DataPointAnomaly
    - rename-model:
        from: IncidentResult
        to: AnomalyIncident
    - rename-model:
        from: RootCause
        to: IncidentRootCause
    - rename-model:
        from: AzureSQLConnectionStringCredential
        to: DatasourceSqlConnectionString
    - rename-model:
        from: DataLakeGen2SharedKeyCredential
        to: DatasourceDataLakeGen2SharedKey
    - rename-model:
        from: ServicePrincipalCredential
        to: DatasourceServicePrincipal
    - rename-model:
        from: ServicePrincipalInKVCredential
        to: DatasourceServicePrincipalInKeyVault
```
