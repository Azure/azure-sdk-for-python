# Release History

## 1.0.0b2 (2026-04-24)

### Features Added

  - Client `CloudHealthMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Enum `DependenciesAggregationType` added member `MAX_NOT_HEALTHY`
  - Enum `DependenciesAggregationType` added member `MIN_HEALTHY`
  - Model `DiscoveryRuleProperties` added property `specification`
  - Model `DiscoveryRuleProperties` added property `error`
  - Model `EntityProperties` added property `tags`
  - Model `EntityProperties` added property `signal_groups`
  - Enum `HealthState` added member `UNHEALTHY`
  - Model `LogAnalyticsQuerySignalDefinitionProperties` added property `tags`
  - Model `PrometheusMetricsSignalDefinitionProperties` added property `tags`
  - Model `RelationshipProperties` added property `tags`
  - Model `ResourceMetricSignalDefinitionProperties` added property `tags`
  - Model `SignalDefinitionProperties` added property `tags`
  - Enum `SignalKind` added member `EXTERNAL_SIGNAL`
  - Enum `SignalOperator` added member `EQUAL`
  - Enum `SignalOperator` added member `GREATER_THAN_OR_EQUAL`
  - Enum `SignalOperator` added member `LESS_THAN`
  - Enum `SignalOperator` added member `LESS_THAN_OR_EQUAL`
  - Enum `SignalOperator` added member `NOT_EQUAL`
  - Added model `ApplicationInsightsTopologySpecification`
  - Added model `AzureMonitorWorkspaceSignals`
  - Added model `AzureResourceSignal`
  - Added model `AzureResourceSignals`
  - Added enum `DependenciesAggregationUnit`
  - Added model `DependenciesSignalGroupV2`
  - Added model `DiscoveryError`
  - Added enum `DiscoveryRuleKind`
  - Added model `DiscoveryRuleSpecification`
  - Added model `EntityHistoryRequest`
  - Added model `EntityHistoryResponse`
  - Added model `ExternalSignal`
  - Added model `ExternalSignalGroup`
  - Added model `HealthReportEvaluationRule`
  - Added model `HealthReportRequest`
  - Added model `HealthStateTransition`
  - Added model `LogAnalyticsSignal`
  - Added model `LogAnalyticsSignals`
  - Added model `PrometheusMetricsSignal`
  - Added model `ResourceGraphQuerySpecification`
  - Added model `SignalGroups`
  - Added model `SignalHistoryDataPoint`
  - Added model `SignalHistoryRequest`
  - Added model `SignalHistoryResponse`
  - Added model `SignalInstanceProperties`
  - Added model `SignalStatus`
  - Added model `ThresholdRuleV2`
  - Operation group `AuthenticationSettingsOperations` added method `begin_create_or_update`
  - Operation group `AuthenticationSettingsOperations` added method `begin_delete`
  - Operation group `DiscoveryRulesOperations` added method `begin_create_or_update`
  - Operation group `DiscoveryRulesOperations` added method `begin_delete`
  - Operation group `EntitiesOperations` added method `begin_create_or_update`
  - Operation group `EntitiesOperations` added method `begin_delete`
  - Operation group `EntitiesOperations` added method `get_history`
  - Operation group `EntitiesOperations` added method `get_signal_history`
  - Operation group `EntitiesOperations` added method `ingest_health_report`
  - Operation group `RelationshipsOperations` added method `begin_create_or_update`
  - Operation group `RelationshipsOperations` added method `begin_delete`
  - Operation group `SignalDefinitionsOperations` added method `begin_create_or_update`
  - Operation group `SignalDefinitionsOperations` added method `begin_delete`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Deleted or renamed enum value `DependenciesAggregationType.THRESHOLDS`
  - Model `DiscoveryRuleProperties` deleted or renamed its instance variable `resource_graph_query`
  - Model `DiscoveryRuleProperties` deleted or renamed its instance variable `deletion_date`
  - Model `DiscoveryRuleProperties` deleted or renamed its instance variable `error_message`
  - Model `DiscoveryRuleProperties` deleted or renamed its instance variable `number_of_discovered_entities`
  - Model `EntityProperties` deleted or renamed its instance variable `kind`
  - Model `EntityProperties` deleted or renamed its instance variable `labels`
  - Model `EntityProperties` deleted or renamed its instance variable `signals`
  - Model `EntityProperties` deleted or renamed its instance variable `deletion_date`
  - Model `EvaluationRule` deleted or renamed its instance variable `dynamic_detection_rule`
  - Model `HealthModelProperties` deleted or renamed its instance variable `dataplane_endpoint`
  - Model `HealthModelProperties` deleted or renamed its instance variable `discovery`
  - Model `HealthModelUpdate` deleted or renamed its instance variable `properties`
  - Deleted or renamed enum value `HealthState.ERROR`
  - Model `LogAnalyticsQuerySignalDefinitionProperties` deleted or renamed its instance variable `labels`
  - Model `LogAnalyticsQuerySignalDefinitionProperties` deleted or renamed its instance variable `deletion_date`
  - Model `PrometheusMetricsSignalDefinitionProperties` deleted or renamed its instance variable `labels`
  - Model `PrometheusMetricsSignalDefinitionProperties` deleted or renamed its instance variable `deletion_date`
  - Model `RelationshipProperties` deleted or renamed its instance variable `labels`
  - Model `RelationshipProperties` deleted or renamed its instance variable `deletion_date`
  - Model `ResourceMetricSignalDefinitionProperties` deleted or renamed its instance variable `labels`
  - Model `ResourceMetricSignalDefinitionProperties` deleted or renamed its instance variable `deletion_date`
  - Model `SignalDefinitionProperties` deleted or renamed its instance variable `labels`
  - Model `SignalDefinitionProperties` deleted or renamed its instance variable `deletion_date`
  - Deleted or renamed enum value `SignalOperator.EQUALS`
  - Deleted or renamed enum value `SignalOperator.GREATER_OR_EQUALS`
  - Deleted or renamed enum value `SignalOperator.LOWER_OR_EQUALS`
  - Deleted or renamed enum value `SignalOperator.LOWER_THAN`
  - Deleted or renamed model `AzureMonitorWorkspaceSignalGroup`
  - Deleted or renamed model `AzureResourceSignalGroup`
  - Deleted or renamed model `DependenciesSignalGroup`
  - Deleted or renamed model `DynamicDetectionRule`
  - Deleted or renamed model `DynamicThresholdDirection`
  - Deleted or renamed model `DynamicThresholdModel`
  - Deleted or renamed model `HealthModelUpdateProperties`
  - Deleted or renamed model `LogAnalyticsSignalGroup`
  - Deleted or renamed model `ModelDiscoverySettings`
  - Deleted or renamed model `SignalAssignment`
  - Deleted or renamed model `SignalGroup`
  - Deleted or renamed model `ThresholdRule`
  - Deleted or renamed method `AuthenticationSettingsOperations.create_or_update`
  - Deleted or renamed method `AuthenticationSettingsOperations.delete`
  - Deleted or renamed method `DiscoveryRulesOperations.create_or_update`
  - Deleted or renamed method `DiscoveryRulesOperations.delete`
  - Deleted or renamed method `EntitiesOperations.create_or_update`
  - Deleted or renamed method `EntitiesOperations.delete`
  - Deleted or renamed method `RelationshipsOperations.create_or_update`
  - Deleted or renamed method `RelationshipsOperations.delete`
  - Deleted or renamed method `SignalDefinitionsOperations.create_or_update`
  - Deleted or renamed method `SignalDefinitionsOperations.delete`

## 1.0.0b1 (2025-06-04)

### Other Changes

  - Initial version
