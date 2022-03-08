# Azure Metrics Advisor for Python

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
output-folder: ../azure/ai/metricsadvisor/
namespace: azure.ai.metricsadvisor
package-name: azure-ai-metricsadvisor
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
python: true
title: MetricsAdvisorClient
head-as-boolean: true
package-version: 1.1.0
add-credential: true
credential-scopes: https://cognitiveservices.azure.com/.default
want-operation-metadata: false
keep-version-file: true
version-tolerant: true
black: true
models-mode: msrest
modelerfour:
    flatten-models: true
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
  - rename-operation:
      from: updateAnomalyDetectionConfiguration
      to: updateDetectionConfiguration
  - rename-operation:
      from: getAnomaliesFromAlertByAnomalyAlertingConfiguration
      to: listAnomaliesForAlert
  - rename-operation:
      from: getIncidentsFromAlertByAnomalyAlertingConfiguration
      to: listIncidentsForAlert
```

### Add empty Anything object to definitions

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]
    transform: >
      $["Anything"] = {}
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

### AnomalyDetectionConfigurationLogicType -> DetectionConditionOperator

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]
    transform: >
      $["WholeMetricConfiguration"]["properties"]["conditionOperator"]["x-ms-enum"]["name"] = "DetectionConditionOperator";
      $["DimensionGroupConfiguration"]["properties"]["conditionOperator"]["x-ms-enum"]["name"] = "DetectionConditionOperator";
      $["SeriesConfiguration"]["properties"]["conditionOperator"]["x-ms-enum"]["name"] = "DetectionConditionOperator";
      $["WholeMetricConfigurationPatch"]["properties"]["conditionOperator"]["x-ms-enum"]["name"] = "DetectionConditionOperator";
```

### DataSourceType -> DatasourceType

```yaml
directive:
  - from: swagger-document
    where: $["paths"]
    transform: >
      $["/dataFeeds"]["get"]["parameters"][1]["x-ms-enum"]["name"] = "DatasourceType";
  - from: swagger-document
    where: $["definitions"]
    transform: >
      $["DataFeedDetail"]["properties"]["dataSourceType"]["x-ms-enum"]["name"] = "DatasourceType";
      $["DataFeedDetailPatch"]["properties"]["dataSourceType"]["x-ms-enum"]["name"] = "DatasourceType";
```

### AnomalyAlertingConfigurationLogicType -> MetricAnomalyAlertConfigurationsOperator

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]
    transform: >
      $["AnomalyAlertingConfiguration"]["properties"]["crossMetricsOperator"]["x-ms-enum"]["name"] = "MetricAnomalyAlertConfigurationsOperator";
```

### ViewMode -> DataFeedAccessMode

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]
    transform: >
      $["DataFeedDetail"]["properties"]["viewMode"]["x-ms-enum"]["name"] = "DataFeedAccessMode";
```

### RollUpMethod -> DataFeedAutoRollupMethod

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]
    transform: >
      $["DataFeedDetail"]["properties"]["rollUpMethod"]["x-ms-enum"]["name"] = "DataFeedAutoRollupMethod";
```

### FillMissingPointType -> DatasourceMissingDataPointFillType

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]
    transform: >
      $["DataFeedDetail"]["properties"]["fillMissingPointType"]["x-ms-enum"]["name"] = "DatasourceMissingDataPointFillType";
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
  - from: swagger-document
    where: $["definitions"]["DataFeedDetail"]["properties"]["granularityName"]["x-ms-enum"]
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
```

### DataSourceCredentialType -> DatasourceCredentialType

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]
    transform: >
      $["DataSourceCredential"]["properties"]["dataSourceCredentialType"]["x-ms-enum"]["name"] = "DatasourceCredentialType";
```

### DataSourceCredential -> DatasourceCredential

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]
    transform: >
      $["DataSourceCredential"]["x-ms-client-name"] = "DatasourceCredential";
```

### AuthenticationTypeEnum -> DatasourceAuthenticationType

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]
    transform: >
      $["DataFeedDetail"]["properties"]["authenticationType"]["x-ms-enum"]["name"] = "DatasourceAuthenticationType";
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
      to: DataFeed
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
  - rename-model:
      from: AzureApplicationInsightsParameter
      to: AzureApplicationInsightsDataFeedSource
  - rename-model:
      from: AzureBlobParameter
      to: AzureBlobDataFeedSource
  - rename-model:
      from: AzureCosmosDBParameter
      to: AzureCosmosDbDataFeedSource
  - rename-model:
      from: SqlSourceParameter
      to: AzureDataExplorerDataFeedSource
  - rename-model:
      from: AzureTableParameter
      to: AzureTableDataFeedSource
  - rename-model:
      from: AzureEventHubsParameter
      to: AzureEventHubsDataFeedSource
  - rename-model:
      from: InfluxDBParameter
      to: InfluxDbDataFeedSource
  - rename-model:
      from: AzureDataLakeStorageGen2Parameter
      to: AzureDataLakeStorageGen2DataFeedSource
  - rename-model:
      from: AzureLogAnalyticsParameter
      to: AzureLogAnalyticsDataFeedSource
  - rename-model:
      from: MongoDBParameter
      to: MongoDbDataFeedSource
  - rename-model:
      from: MetricAlertingConfiguration
      to: MetricAlertConfiguration
  - rename-model:
      from: ValueCondition
      to: MetricBoundaryCondition
  - rename-model:
      from: MetricDataItem
      to: MetricSeriesData
```

### Change DimensionGroupIdentity just for MetricSeriesGroupDetectionCondition

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["MetricSeriesGroupDetectionCondition"]
    transform: >
        $.properties["group"] = {"required": ["dimension"], "type": "object", "properties": { "dimension": { "x-ms-client-name": "seriesGroupKey", "description": "dimension specified for series group", "type": "object", "additionalProperties": { "type": "string" }}}};
```

### Change SeriesIdentity just for AnomalyIncident

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["AnomalyIncident"]
    transform: >
        $.properties["rootNode"] = {"required": ["dimension"], "type": "object", "properties": { "dimension": { "x-ms-client-name": "dimensionKey", "description": "dimension specified for series group", "type": "object", "additionalProperties": { "type": "string" }}}};
```

### Change SeriesIdentity just for MetricSingleSeriesDetectionCondition

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["MetricSingleSeriesDetectionCondition"]
    transform: >
        $.properties["series"] = {"required": ["dimension"], "type": "object", "properties": { "dimension": { "x-ms-client-name": "seriesKey", "description": "dimension specified for series group", "type": "object", "additionalProperties": { "type": "string" }}}};
```

### Change SeriesIdentity just for MetricEnrichedSeriesData

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["MetricEnrichedSeriesData"]
    transform: >
        $.properties["series"] = {"required": ["dimension"], "type": "object", "properties": { "dimension": { "x-ms-client-name": "seriesKey", "description": "dimension specified for series group", "type": "object", "additionalProperties": { "type": "string" }}}};
```

### Change SeriesKey just for MetricSeriesData

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["MetricSeriesData"]
    transform: >
        $.properties["id"] = {"type": "object", "properties": { "dimension": { "x-ms-client-name": "seriesKey", "description": "dimension specified for series group", "type": "object", "additionalProperties": { "type": "string" }}, "metricId": {"format": "uuid", "type": "string", "readOnly": true}}};
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

### anomalyScopeType enum -> metricAnomalyAlertScopeType, change enum values

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["MetricAlertConfiguration"]["properties"]["anomalyScopeType"]
    transform: >
      $["x-ms-enum"]["name"] = "MetricAnomalyAlertScopeType";
```

### NeedRollupEnum -> DataFeedRollupType, change enum values

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]
    transform: >
      $["DataFeed"]["properties"]["needRollup"]["x-ms-enum"]["name"] = "DataFeedRollupType";
```

```yaml
declare-directive:
  where-parameter: >-
    (() => {
      switch ($context.from) {
        case "code-model-v1":
          throw "not implemented";

        case "code-model-v3":
          return {from: "code-model-v3", where: `$.parameters.filter(p => p["name"] == ${JSON.stringify($)})[0]`};

        case "openapi-document":
          return { from: "openapi-document", where: `$.parameters.filter(p => p["name"] == ${JSON.stringify($)})[0]` };

        case "swagger-document":
        default:
          return { from: "swagger-document", where: `$.parameters.filter(p => p["name"] == ${JSON.stringify($)})[0]` };
      }
    })()
```

```yaml
declare-directive:
    change-parameter-schema: >-
        [{
        from: 'swagger-document',
        transform: `$.schema["$ref"] = "#/definitions/" + JSON.stringify($)`
        },
        {
        from: 'openapi-document',
        transform: `$.schema["$ref"] = "#/definitions/" + JSON.stringify($)`
        }]
```

### Change parameter types

```yaml
directive:
  - where-operation: updateHook
    transform: >
      $["parameters"][1]["schema"]["$ref"] = "#/definitions/Anything";
  - where-operation: updateDetectionConfiguration
    transform: >
      $["parameters"][1]["schema"]["$ref"] = "#/definitions/Anything";
  - where-operation: listAlerts
    transform: >
      $["parameters"][3]["schema"]["$ref"] = "#/definitions/Anything";
  - where-operation: listMetricSeriesData
    transform: >
      $["parameters"][1]["schema"]["$ref"] = "#/definitions/Anything";
  - where-operation: listMetricDimensionValues
    transform: >
      $["parameters"][3]["schema"]["$ref"] = "#/definitions/Anything";
  - where-operation: listMetricSeriesDefinitions
    transform: >
      $["parameters"][3]["schema"]["$ref"] = "#/definitions/Anything";
  - where-operation: updateAlertConfiguration
    transform: >
      $["parameters"][1]["schema"]["$ref"] = "#/definitions/Anything";
  - where-operation: updateDatasourceCredential
    transform: >
      $["parameters"][1]["schema"]["$ref"] = "#/definitions/Anything";
  - where-operation: updateDataFeed
    transform: >
      $["parameters"][1]["schema"]["$ref"] = "#/definitions/Anything";
  - where-operation: listAnomalyDimensionValues
    transform: >
      $["parameters"][3]["schema"]["$ref"] = "#/definitions/Anything";
  - where-operation: getAnomaliesByAnomalyDetectionConfiguration
    transform: >
      $["parameters"][3]["schema"]["$ref"] = "#/definitions/Anything";
  - where-operation: getIncidentsByAnomalyDetectionConfiguration
    transform: >
      $["parameters"][2]["schema"]["$ref"] = "#/definitions/Anything";
  - where-operation: listMetricEnrichedSeriesData
    transform: >
      $["parameters"][1]["schema"]["$ref"] = "#/definitions/Anything";
  - where-operation: listMetricEnrichmentStatus
    transform: >
      $["parameters"][3]["schema"]["$ref"] = "#/definitions/Anything";
  - where-operation: listFeedback
    transform: >
      $["parameters"][2]["schema"]["$ref"] = "#/definitions/Anything";
  - where-operation: refreshDataFeedIngestion
    transform: >
      $["parameters"][1]["schema"]["$ref"] = "#/definitions/Anything";
  - where-operation: listDataFeedIngestionStatus
    transform: >
      $["parameters"][3]["schema"]["$ref"] = "#/definitions/Anything";
```

### Change Property Types

```yaml
directive:
  - where-model: MetricBoundaryCondition
    transform: >
      $["properties"]["direction"]["x-ms-enum"] = undefined;
      $["properties"]["direction"]["enum"] = undefined;
  - where-model: AnomalyAlertingConfiguration
    transform: >
      $["properties"]["crossMetricsOperator"]["x-ms-enum"] = undefined;
      $["properties"]["crossMetricsOperator"]["enum"] = undefined;
  - where-model: AnomalyProperty
    transform: >
      $["properties"]["anomalyStatus"]["x-ms-enum"] = undefined;
      $["properties"]["anomalyStatus"]["enum"] = undefined;
  - where-model: NotificationHook
    transform: >
      $["properties"]["hookType"]["x-ms-enum"] = undefined;
      $["properties"]["hookType"]["enum"] = undefined;
  - where-model: DataFeedIngestionStatus
    transform: >
      $["properties"]["status"]["x-ms-enum"] = undefined;
      $["properties"]["status"]["enum"] = undefined;
```

### Change Response Types

```yaml
directive:
  - where-operation: updateDataFeed
    transform: >
      $["responses"]["200"]["schema"]["$ref"] = "#/definitions/Anything";
  - where-operation: getDatasourceCredential
    transform: >
      $["responses"]["200"]["schema"]["$ref"] = "#/definitions/Anything";
  - where-operation: updateDatasourceCredential
    transform: >
      $["responses"]["200"]["schema"]["$ref"] = "#/definitions/Anything";
```

### Remove ErrorCode

```yaml
directive:
  - from: swagger-document
    where: $["paths"][*]
    transform: >
      for (var op of Object.values($)) {
          op["responses"]["default"]["schema"]["$ref"] = "#/definitions/Anything";
      }
```

### Remove Models

```yaml
directive:
  - remove-model: HookInfoPatch
  - remove-model: EmailHookInfoPatch
  - remove-model: WebhookHookInfoPatch
  - remove-model: AzureApplicationInsightsDataFeed
  - remove-model: AzureApplicationInsightsDataFeedPatch
  - remove-model: AzureBlobDataFeed
  - remove-model: AzureBlobDataFeedPatch
  - remove-model: AzureCosmosDBDataFeed
  - remove-model: AzureCosmosDBDataFeedPatch
  - remove-model: AzureDataExplorerDataFeed
  - remove-model: AzureDataExplorerDataFeedPatch
  - remove-model: AzureTableDataFeed
  - remove-model: AzureTableDataFeedPatch
  - remove-model: AzureEventHubsDataFeed
  - remove-model: AzureEventHubsDataFeedPatch
  - remove-model: InfluxDBDataFeed
  - remove-model: InfluxDBDataFeedPatch
  - remove-model: MySqlDataFeed
  - remove-model: MySqlDataFeedPatch
  - remove-model: PostgreSqlDataFeed
  - remove-model: PostgreSqlDataFeedPatch
  - remove-model: SQLServerDataFeed
  - remove-model: SQLServerDataFeedPatch
  - remove-model: AzureDataLakeStorageGen2DataFeed
  - remove-model: AzureDataLakeStorageGen2DataFeedPatch
  - remove-model: AzureLogAnalyticsDataFeed
  - remove-model: AzureLogAnalyticsDataFeedPatch
  - remove-model: MongoDBDataFeed
  - remove-model: MongoDBDataFeedPatch
  - remove-model: AzureApplicationInsightsParameterPatch
  - remove-model: AzureBlobParameterPatch
  - remove-model: AzureCosmosDBParameterPatch
  - remove-model: AzureTableParameterPatch
  - remove-model: AzureEventHubsParameterPatch
  - remove-model: InfluxDBParameterPatch
  - remove-model: SQLSourceParameterPatch
  - remove-model: AzureDataLakeStorageGen2ParameterPatch
  - remove-model: AzureLogAnalyticsParameterPatch
  - remove-model: MongoDBParameterPatch
  - remove-model: SuppressConditionPatch
  - remove-model: SmartDetectionConditionPatch
  - remove-model: HardThresholdConditionPatch
  - remove-model: ChangeThresholdConditionPatch
  - remove-model: AnomalyDetectionConfigurationPatch
  - remove-model: WholeMetricConfigurationPatch
  - remove-model: AlertingResultQuery
  - remove-model: MetricDataQueryOptions
  - remove-model: MetricDimensionQueryOptions
  - remove-model: MetricSeriesQueryOptions
  - remove-model: ServicePrincipalCredentialPatch
  - remove-model: ServicePrincipalInKVCredentialPatch
  - remove-model: ServicePrincipalInKVParamPatch
  - remove-model: ServicePrincipalParamPatch
  - remove-model: WebhookHookInfoPatch
  - remove-model: WebhookHookParameterPatch
  - remove-model: AnomalyAlertingConfigurationPatch
  - remove-model: DataSourceCredentialPatch
  - remove-model: AzureSQLConnectionStringCredentialPatch
  - remove-model: AzureSQLConnectionStringParamPatch
  - remove-model: DataFeedDetailPatch
  - remove-model: DataLakeGen2SharedKeyCredentialPatch
  - remove-model: DataLakeGen2SharedKeyParamPatch
  - remove-model: EmailHookParameterPatch
  - remove-model: UsageStats
  - remove-model: AnomalyDimensionQuery
  - remove-model: DetectionAnomalyResultQuery
  - remove-model: DetectionIncidentResultQuery
  - remove-model: DetectionSeriesQuery
  - remove-model: EnrichmentStatusQueryOption
  - remove-model: ErrorCode
  - remove-model: MetricFeedbackFilter
  - remove-model: IngestionProgressResetOptions
  - remove-model: IngestionStatusQueryOptions
```

### Remove Operations

```yaml
directive:
  - remove-operation: getActiveSeriesCount
```

### Rename Properties

```yaml
declare-directive:
    rename-property: >-
        [{
        from: 'swagger-document',
        transform: `if ($.properties[${JSON.stringify($.from)}]) { $.properties[${JSON.stringify($.from)}]["x-ms-client-name"] = ${JSON.stringify($.to)}; }`
        },
        {
        from: 'openapi-document',
        transform: `if ($.properties[${JSON.stringify($.from)}]) { $.properties[${JSON.stringify($.from)}]["x-ms-client-name"] = ${JSON.stringify($.to)}; }`
        }]
```

```yaml
directive:
  - where-model: AnomalyAlertConfiguration
    rename-property:
      from: anomalyAlertingConfigurationId
      to: id
  - where-model: AnomalyAlertConfiguration
    rename-property:
      from: metricAlertingConfigurations
      to: metricAlertConfigurations
  - where-model: AnomalyAlertConfiguration
    rename-property:
      from: splitAlertByDimensions
      to: dimensionsToSplitAlert
  - where-model: MetricAlertConfiguration
    rename-property:
      from: anomalyDetectionConfigurationId
      to: detectionConfigurationId
  - where-model: MetricAlertConfiguration
    rename-property:
      from: snoozeFilter
      to: alertSnoozeCondition
  - where-model: FeedbackDimensionFilter
    rename-property:
      from: dimension
      to: dimensionKey
  - where-model: NotificationHook
    rename-property:
      from: hookName
      to: name
  - where-model: NotificationHook
    rename-property:
      from: hookId
      to: id
  - where-model: EmailHookParameter
    rename-property:
      from: toList
      to: emailsToAlert
  - where-model: WebhookHookParameter
    remove-property: headers
  - where-model: DataFeedMetric
    rename-property:
      from: metricName
      to: name
  - where-model: DataFeedMetric
    rename-property:
      from: metricId
      to: id
  - where-model: DataFeedMetric
    rename-property:
      from: metricDisplayName
      to: displayName
  - where-model: DataFeedMetric
    rename-property:
      from: metricDescription
      to: description
  - where-model: DataFeedDimension
    rename-property:
      from: dimensionName
      to: name
  - where-model: DataFeedDimension
    rename-property:
      from: dimensionDisplayName
      to: displayName
  - where-model: DataFeed
    rename-property:
      from: dataFeedName
      to: name
  - where-model: DataFeed
    rename-property:
      from: dataFeedId
      to: id
  - where-model: DataFeed
    rename-property:
      from: viewMode
      to: accessMode
  - where-model: AnomalyDetectionConfiguration
    rename-property:
      from: anomalyDetectionConfigurationId
      to: id
  - where-model: AnomalyDetectionConfiguration
    rename-property:
      from: wholeMetricConfiguration
      to: wholeSeriesDetectionCondition
  - where-model: AnomalyDetectionConfiguration
    rename-property:
      from: dimensionGroupOverrideConfigurations
      to: seriesGroupDetectionConditions
  - where-model: AnomalyDetectionConfiguration
    rename-property:
      from: seriesOverrideConfigurations
      to: seriesDetectionConditions
  - where-model: MetricSeriesGroupDetectionCondition
    rename-property:
      from: seriesOverrideConfigurations
      to: seriesDetectionConditions
  - where-model: MetricBoundaryCondition
    rename-property:
      from: metricId
      to: companionMetricId
  - where-model: MetricFeedback
    rename-property:
      from: feedbackId
      to: id
  - where-model: AnomalyFeedbackValue
    rename-property:
      from: anomalyValue
      to: value
  - where-model: ChangePointFeedbackValue
    rename-property:
      from: changePointValue
      to: value
  - where-model: CommentFeedbackValue
    rename-property:
      from: commentValue
      to: value
  - where-model: PeriodFeedbackValue
    rename-property:
      from: periodValue
      to: value
  - where-model: DataSourceCredential
    rename-property:
      from: dataSourceCredentialType
      to: credentialType
  - where-model: DataSourceCredential
    rename-property:
      from: dataSourceCredentialName
      to: name
  - where-model: DataSourceCredential
    rename-property:
      from: dataSourceCredentialId
      to: id
  - where-model: DataSourceCredential
    rename-property:
      from: dataSourceCredentialDescription
      to: description
  - where-model: AnomalyProperty
    rename-property:
      from: anomalySeverity
      to: severity
  - where-model: AnomalyProperty
    rename-property:
      from: anomalyStatus
      to: status
  - where-model: DataPointAnomaly
    rename-property:
      from: anomalyDetectionConfigurationId
      to: detectionConfigurationId
  - where-model: AnomalyIncident
    rename-property:
      from: anomalyDetectionConfigurationId
      to: detectionConfigurationId
  - where-model: AnomalyIncident
    rename-property:
      from: incidentId
      to: id
  - where-model: IncidentProperty
    rename-property:
      from: maxSeverity
      to: severity
  - where-model: IncidentProperty
    rename-property:
      from: incidentStatus
      to: status
  - where-model: MetricEnrichedSeriesData
    rename-property:
      from: timestampList
      to: timestamps
  - where-model: MetricEnrichedSeriesData
    rename-property:
      from: valueList
      to: values
  - where-model: MetricEnrichedSeriesData
    rename-property:
      from: isAnomalyList
      to: isAnomaly
  - where-model: MetricEnrichedSeriesData
    rename-property:
      from: periodList
      to: periods
  - where-model: MetricEnrichedSeriesData
    rename-property:
      from: expectedValueList
      to: expectedValues
  - where-model: MetricEnrichedSeriesData
    rename-property:
      from: lowerBoundaryList
      to: lowerBounds
  - where-model: MetricEnrichedSeriesData
    rename-property:
      from: upperBoundaryList
      to: upperBounds
  - where-model: AnomalyAlert
    rename-property:
      from: alertId
      to: id
  - where-model: MetricBoundaryCondition
    remove-property: type
  - where-model: MetricSeriesData
    rename-property:
      from: timestampList
      to: timestamps
  - where-model: MetricSeriesData
    rename-property:
      from: valueList
      to: values
```

```yaml
declare-directive:
    make-property-optional: >-
        [{
        from: 'swagger-document',
        transform: `$.required = $.required.filter(item => item !== ${JSON.stringify($)})`
        },
        {
        from: 'openapi-document',
        transform: `$.required = $.required.filter(item => item !== ${JSON.stringify($)})`
        }]
```

```yaml
directive:
  - where-model: NotificationHook
    make-property-optional: hookName
  - where-model: EmailNotificationHook
    make-property-optional: hookParameter
  - where-model: WebNotificationHook
    make-property-optional: hookParameter
  - where-model: WebhookHookParameter
    make-property-optional: endpoint
  - where-model: EmailHookParameter
    make-property-optional: toList
  - where-model: AzureLogAnalyticsDataFeedSource
    make-property-optional: tenantId
  - where-model: AzureLogAnalyticsDataFeedSource
    make-property-optional: clientId
  - where-model: AzureLogAnalyticsDataFeedSource
    make-property-optional: clientSecret
  - where-model: SuppressCondition
    make-property-optional: minNumber
  - where-model: SuppressCondition
    make-property-optional: minRatio
  - where-model: SmartDetectionCondition
    make-property-optional: anomalyDetectorDirection
  - where-model: SmartDetectionCondition
    make-property-optional: sensitivity
  - where-model: SmartDetectionCondition
    make-property-optional: suppressCondition
  - where-model: HardThresholdCondition
    make-property-optional: anomalyDetectorDirection
  - where-model: HardThresholdCondition
    make-property-optional: suppressCondition
  - where-model: ChangeThresholdCondition
    make-property-optional: anomalyDetectorDirection
  - where-model: ChangeThresholdCondition
    make-property-optional: changePercentage
  - where-model: ChangeThresholdCondition
    make-property-optional: shiftPoint
  - where-model: ChangeThresholdCondition
    make-property-optional: suppressCondition
  - where-model: ChangeThresholdCondition
    make-property-optional: withinRange
```

```yaml
declare-directive:
    flatten-property: >-
        [{
        from: 'swagger-document',
        transform: `if ($.properties[${JSON.stringify($)}]) { $.properties[${JSON.stringify($)}]["x-ms-client-flatten"] = true; }`
        },
        {
        from: 'openapi-document',
        transform: `if ($.properties[${JSON.stringify($)}]) { $.properties[${JSON.stringify($)}]["x-ms-client-flatten"] = true; }`
        }]
```

### Flatten properties

```yaml
directive:
  - where-model: EmailNotificationHook
    flatten-property: hookParameter
  - where-model: WebNotificationHook
    flatten-property: hookParameter
  - where-model: MetricSeriesGroupDetectionCondition
    flatten-property: group
  - where-model: MetricSingleSeriesDetectionCondition
    flatten-property: series
  - where-model: MetricFeedback
    flatten-property: dimensionFilter
  - where-model: AnomalyFeedback
    flatten-property: value
  - where-model: ChangePointFeedback
    flatten-property: value
  - where-model: CommentFeedback
    flatten-property: value
  - where-model: PeriodFeedback
    flatten-property: value
  - where-model: DatasourceSqlConnectionString
    flatten-property: parameters
  - where-model: DatasourceDataLakeGen2SharedKey
    flatten-property: parameters
  - where-model: DatasourceServicePrincipal
    flatten-property: parameters
  - where-model: DatasourceServicePrincipalInKeyVault
    flatten-property: parameters
  - where-model: DataPointAnomaly
    flatten-property: property
  - where-model: AnomalyIncident
    flatten-property: rootNode
  - where-model: AnomalyIncident
    flatten-property: property
  - where-model: MetricEnrichedSeriesData
    flatten-property: series
  - where-model: MetricSeriesData
    flatten-property: id
```

```yaml
declare-directive:
    rename-parameter: >-
        [{
        from: 'swagger-document',
        transform: `for (const param in $.parameters) { if (param["name"] == ${JSON.stringify($.from)}) { $[param]["x-ms-client-name"] = ${JSON.stringify($.to)}; } }`
        },
        {
        from: 'openapi-document',
        transform: `for (const param in $.parameters) { if (param["name"] == ${JSON.stringify($.from)}) { $[param]["x-ms-client-name"] = ${JSON.stringify($.to)}; } }`
        }]
```

### Rename parameters

```yaml
directive:
  - where-operation: getDetectionConfiguration
    transform: >
        $.parameters[0]["x-ms-client-name"] = "detectionConfigurationId";
  - where-operation: listIncidentRootCauses
    transform: >
        $.parameters[0]["x-ms-client-name"] = "detectionConfigurationId";
  - where-operation: addFeedback
    transform: >
        $.parameters[0]["x-ms-client-name"] = "feedback";
  - where-operation: listAnomaliesForAlert
    transform: >
        $.parameters[0]["x-ms-client-name"] = "alertConfigurationId";
  - where-operation: listIncidentsForAlert
    transform: >
        $.parameters[0]["x-ms-client-name"] = "alertConfigurationId";
```

### Add DataSourceParameter to DataFeed

```yaml
directive:
  - from: swagger-document
    where: $["definitions"]["DataFeed"]
    transform: >
        $.properties["dataSourceParameter"] = {"type": "object"};
```

```yaml
declare-directive:
    make-not-readonly: >-
        [{
        from: 'swagger-document',
        transform: `if ($.properties[${JSON.stringify($)}]) { $.properties[${JSON.stringify($)}]["readOnly"] = false; }`
        },
        {
        from: 'openapi-document',
        transform: `if ($.properties[${JSON.stringify($)}]) { $.properties[${JSON.stringify($)}]["readOnly"] = false; }`
        }]
```

### Make AnomalyAlertConfiguration id property not readonly

```yaml
directive:
  - where-model: AnomalyAlertConfiguration
    make-not-readonly: anomalyAlertingConfigurationId
  - where-model: DataFeed
    make-not-readonly: status
```
