# Release History

## 8.0.0b2 (2025-11-16)

### Features Added

  - Model `MonitorManagementClient` added parameter `cloud_setting` in method `__init__`
  - Model `ErrorResponse` added property `error`
  - Model `MetricAlertResource` added property `resolve_configuration`
  - Model `MetricAlertResource` added property `custom_properties`
  - Model `MetricAlertResource` added property `action_properties`
  - Model `MetricAlertResource` added property `identity`
  - Model `MetricAlertResourcePatch` added property `identity`
  - Model `MetricAlertResourcePatch` added property `resolve_configuration`
  - Model `MetricAlertResourcePatch` added property `custom_properties`
  - Model `MetricAlertResourcePatch` added property `action_properties`
  - Enum `Odatatype` added member `MICROSOFT_AZURE_MONITOR_PROM_QL_CRITERIA`
  - Model `Resource` added property `identity`
  - Added model `DynamicPromQLCriteria`
  - Added model `MultiPromQLCriteria`
  - Added model `PromQLCriteria`
  - Added model `QueryFailingPeriods`
  - Added model `ResolveConfiguration`
  - Added model `StaticPromQLCriteria`

### Breaking Changes

  - Deleted or renamed client operation group `MonitorManagementClient.action_groups`
  - Deleted or renamed client operation group `MonitorManagementClient.activity_log_alerts`
  - Deleted or renamed client operation group `MonitorManagementClient.activity_logs`
  - Deleted or renamed client operation group `MonitorManagementClient.tenant_activity_logs`
  - Deleted or renamed client operation group `MonitorManagementClient.alert_rule_incidents`
  - Deleted or renamed client operation group `MonitorManagementClient.autoscale_settings`
  - Deleted or renamed client operation group `MonitorManagementClient.predictive_metric`
  - Deleted or renamed client operation group `MonitorManagementClient.baselines`
  - Deleted or renamed client operation group `MonitorManagementClient.diagnostic_settings`
  - Deleted or renamed client operation group `MonitorManagementClient.diagnostic_settings_category`
  - Deleted or renamed client operation group `MonitorManagementClient.event_categories`
  - Deleted or renamed client operation group `MonitorManagementClient.guest_diagnostics_settings`
  - Deleted or renamed client operation group `MonitorManagementClient.guest_diagnostics_settings_association`
  - Deleted or renamed client operation group `MonitorManagementClient.log_profiles`
  - Deleted or renamed client operation group `MonitorManagementClient.metric_definitions`
  - Deleted or renamed client operation group `MonitorManagementClient.metric_namespaces`
  - Deleted or renamed client operation group `MonitorManagementClient.metrics`
  - Deleted or renamed client operation group `MonitorManagementClient.operations`
  - Deleted or renamed client operation group `MonitorManagementClient.scheduled_query_rules`
  - Deleted or renamed client operation group `MonitorManagementClient.service_diagnostic_settings`
  - Deleted or renamed client operation group `MonitorManagementClient.vm_insights`
  - Deleted or renamed client operation group `MonitorManagementClient.private_link_scopes`
  - Deleted or renamed client operation group `MonitorManagementClient.private_link_scope_operation_status`
  - Deleted or renamed client operation group `MonitorManagementClient.private_link_resources`
  - Deleted or renamed client operation group `MonitorManagementClient.private_endpoint_connections`
  - Deleted or renamed client operation group `MonitorManagementClient.private_link_scoped_resources`
  - Deleted or renamed client operation group `MonitorManagementClient.subscription_diagnostic_settings`
  - Deleted or renamed client operation group `MonitorManagementClient.azure_monitor_workspaces`
  - Deleted or renamed client operation group `MonitorManagementClient.monitor_operations`
  - Deleted or renamed client operation group `MonitorManagementClient.data_collection_endpoints`
  - Deleted or renamed client operation group `MonitorManagementClient.data_collection_rule_associations`
  - Deleted or renamed client operation group `MonitorManagementClient.data_collection_rules`
  - Model `ErrorResponse` deleted or renamed its instance variable `code`
  - Model `ErrorResponse` deleted or renamed its instance variable `message`
  - Model `Resource` deleted or renamed its instance variable `system_data`
  - Deleted or renamed model `ActionDetail`
  - Deleted or renamed model `ActionGroup`
  - Deleted or renamed model `ActionGroupList`
  - Deleted or renamed model `ActionGroupPatchBody`
  - Deleted or renamed model `ActionGroupResource`
  - Deleted or renamed model `ActionList`
  - Deleted or renamed model `ActionType`
  - Deleted or renamed model `Actions`
  - Deleted or renamed model `ActivityLogAlertResource`
  - Deleted or renamed model `AdxDestination`
  - Deleted or renamed model `AgentSetting`
  - Deleted or renamed model `AgentSettingsSpec`
  - Deleted or renamed model `AggregationType`
  - Deleted or renamed model `AlertRuleAllOfCondition`
  - Deleted or renamed model `AlertRuleAnyOfOrLeafCondition`
  - Deleted or renamed model `AlertRuleLeafCondition`
  - Deleted or renamed model `AlertRuleList`
  - Deleted or renamed model `AlertRulePatchObject`
  - Deleted or renamed model `AlertSeverity`
  - Deleted or renamed model `ArmRoleReceiver`
  - Deleted or renamed model `AutomationRunbookReceiver`
  - Deleted or renamed model `AutoscaleErrorResponse`
  - Deleted or renamed model `AutoscaleErrorResponseError`
  - Deleted or renamed model `AutoscaleNotification`
  - Deleted or renamed model `AutoscaleProfile`
  - Deleted or renamed model `AutoscaleSettingResource`
  - Deleted or renamed model `AutoscaleSettingResourceCollection`
  - Deleted or renamed model `AutoscaleSettingResourcePatch`
  - Deleted or renamed model `AzureAppPushReceiver`
  - Deleted or renamed model `AzureFunctionReceiver`
  - Deleted or renamed model `AzureMonitorMetricsDestination`
  - Deleted or renamed model `AzureMonitorPrivateLinkScope`
  - Deleted or renamed model `AzureMonitorWorkspace`
  - Deleted or renamed model `AzureMonitorWorkspaceDefaultIngestionSettings`
  - Deleted or renamed model `AzureMonitorWorkspaceMetrics`
  - Deleted or renamed model `AzureMonitorWorkspaceResource`
  - Deleted or renamed model `AzureMonitorWorkspaceResourceForUpdate`
  - Deleted or renamed model `AzureMonitorWorkspaceResourceProperties`
  - Deleted or renamed model `AzureResource`
  - Deleted or renamed model `AzureResourceAutoGenerated`
  - Deleted or renamed model `BaselineMetadata`
  - Deleted or renamed model `BaselineSensitivity`
  - Deleted or renamed model `CategoryType`
  - Deleted or renamed model `ColumnDefinition`
  - Deleted or renamed model `ComparisonOperationType`
  - Deleted or renamed model `Condition`
  - Deleted or renamed model `ConditionFailingPeriods`
  - Deleted or renamed model `ConditionOperator`
  - Deleted or renamed model `ConfigurationAccessEndpointSpec`
  - Deleted or renamed model `Context`
  - Deleted or renamed model `CreatedByType`
  - Deleted or renamed model `DataCollectionEndpoint`
  - Deleted or renamed model `DataCollectionEndpointConfigurationAccess`
  - Deleted or renamed model `DataCollectionEndpointFailoverConfiguration`
  - Deleted or renamed model `DataCollectionEndpointLogsIngestion`
  - Deleted or renamed model `DataCollectionEndpointMetadata`
  - Deleted or renamed model `DataCollectionEndpointMetricsIngestion`
  - Deleted or renamed model `DataCollectionEndpointNetworkAcls`
  - Deleted or renamed model `DataCollectionEndpointResource`
  - Deleted or renamed model `DataCollectionEndpointResourceIdentity`
  - Deleted or renamed model `DataCollectionEndpointResourceProperties`
  - Deleted or renamed model `DataCollectionEndpointResourceSystemData`
  - Deleted or renamed model `DataCollectionRule`
  - Deleted or renamed model `DataCollectionRuleAgentSettings`
  - Deleted or renamed model `DataCollectionRuleAssociation`
  - Deleted or renamed model `DataCollectionRuleAssociationMetadata`
  - Deleted or renamed model `DataCollectionRuleAssociationProxyOnlyResource`
  - Deleted or renamed model `DataCollectionRuleAssociationProxyOnlyResourceProperties`
  - Deleted or renamed model `DataCollectionRuleAssociationProxyOnlyResourceSystemData`
  - Deleted or renamed model `DataCollectionRuleDataSources`
  - Deleted or renamed model `DataCollectionRuleDestinations`
  - Deleted or renamed model `DataCollectionRuleEndpoints`
  - Deleted or renamed model `DataCollectionRuleMetadata`
  - Deleted or renamed model `DataCollectionRuleReferences`
  - Deleted or renamed model `DataCollectionRuleResource`
  - Deleted or renamed model `DataCollectionRuleResourceIdentity`
  - Deleted or renamed model `DataCollectionRuleResourceProperties`
  - Deleted or renamed model `DataCollectionRuleResourceSystemData`
  - Deleted or renamed model `DataContainer`
  - Deleted or renamed model `DataFlow`
  - Deleted or renamed model `DataImportSources`
  - Deleted or renamed model `DataImportSourcesEventHub`
  - Deleted or renamed model `DataSource`
  - Deleted or renamed model `DataSourceConfiguration`
  - Deleted or renamed model `DataSourceKind`
  - Deleted or renamed model `DataSourcesSpec`
  - Deleted or renamed model `DataSourcesSpecDataImports`
  - Deleted or renamed model `DataStatus`
  - Deleted or renamed model `DestinationsSpec`
  - Deleted or renamed model `DestinationsSpecAzureMonitorMetrics`
  - Deleted or renamed model `DiagnosticSettingsCategoryResource`
  - Deleted or renamed model `DiagnosticSettingsCategoryResourceCollection`
  - Deleted or renamed model `DiagnosticSettingsResource`
  - Deleted or renamed model `DiagnosticSettingsResourceCollection`
  - Deleted or renamed model `Dimension`
  - Deleted or renamed model `DimensionOperator`
  - Deleted or renamed model `EmailNotification`
  - Deleted or renamed model `EmailReceiver`
  - Deleted or renamed model `EnableRequest`
  - Deleted or renamed model `EndpointsSpec`
  - Deleted or renamed model `EnrichmentData`
  - Deleted or renamed model `Error`
  - Deleted or renamed model `ErrorAdditionalInfo`
  - Deleted or renamed model `ErrorContract`
  - Deleted or renamed model `ErrorDetailAutoGenerated`
  - Deleted or renamed model `ErrorDetailAutoGenerated2`
  - Deleted or renamed model `ErrorResponseAutoGenerated`
  - Deleted or renamed model `ErrorResponseAutoGenerated2`
  - Deleted or renamed model `ErrorResponseAutoGenerated3`
  - Deleted or renamed model `ErrorResponseAutoGenerated4`
  - Deleted or renamed model `ErrorResponseAutoGenerated5`
  - Deleted or renamed model `ErrorResponseCommon`
  - Deleted or renamed model `ErrorResponseCommonV2`
  - Deleted or renamed model `EtwEventConfiguration`
  - Deleted or renamed model `EtwProviderConfiguration`
  - Deleted or renamed model `EventCategoryCollection`
  - Deleted or renamed model `EventData`
  - Deleted or renamed model `EventDataCollection`
  - Deleted or renamed model `EventHubDataSource`
  - Deleted or renamed model `EventHubDestination`
  - Deleted or renamed model `EventHubDirectDestination`
  - Deleted or renamed model `EventHubReceiver`
  - Deleted or renamed model `EventLevel`
  - Deleted or renamed model `EventLogConfiguration`
  - Deleted or renamed model `ExtensionDataSource`
  - Deleted or renamed model `FailoverConfigurationSpec`
  - Deleted or renamed model `GuestDiagnosticSettingsAssociationList`
  - Deleted or renamed model `GuestDiagnosticSettingsAssociationResource`
  - Deleted or renamed model `GuestDiagnosticSettingsAssociationResourcePatch`
  - Deleted or renamed model `GuestDiagnosticSettingsList`
  - Deleted or renamed model `GuestDiagnosticSettingsOsType`
  - Deleted or renamed model `GuestDiagnosticSettingsPatchResource`
  - Deleted or renamed model `GuestDiagnosticSettingsResource`
  - Deleted or renamed model `HttpRequestInfo`
  - Deleted or renamed model `IisLogsDataSource`
  - Deleted or renamed model `Incident`
  - Deleted or renamed model `IngestionSettings`
  - Deleted or renamed model `ItsmReceiver`
  - Deleted or renamed model `Kind`
  - Deleted or renamed model `KnownAgentSettingName`
  - Deleted or renamed model `KnownColumnDefinitionType`
  - Deleted or renamed model `KnownDataCollectionEndpointProvisioningState`
  - Deleted or renamed model `KnownDataCollectionEndpointResourceKind`
  - Deleted or renamed model `KnownDataCollectionRuleAssociationProvisioningState`
  - Deleted or renamed model `KnownDataCollectionRuleProvisioningState`
  - Deleted or renamed model `KnownDataCollectionRuleResourceKind`
  - Deleted or renamed model `KnownDataFlowStreams`
  - Deleted or renamed model `KnownExtensionDataSourceStreams`
  - Deleted or renamed model `KnownLocationSpecProvisioningStatus`
  - Deleted or renamed model `KnownLogFileTextSettingsRecordStartTimestampFormat`
  - Deleted or renamed model `KnownLogFilesDataSourceFormat`
  - Deleted or renamed model `KnownPerfCounterDataSourceStreams`
  - Deleted or renamed model `KnownPrometheusForwarderDataSourceStreams`
  - Deleted or renamed model `KnownPublicNetworkAccessOptions`
  - Deleted or renamed model `KnownStorageBlobLookupType`
  - Deleted or renamed model `KnownSyslogDataSourceFacilityNames`
  - Deleted or renamed model `KnownSyslogDataSourceLogLevels`
  - Deleted or renamed model `KnownSyslogDataSourceStreams`
  - Deleted or renamed model `KnownWindowsEventLogDataSourceStreams`
  - Deleted or renamed model `KnownWindowsFirewallLogsDataSourceProfileFilter`
  - Deleted or renamed model `LocalizableString`
  - Deleted or renamed model `LocalizableStringAutoGenerated`
  - Deleted or renamed model `LocationSpec`
  - Deleted or renamed model `LogAnalyticsDestination`
  - Deleted or renamed model `LogFileSettings`
  - Deleted or renamed model `LogFileSettingsText`
  - Deleted or renamed model `LogFileTextSettings`
  - Deleted or renamed model `LogFilesDataSource`
  - Deleted or renamed model `LogFilesDataSourceSettings`
  - Deleted or renamed model `LogProfileCollection`
  - Deleted or renamed model `LogProfileResource`
  - Deleted or renamed model `LogProfileResourcePatch`
  - Deleted or renamed model `LogSettings`
  - Deleted or renamed model `LogSettingsAutoGenerated`
  - Deleted or renamed model `LogicAppReceiver`
  - Deleted or renamed model `LogsIngestionEndpointSpec`
  - Deleted or renamed model `ManagedServiceIdentity`
  - Deleted or renamed model `ManagedServiceIdentityType`
  - Deleted or renamed model `Metadata`
  - Deleted or renamed model `MetadataValue`
  - Deleted or renamed model `Metric`
  - Deleted or renamed model `MetricAggregationType`
  - Deleted or renamed model `MetricAvailability`
  - Deleted or renamed model `MetricBaselinesResponse`
  - Deleted or renamed model `MetricClass`
  - Deleted or renamed model `MetricDefinition`
  - Deleted or renamed model `MetricDefinitionCollection`
  - Deleted or renamed model `MetricNamespace`
  - Deleted or renamed model `MetricNamespaceCollection`
  - Deleted or renamed model `MetricNamespaceName`
  - Deleted or renamed model `MetricResultType`
  - Deleted or renamed model `MetricSettings`
  - Deleted or renamed model `MetricSettingsAutoGenerated`
  - Deleted or renamed model `MetricSingleDimension`
  - Deleted or renamed model `MetricStatisticType`
  - Deleted or renamed model `MetricTrigger`
  - Deleted or renamed model `MetricUnit`
  - Deleted or renamed model `MetricValue`
  - Deleted or renamed model `Metrics`
  - Deleted or renamed model `MetricsIngestionEndpointSpec`
  - Deleted or renamed model `MicrosoftFabricDestination`
  - Deleted or renamed model `MonitoringAccountDestination`
  - Deleted or renamed model `NamespaceClassification`
  - Deleted or renamed model `NetworkRuleSet`
  - Deleted or renamed model `NotificationRequestBody`
  - Deleted or renamed model `OnboardingStatus`
  - Deleted or renamed model `Operation`
  - Deleted or renamed model `OperationAutoGenerated`
  - Deleted or renamed model `OperationDisplay`
  - Deleted or renamed model `OperationDisplayAutoGenerated`
  - Deleted or renamed model `OperationListResultAutoGenerated`
  - Deleted or renamed model `OperationStatus`
  - Deleted or renamed model `Origin`
  - Deleted or renamed model `PerfCounterDataSource`
  - Deleted or renamed model `PerformanceCounterConfiguration`
  - Deleted or renamed model `PlatformTelemetryDataSource`
  - Deleted or renamed model `PredictiveAutoscalePolicy`
  - Deleted or renamed model `PredictiveAutoscalePolicyScaleMode`
  - Deleted or renamed model `PredictiveResponse`
  - Deleted or renamed model `PredictiveValue`
  - Deleted or renamed model `PrivateEndpoint`
  - Deleted or renamed model `PrivateEndpointConnection`
  - Deleted or renamed model `PrivateEndpointConnectionAutoGenerated`
  - Deleted or renamed model `PrivateEndpointConnectionProvisioningState`
  - Deleted or renamed model `PrivateEndpointProperty`
  - Deleted or renamed model `PrivateEndpointServiceConnectionStatus`
  - Deleted or renamed model `PrivateLinkResource`
  - Deleted or renamed model `PrivateLinkScopedResource`
  - Deleted or renamed model `PrivateLinkScopesResource`
  - Deleted or renamed model `PrivateLinkServiceConnectionState`
  - Deleted or renamed model `PrivateLinkServiceConnectionStateProperty`
  - Deleted or renamed model `PrometheusForwarderDataSource`
  - Deleted or renamed model `ProvisioningState`
  - Deleted or renamed model `ProxyOnlyResource`
  - Deleted or renamed model `ProxyResource`
  - Deleted or renamed model `PublicNetworkAccess`
  - Deleted or renamed model `ReceiverStatus`
  - Deleted or renamed model `Recurrence`
  - Deleted or renamed model `RecurrenceFrequency`
  - Deleted or renamed model `RecurrentSchedule`
  - Deleted or renamed model `ReferencesSpec`
  - Deleted or renamed model `ReferencesSpecEnrichmentData`
  - Deleted or renamed model `ResourceAutoGenerated`
  - Deleted or renamed model `ResourceAutoGenerated2`
  - Deleted or renamed model `ResourceAutoGenerated3`
  - Deleted or renamed model `ResourceAutoGenerated4`
  - Deleted or renamed model `ResourceAutoGenerated5`
  - Deleted or renamed model `ResourceAutoGenerated6`
  - Deleted or renamed model `ResourceAutoGenerated7`
  - Deleted or renamed model `ResourceAutoGenerated8`
  - Deleted or renamed model `ResourceForUpdate`
  - Deleted or renamed model `ResourceForUpdateIdentity`
  - Deleted or renamed model `Response`
  - Deleted or renamed model `ResponseWithError`
  - Deleted or renamed model `ResultType`
  - Deleted or renamed model `RetentionPolicy`
  - Deleted or renamed model `RuleResolveConfiguration`
  - Deleted or renamed model `ScaleAction`
  - Deleted or renamed model `ScaleCapacity`
  - Deleted or renamed model `ScaleDirection`
  - Deleted or renamed model `ScaleRule`
  - Deleted or renamed model `ScaleRuleMetricDimension`
  - Deleted or renamed model `ScaleRuleMetricDimensionOperationType`
  - Deleted or renamed model `ScaleType`
  - Deleted or renamed model `ScheduledQueryRuleCriteria`
  - Deleted or renamed model `ScheduledQueryRuleResource`
  - Deleted or renamed model `ScheduledQueryRuleResourceCollection`
  - Deleted or renamed model `ScheduledQueryRuleResourcePatch`
  - Deleted or renamed model `ScopedResource`
  - Deleted or renamed model `SenderAuthorization`
  - Deleted or renamed model `ServiceDiagnosticSettingsResource`
  - Deleted or renamed model `ServiceDiagnosticSettingsResourcePatch`
  - Deleted or renamed model `SingleBaseline`
  - Deleted or renamed model `SingleMetricBaseline`
  - Deleted or renamed model `SinkConfiguration`
  - Deleted or renamed model `SinkConfigurationKind`
  - Deleted or renamed model `SmsReceiver`
  - Deleted or renamed model `StorageBlob`
  - Deleted or renamed model `StorageBlobDestination`
  - Deleted or renamed model `StorageTableDestination`
  - Deleted or renamed model `StreamDeclaration`
  - Deleted or renamed model `SubscriptionDiagnosticSettingsResource`
  - Deleted or renamed model `SubscriptionDiagnosticSettingsResourceCollection`
  - Deleted or renamed model `SubscriptionLogSettings`
  - Deleted or renamed model `SubscriptionProxyOnlyResource`
  - Deleted or renamed model `SubscriptionScopeMetricDefinition`
  - Deleted or renamed model `SubscriptionScopeMetricDefinitionCollection`
  - Deleted or renamed model `SubscriptionScopeMetricsRequestBodyParameters`
  - Deleted or renamed model `SyslogDataSource`
  - Deleted or renamed model `SystemData`
  - Deleted or renamed model `TagsResource`
  - Deleted or renamed model `TestNotificationDetailsResponse`
  - Deleted or renamed model `TimeAggregation`
  - Deleted or renamed model `TimeAggregationType`
  - Deleted or renamed model `TimeSeriesBaseline`
  - Deleted or renamed model `TimeSeriesElement`
  - Deleted or renamed model `TimeWindow`
  - Deleted or renamed model `TrackedResource`
  - Deleted or renamed model `UserAssignedIdentity`
  - Deleted or renamed model `VMInsightsOnboardingStatus`
  - Deleted or renamed model `VoiceReceiver`
  - Deleted or renamed model `WebhookNotification`
  - Deleted or renamed model `WebhookReceiver`
  - Deleted or renamed model `WindowsEventLogDataSource`
  - Deleted or renamed model `WindowsFirewallLogsDataSource`
  - Deleted or renamed model `WorkspaceInfo`
  - Deleted or renamed model `ActionGroupsOperations`
  - Deleted or renamed model `ActivityLogAlertsOperations`
  - Deleted or renamed model `ActivityLogsOperations`
  - Deleted or renamed model `AlertRuleIncidentsOperations`
  - Deleted or renamed model `AutoscaleSettingsOperations`
  - Deleted or renamed model `AzureMonitorWorkspacesOperations`
  - Deleted or renamed model `BaselinesOperations`
  - Deleted or renamed model `DataCollectionEndpointsOperations`
  - Deleted or renamed model `DataCollectionRuleAssociationsOperations`
  - Deleted or renamed model `DataCollectionRulesOperations`
  - Deleted or renamed model `DiagnosticSettingsCategoryOperations`
  - Deleted or renamed model `DiagnosticSettingsOperations`
  - Deleted or renamed model `EventCategoriesOperations`
  - Deleted or renamed model `GuestDiagnosticsSettingsAssociationOperations`
  - Deleted or renamed model `GuestDiagnosticsSettingsOperations`
  - Deleted or renamed model `LogProfilesOperations`
  - Deleted or renamed model `MetricDefinitionsOperations`
  - Deleted or renamed model `MetricNamespacesOperations`
  - Deleted or renamed model `MetricsOperations`
  - Deleted or renamed model `MonitorOperationsOperations`
  - Deleted or renamed model `Operations`
  - Deleted or renamed model `PredictiveMetricOperations`
  - Deleted or renamed model `PrivateEndpointConnectionsOperations`
  - Deleted or renamed model `PrivateLinkResourcesOperations`
  - Deleted or renamed model `PrivateLinkScopeOperationStatusOperations`
  - Deleted or renamed model `PrivateLinkScopedResourcesOperations`
  - Deleted or renamed model `PrivateLinkScopesOperations`
  - Deleted or renamed model `ScheduledQueryRulesOperations`
  - Deleted or renamed model `ServiceDiagnosticSettingsOperations`
  - Deleted or renamed model `SubscriptionDiagnosticSettingsOperations`
  - Deleted or renamed model `TenantActivityLogsOperations`
  - Deleted or renamed model `VMInsightsOperations`

## 8.0.0b1 (2025-08-05)

### Features Added

  - Client `MonitorManagementClient` added operation group `diagnostic_settings`
  - Client `MonitorManagementClient` added operation group `diagnostic_settings_category`
  - Client `MonitorManagementClient` added operation group `guest_diagnostics_settings`
  - Client `MonitorManagementClient` added operation group `guest_diagnostics_settings_association`
  - Client `MonitorManagementClient` added operation group `service_diagnostic_settings`
  - Client `MonitorManagementClient` added operation group `vm_insights`
  - Client `MonitorManagementClient` added operation group `private_link_scopes`
  - Client `MonitorManagementClient` added operation group `private_link_scope_operation_status`
  - Client `MonitorManagementClient` added operation group `private_link_resources`
  - Client `MonitorManagementClient` added operation group `private_endpoint_connections`
  - Client `MonitorManagementClient` added operation group `private_link_scoped_resources`
  - Client `MonitorManagementClient` added operation group `subscription_diagnostic_settings`
  - Model `ErrorDetailAutoGenerated` added property `details`
  - Model `ResourceAutoGenerated3` added property `location`
  - Model `ResourceAutoGenerated3` added property `tags`
  - Model `ResourceAutoGenerated4` added property `location`
  - Model `ResourceAutoGenerated4` added property `tags`
  - Added model `AzureMonitorPrivateLinkScope`
  - Added model `AzureMonitorPrivateLinkScopeListResult`
  - Added enum `CategoryType`
  - Added model `DataContainer`
  - Added model `DataSource`
  - Added model `DataSourceConfiguration`
  - Added enum `DataSourceKind`
  - Added enum `DataStatus`
  - Added model `DiagnosticSettingsCategoryResource`
  - Added model `DiagnosticSettingsCategoryResourceCollection`
  - Added model `DiagnosticSettingsResource`
  - Added model `DiagnosticSettingsResourceCollection`
  - Added model `Error`
  - Added model `ErrorResponseCommon`
  - Added model `EtwEventConfiguration`
  - Added model `EtwProviderConfiguration`
  - Added model `EventLogConfiguration`
  - Added model `GuestDiagnosticSettingsAssociationList`
  - Added model `GuestDiagnosticSettingsAssociationResource`
  - Added model `GuestDiagnosticSettingsAssociationResourcePatch`
  - Added model `GuestDiagnosticSettingsList`
  - Added enum `GuestDiagnosticSettingsOsType`
  - Added model `GuestDiagnosticSettingsPatchResource`
  - Added model `GuestDiagnosticSettingsResource`
  - Added model `LogSettings`
  - Added model `LogSettingsAutoGenerated`
  - Added model `MetricSettings`
  - Added model `MetricSettingsAutoGenerated`
  - Added enum `OnboardingStatus`
  - Added model `OperationStatus`
  - Added model `PerformanceCounterConfiguration`
  - Added model `PrivateEndpointConnectionAutoGenerated`
  - Added model `PrivateEndpointConnectionListResult`
  - Added model `PrivateEndpointProperty`
  - Added model `PrivateLinkResource`
  - Added model `PrivateLinkResourceListResult`
  - Added model `PrivateLinkScopesResource`
  - Added model `PrivateLinkServiceConnectionStateProperty`
  - Added model `ProxyOnlyResource`
  - Added model `ProxyResource`
  - Added model `ResourceAutoGenerated5`
  - Added model `ResourceAutoGenerated6`
  - Added model `ResourceAutoGenerated7`
  - Added model `ResourceAutoGenerated8`
  - Added model `ResponseWithError`
  - Added model `ScopedResource`
  - Added model `ScopedResourceListResult`
  - Added model `ServiceDiagnosticSettingsResource`
  - Added model `ServiceDiagnosticSettingsResourcePatch`
  - Added model `SinkConfiguration`
  - Added enum `SinkConfigurationKind`
  - Added model `SubscriptionDiagnosticSettingsResource`
  - Added model `SubscriptionDiagnosticSettingsResourceCollection`
  - Added model `SubscriptionLogSettings`
  - Added model `SubscriptionProxyOnlyResource`
  - Added model `TagsResource`
  - Added model `VMInsightsOnboardingStatus`
  - Added model `WorkspaceInfo`
  - Added operation group `DiagnosticSettingsCategoryOperations`
  - Added operation group `DiagnosticSettingsOperations`
  - Added operation group `GuestDiagnosticsSettingsAssociationOperations`
  - Added operation group `GuestDiagnosticsSettingsOperations`
  - Added operation group `PrivateEndpointConnectionsOperations`
  - Added operation group `PrivateLinkResourcesOperations`
  - Added operation group `PrivateLinkScopeOperationStatusOperations`
  - Added operation group `PrivateLinkScopedResourcesOperations`
  - Added operation group `PrivateLinkScopesOperations`
  - Added operation group `ServiceDiagnosticSettingsOperations`
  - Added operation group `SubscriptionDiagnosticSettingsOperations`
  - Added operation group `VMInsightsOperations`

### Breaking Changes

  - Model `ErrorDetail` deleted or renamed its instance variable `details`
  - Model `PrivateEndpointConnection` deleted or renamed its instance variable `group_ids`
  - Model `PrivateEndpointConnection` deleted or renamed its instance variable `system_data`
  - Model `ResourceAutoGenerated` deleted or renamed its instance variable `location`
  - Model `ResourceAutoGenerated` deleted or renamed its instance variable `tags`
  - Model `ResourceAutoGenerated3` deleted or renamed its instance variable `system_data`
  - Model `ResourceAutoGenerated4` deleted or renamed its instance variable `system_data`

## 7.0.0 (2025-07-28)

### Features Added

  - Client `MonitorManagementClient` added operation group `action_groups`
  - Client `MonitorManagementClient` added operation group `activity_log_alerts`
  - Client `MonitorManagementClient` added operation group `activity_logs`
  - Client `MonitorManagementClient` added operation group `alert_rule_incidents`
  - Client `MonitorManagementClient` added operation group `autoscale_settings`
  - Client `MonitorManagementClient` added operation group `predictive_metric`
  - Client `MonitorManagementClient` added operation group `data_collection_endpoints`
  - Client `MonitorManagementClient` added operation group `data_collection_rule_associations`
  - Client `MonitorManagementClient` added operation group `data_collection_rules`
  - Client `MonitorManagementClient` added operation group `event_categories`
  - Client `MonitorManagementClient` added operation group `log_profiles`
  - Client `MonitorManagementClient` added operation group `metric_alerts`
  - Client `MonitorManagementClient` added operation group `metric_alerts_status`
  - Client `MonitorManagementClient` added operation group `baselines`
  - Client `MonitorManagementClient` added operation group `metric_definitions`
  - Client `MonitorManagementClient` added operation group `metric_namespaces`
  - Client `MonitorManagementClient` added operation group `metrics`
  - Client `MonitorManagementClient` added operation group `operations`
  - Client `MonitorManagementClient` added operation group `scheduled_query_rules`
  - Client `MonitorManagementClient` added operation group `tenant_activity_logs`
  - Client `MonitorManagementClient` added operation group `azure_monitor_workspaces`
  - Client `MonitorManagementClient` added operation group `monitor_operations`
  - Added model `ActionDetail`
  - Added model `ActionGroup`
  - Added model `ActionGroupList`
  - Added model `ActionGroupResource`
  - Added model `ActionList`
  - Added enum `ActionType`
  - Added model `Actions`
  - Added model `ActivityLogAlertResource`
  - Added model `AdxDestination`
  - Added model `AgentSetting`
  - Added model `AgentSettingsSpec`
  - Added enum `AggregationType`
  - Added enum `AggregationTypeEnum`
  - Added model `AlertRuleAllOfCondition`
  - Added model `AlertRuleAnyOfOrLeafCondition`
  - Added model `AlertRuleLeafCondition`
  - Added model `AlertRuleList`
  - Added model `AlertRulePatchObject`
  - Added enum `AlertSeverity`
  - Added model `ArmRoleReceiver`
  - Added model `AutomationRunbookReceiver`
  - Added model `AutoscaleErrorResponse`
  - Added model `AutoscaleErrorResponseError`
  - Added model `AutoscaleNotification`
  - Added model `AutoscaleProfile`
  - Added model `AutoscaleSettingResource`
  - Added model `AutoscaleSettingResourceCollection`
  - Added model `AutoscaleSettingResourcePatch`
  - Added model `AzureFunctionReceiver`
  - Added model `AzureMonitorMetricsDestination`
  - Added model `AzureMonitorWorkspace`
  - Added model `AzureMonitorWorkspaceDefaultIngestionSettings`
  - Added model `AzureMonitorWorkspaceMetrics`
  - Added model `AzureMonitorWorkspaceResource`
  - Added model `AzureMonitorWorkspaceResourceForUpdate`
  - Added model `AzureMonitorWorkspaceResourceListResult`
  - Added model `AzureMonitorWorkspaceResourceProperties`
  - Added model `AzureResourceAutoGenerated`
  - Added model `BaselineMetadata`
  - Added enum `BaselineSensitivity`
  - Added model `ColumnDefinition`
  - Added enum `ComparisonOperationType`
  - Added model `Condition`
  - Added model `ConditionFailingPeriods`
  - Added enum `ConditionOperator`
  - Added model `ConfigurationAccessEndpointSpec`
  - Added model `Context`
  - Added enum `CreatedByType`
  - Added enum `CriterionType`
  - Added model `DataCollectionEndpoint`
  - Added model `DataCollectionEndpointConfigurationAccess`
  - Added model `DataCollectionEndpointFailoverConfiguration`
  - Added model `DataCollectionEndpointLogsIngestion`
  - Added model `DataCollectionEndpointMetadata`
  - Added model `DataCollectionEndpointMetricsIngestion`
  - Added model `DataCollectionEndpointNetworkAcls`
  - Added model `DataCollectionEndpointResource`
  - Added model `DataCollectionEndpointResourceIdentity`
  - Added model `DataCollectionEndpointResourceListResult`
  - Added model `DataCollectionEndpointResourceProperties`
  - Added model `DataCollectionEndpointResourceSystemData`
  - Added model `DataCollectionRule`
  - Added model `DataCollectionRuleAgentSettings`
  - Added model `DataCollectionRuleAssociation`
  - Added model `DataCollectionRuleAssociationMetadata`
  - Added model `DataCollectionRuleAssociationProxyOnlyResource`
  - Added model `DataCollectionRuleAssociationProxyOnlyResourceListResult`
  - Added model `DataCollectionRuleAssociationProxyOnlyResourceProperties`
  - Added model `DataCollectionRuleAssociationProxyOnlyResourceSystemData`
  - Added model `DataCollectionRuleDataSources`
  - Added model `DataCollectionRuleDestinations`
  - Added model `DataCollectionRuleEndpoints`
  - Added model `DataCollectionRuleMetadata`
  - Added model `DataCollectionRuleReferences`
  - Added model `DataCollectionRuleResource`
  - Added model `DataCollectionRuleResourceIdentity`
  - Added model `DataCollectionRuleResourceListResult`
  - Added model `DataCollectionRuleResourceProperties`
  - Added model `DataCollectionRuleResourceSystemData`
  - Added model `DataFlow`
  - Added model `DataImportSources`
  - Added model `DataImportSourcesEventHub`
  - Added model `DataSourcesSpec`
  - Added model `DataSourcesSpecDataImports`
  - Added model `DestinationsSpec`
  - Added model `DestinationsSpecAzureMonitorMetrics`
  - Added model `Dimension`
  - Added enum `DimensionOperator`
  - Added model `DynamicMetricCriteria`
  - Added model `DynamicThresholdFailingPeriods`
  - Added enum `DynamicThresholdOperator`
  - Added enum `DynamicThresholdSensitivity`
  - Added model `EmailNotification`
  - Added model `EnableRequest`
  - Added model `EndpointsSpec`
  - Added model `EnrichmentData`
  - Added model `ErrorAdditionalInfo`
  - Added model `ErrorContract`
  - Added model `ErrorDetail`
  - Added model `ErrorDetailAdditionalInfoItem`
  - Added model `ErrorDetailAutoGenerated`
  - Added model `ErrorDetailAutoGenerated2`
  - Added model `ErrorResponseAutoGenerated`
  - Added model `ErrorResponseAutoGenerated2`
  - Added model `ErrorResponseAutoGenerated3`
  - Added model `ErrorResponseAutoGenerated4`
  - Added model `ErrorResponseAutoGenerated5`
  - Added model `ErrorResponseCommonV2`
  - Added model `ErrorResponseError`
  - Added model `ErrorResponseErrorAdditionalInfoItem`
  - Added model `EventCategoryCollection`
  - Added model `EventData`
  - Added model `EventDataCollection`
  - Added model `EventHubDataSource`
  - Added model `EventHubDestination`
  - Added model `EventHubDirectDestination`
  - Added model `EventHubReceiver`
  - Added enum `EventLevel`
  - Added model `ExtensionDataSource`
  - Added model `FailoverConfigurationSpec`
  - Added model `HttpRequestInfo`
  - Added model `Identity`
  - Added enum `IdentityType`
  - Added model `IisLogsDataSource`
  - Added model `Incident`
  - Added model `IncidentListResult`
  - Added model `IngestionSettings`
  - Added model `ItsmReceiver`
  - Added enum `Kind`
  - Added enum `KnownAgentSettingName`
  - Added enum `KnownColumnDefinitionType`
  - Added enum `KnownDataCollectionEndpointProvisioningState`
  - Added enum `KnownDataCollectionEndpointResourceKind`
  - Added enum `KnownDataCollectionRuleAssociationProvisioningState`
  - Added enum `KnownDataCollectionRuleProvisioningState`
  - Added enum `KnownDataCollectionRuleResourceKind`
  - Added enum `KnownDataFlowStreams`
  - Added enum `KnownExtensionDataSourceStreams`
  - Added enum `KnownLocationSpecProvisioningStatus`
  - Added enum `KnownLogFileTextSettingsRecordStartTimestampFormat`
  - Added enum `KnownLogFilesDataSourceFormat`
  - Added enum `KnownPerfCounterDataSourceStreams`
  - Added enum `KnownPrometheusForwarderDataSourceStreams`
  - Added enum `KnownPublicNetworkAccessOptions`
  - Added enum `KnownStorageBlobLookupType`
  - Added enum `KnownSyslogDataSourceFacilityNames`
  - Added enum `KnownSyslogDataSourceLogLevels`
  - Added enum `KnownSyslogDataSourceStreams`
  - Added enum `KnownWindowsEventLogDataSourceStreams`
  - Added enum `KnownWindowsFirewallLogsDataSourceProfileFilter`
  - Added model `LocalizableString`
  - Added model `LocalizableStringAutoGenerated`
  - Added model `LocationSpec`
  - Added model `LogAnalyticsDestination`
  - Added model `LogFileSettings`
  - Added model `LogFileSettingsText`
  - Added model `LogFileTextSettings`
  - Added model `LogFilesDataSource`
  - Added model `LogFilesDataSourceSettings`
  - Added model `LogProfileCollection`
  - Added model `LogProfileResource`
  - Added model `LogProfileResourcePatch`
  - Added model `LogicAppReceiver`
  - Added model `LogsIngestionEndpointSpec`
  - Added model `ManagedServiceIdentity`
  - Added enum `ManagedServiceIdentityType`
  - Added model `Metadata`
  - Added model `MetadataValue`
  - Added model `Metric`
  - Added enum `MetricAggregationType`
  - Added model `MetricAlertAction`
  - Added model `MetricAlertCriteria`
  - Added model `MetricAlertMultipleResourceMultipleMetricCriteria`
  - Added model `MetricAlertResource`
  - Added model `MetricAlertResourceCollection`
  - Added model `MetricAlertResourcePatch`
  - Added model `MetricAlertSingleResourceMultipleMetricCriteria`
  - Added model `MetricAlertStatus`
  - Added model `MetricAlertStatusCollection`
  - Added model `MetricAlertStatusProperties`
  - Added model `MetricAvailability`
  - Added model `MetricBaselinesResponse`
  - Added enum `MetricClass`
  - Added model `MetricCriteria`
  - Added model `MetricDefinition`
  - Added model `MetricDefinitionCollection`
  - Added model `MetricDimension`
  - Added model `MetricNamespace`
  - Added model `MetricNamespaceCollection`
  - Added model `MetricNamespaceName`
  - Added enum `MetricResultType`
  - Added model `MetricSingleDimension`
  - Added enum `MetricStatisticType`
  - Added model `MetricTrigger`
  - Added enum `MetricUnit`
  - Added model `MetricValue`
  - Added model `Metrics`
  - Added model `MetricsIngestionEndpointSpec`
  - Added model `MicrosoftFabricDestination`
  - Added model `MonitoringAccountDestination`
  - Added model `MultiMetricCriteria`
  - Added enum `NamespaceClassification`
  - Added model `NetworkRuleSet`
  - Added model `NotificationRequestBody`
  - Added enum `Odatatype`
  - Added model `Operation`
  - Added model `OperationAutoGenerated`
  - Added model `OperationDisplay`
  - Added model `OperationDisplayAutoGenerated`
  - Added model `OperationListResult`
  - Added model `OperationListResultAutoGenerated`
  - Added enum `Operator`
  - Added enum `Origin`
  - Added model `PerfCounterDataSource`
  - Added model `PlatformTelemetryDataSource`
  - Added model `PredictiveAutoscalePolicy`
  - Added enum `PredictiveAutoscalePolicyScaleMode`
  - Added model `PredictiveResponse`
  - Added model `PredictiveValue`
  - Added model `PrivateEndpoint`
  - Added model `PrivateEndpointConnection`
  - Added enum `PrivateEndpointConnectionProvisioningState`
  - Added enum `PrivateEndpointServiceConnectionStatus`
  - Added model `PrivateLinkScopedResource`
  - Added model `PrivateLinkServiceConnectionState`
  - Added model `PrometheusForwarderDataSource`
  - Added enum `ProvisioningState`
  - Added enum `PublicNetworkAccess`
  - Added model `Recurrence`
  - Added enum `RecurrenceFrequency`
  - Added model `RecurrentSchedule`
  - Added model `ReferencesSpec`
  - Added model `ReferencesSpecEnrichmentData`
  - Added model `Resource`
  - Added model `ResourceAutoGenerated`
  - Added model `ResourceAutoGenerated2`
  - Added model `ResourceAutoGenerated3`
  - Added model `ResourceAutoGenerated4`
  - Added model `ResourceForUpdate`
  - Added model `ResourceForUpdateIdentity`
  - Added model `Response`
  - Added enum `ResultType`
  - Added model `RetentionPolicy`
  - Added model `RuleResolveConfiguration`
  - Added model `ScaleAction`
  - Added model `ScaleCapacity`
  - Added enum `ScaleDirection`
  - Added model `ScaleRule`
  - Added model `ScaleRuleMetricDimension`
  - Added enum `ScaleRuleMetricDimensionOperationType`
  - Added enum `ScaleType`
  - Added model `ScheduledQueryRuleCriteria`
  - Added model `ScheduledQueryRuleResource`
  - Added model `ScheduledQueryRuleResourceCollection`
  - Added model `ScheduledQueryRuleResourcePatch`
  - Added model `SenderAuthorization`
  - Added model `SingleBaseline`
  - Added model `SingleMetricBaseline`
  - Added model `StorageBlob`
  - Added model `StorageBlobDestination`
  - Added model `StorageTableDestination`
  - Added model `StreamDeclaration`
  - Added model `SubscriptionScopeMetricDefinition`
  - Added model `SubscriptionScopeMetricDefinitionCollection`
  - Added model `SubscriptionScopeMetricsRequestBodyParameters`
  - Added model `SyslogDataSource`
  - Added model `SystemData`
  - Added model `TestNotificationDetailsResponse`
  - Added enum `TimeAggregation`
  - Added enum `TimeAggregationType`
  - Added model `TimeSeriesBaseline`
  - Added model `TimeSeriesElement`
  - Added model `TimeWindow`
  - Added model `TrackedResource`
  - Added model `UserAssignedIdentity`
  - Added model `UserIdentityProperties`
  - Added model `WebhookNotification`
  - Added model `WebtestLocationAvailabilityCriteria`
  - Added model `WindowsEventLogDataSource`
  - Added model `WindowsFirewallLogsDataSource`

### Breaking Changes

  - This package now only targets the latest Api-Version available on Azure and removes APIs of other Api-Version. After this change, the package can have much smaller size. If your application requires a specific and non-latest Api-Version, it's recommended to pin this package to the previous released version; If your application always only use latest Api-Version, please ignore this change.
  - Deleted or renamed client operation group `MonitorManagementClient.tenant_action_groups`
  - Parameter `subscription_id` of client `MonitorManagementClient` is now required
  - Deleted or renamed model `TenantActionGroupList`
  - Deleted or renamed model `TenantActionGroupResource`
  - Deleted or renamed operation group `TenantActionGroupsOperations`

## 7.0.0b3 (2025-07-21)

### Features Added

  - Client `MonitorManagementClient` added operation group `data_collection_endpoints`
  - Client `MonitorManagementClient` added operation group `data_collection_rule_associations`
  - Client `MonitorManagementClient` added operation group `data_collection_rules`
  - Added model `AdxDestination`
  - Added model `AgentSetting`
  - Added model `AgentSettingsSpec`
  - Added model `AzureMonitorMetricsDestination`
  - Added model `ColumnDefinition`
  - Added model `ConfigurationAccessEndpointSpec`
  - Added model `DataCollectionEndpoint`
  - Added model `DataCollectionEndpointConfigurationAccess`
  - Added model `DataCollectionEndpointFailoverConfiguration`
  - Added model `DataCollectionEndpointLogsIngestion`
  - Added model `DataCollectionEndpointMetadata`
  - Added model `DataCollectionEndpointMetricsIngestion`
  - Added model `DataCollectionEndpointNetworkAcls`
  - Added model `DataCollectionEndpointResource`
  - Added model `DataCollectionEndpointResourceIdentity`
  - Added model `DataCollectionEndpointResourceListResult`
  - Added model `DataCollectionEndpointResourceProperties`
  - Added model `DataCollectionEndpointResourceSystemData`
  - Added model `DataCollectionRule`
  - Added model `DataCollectionRuleAgentSettings`
  - Added model `DataCollectionRuleAssociation`
  - Added model `DataCollectionRuleAssociationMetadata`
  - Added model `DataCollectionRuleAssociationProxyOnlyResource`
  - Added model `DataCollectionRuleAssociationProxyOnlyResourceListResult`
  - Added model `DataCollectionRuleAssociationProxyOnlyResourceProperties`
  - Added model `DataCollectionRuleAssociationProxyOnlyResourceSystemData`
  - Added model `DataCollectionRuleDataSources`
  - Added model `DataCollectionRuleDestinations`
  - Added model `DataCollectionRuleEndpoints`
  - Added model `DataCollectionRuleMetadata`
  - Added model `DataCollectionRuleReferences`
  - Added model `DataCollectionRuleResource`
  - Added model `DataCollectionRuleResourceIdentity`
  - Added model `DataCollectionRuleResourceListResult`
  - Added model `DataCollectionRuleResourceProperties`
  - Added model `DataCollectionRuleResourceSystemData`
  - Added model `DataFlow`
  - Added model `DataImportSources`
  - Added model `DataImportSourcesEventHub`
  - Added model `DataSourcesSpec`
  - Added model `DataSourcesSpecDataImports`
  - Added model `DestinationsSpec`
  - Added model `DestinationsSpecAzureMonitorMetrics`
  - Added model `EndpointsSpec`
  - Added model `EnrichmentData`
  - Added model `ErrorDetailAutoGenerated2`
  - Added model `ErrorResponseCommonV2`
  - Added model `EventHubDataSource`
  - Added model `EventHubDestination`
  - Added model `EventHubDirectDestination`
  - Added model `ExtensionDataSource`
  - Added model `FailoverConfigurationSpec`
  - Added model `IisLogsDataSource`
  - Added enum `KnownAgentSettingName`
  - Added enum `KnownColumnDefinitionType`
  - Added enum `KnownDataCollectionEndpointProvisioningState`
  - Added enum `KnownDataCollectionEndpointResourceKind`
  - Added enum `KnownDataCollectionRuleAssociationProvisioningState`
  - Added enum `KnownDataCollectionRuleProvisioningState`
  - Added enum `KnownDataCollectionRuleResourceKind`
  - Added enum `KnownDataFlowStreams`
  - Added enum `KnownExtensionDataSourceStreams`
  - Added enum `KnownLocationSpecProvisioningStatus`
  - Added enum `KnownLogFileTextSettingsRecordStartTimestampFormat`
  - Added enum `KnownLogFilesDataSourceFormat`
  - Added enum `KnownPerfCounterDataSourceStreams`
  - Added enum `KnownPrometheusForwarderDataSourceStreams`
  - Added enum `KnownPublicNetworkAccessOptions`
  - Added enum `KnownStorageBlobLookupType`
  - Added enum `KnownSyslogDataSourceFacilityNames`
  - Added enum `KnownSyslogDataSourceLogLevels`
  - Added enum `KnownSyslogDataSourceStreams`
  - Added enum `KnownWindowsEventLogDataSourceStreams`
  - Added enum `KnownWindowsFirewallLogsDataSourceProfileFilter`
  - Added model `LocationSpec`
  - Added model `LogAnalyticsDestination`
  - Added model `LogFileSettings`
  - Added model `LogFileSettingsText`
  - Added model `LogFileTextSettings`
  - Added model `LogFilesDataSource`
  - Added model `LogFilesDataSourceSettings`
  - Added model `LogsIngestionEndpointSpec`
  - Added model `ManagedServiceIdentity`
  - Added enum `ManagedServiceIdentityType`
  - Added model `Metadata`
  - Added model `MetricsIngestionEndpointSpec`
  - Added model `MicrosoftFabricDestination`
  - Added model `MonitoringAccountDestination`
  - Added model `NetworkRuleSet`
  - Added model `PerfCounterDataSource`
  - Added model `PlatformTelemetryDataSource`
  - Added model `PrivateLinkScopedResource`
  - Added model `PrometheusForwarderDataSource`
  - Added model `ReferencesSpec`
  - Added model `ReferencesSpecEnrichmentData`
  - Added model `ResourceForUpdate`
  - Added model `ResourceForUpdateIdentity`
  - Added model `StorageBlob`
  - Added model `StorageBlobDestination`
  - Added model `StorageTableDestination`
  - Added model `StreamDeclaration`
  - Added model `SyslogDataSource`
  - Added model `UserAssignedIdentity`
  - Added model `WindowsEventLogDataSource`
  - Added model `WindowsFirewallLogsDataSource`
  - Added operation group `DataCollectionEndpointsOperations`
  - Added operation group `DataCollectionRuleAssociationsOperations`
  - Added operation group `DataCollectionRulesOperations`

## 7.0.0b2 (2025-06-16)

### Features Added

  - Client `MonitorManagementClient` added operation group `azure_monitor_workspaces`
  - Client `MonitorManagementClient` added operation group `monitor_operations`
  - Enum `ProvisioningState` added member `CREATING`
  - Enum `ProvisioningState` added member `DELETING`
  - Added enum `ActionType`
  - Added model `AzureMonitorWorkspace`
  - Added model `AzureMonitorWorkspaceDefaultIngestionSettings`
  - Added model `AzureMonitorWorkspaceMetrics`
  - Added model `AzureMonitorWorkspaceResource`
  - Added model `AzureMonitorWorkspaceResourceForUpdate`
  - Added model `AzureMonitorWorkspaceResourceListResult`
  - Added model `AzureMonitorWorkspaceResourceProperties`
  - Added model `ErrorDetailAutoGenerated`
  - Added model `ErrorResponseAutoGenerated3`
  - Added model `IngestionSettings`
  - Added model `Metrics`
  - Added model `OperationAutoGenerated`
  - Added model `OperationDisplayAutoGenerated`
  - Added model `OperationListResultAutoGenerated`
  - Added enum `Origin`
  - Added model `PrivateEndpoint`
  - Added model `PrivateEndpointConnectionAutoGenerated`
  - Added enum `PrivateEndpointConnectionProvisioningState`
  - Added enum `PrivateEndpointServiceConnectionStatus`
  - Added model `PrivateLinkServiceConnectionState`
  - Added enum `PublicNetworkAccess`
  - Added model `ResourceAutoGenerated4`
  - Added model `ResourceAutoGenerated5`
  - Added model `TrackedResource`
  - Added operation group `AzureMonitorWorkspacesOperations`
  - Added operation group `MonitorOperationsOperations`

## 7.0.0b1 (2025-02-08)

### Features Added

  - Client `MonitorManagementClient` added operation group `action_groups`
  - Client `MonitorManagementClient` added operation group `activity_log_alerts`
  - Client `MonitorManagementClient` added operation group `activity_logs`
  - Client `MonitorManagementClient` added operation group `tenant_activity_logs`
  - Client `MonitorManagementClient` added operation group `alert_rule_incidents`
  - Client `MonitorManagementClient` added operation group `autoscale_settings`
  - Client `MonitorManagementClient` added operation group `predictive_metric`
  - Client `MonitorManagementClient` added operation group `baselines`
  - Client `MonitorManagementClient` added operation group `diagnostic_settings`
  - Client `MonitorManagementClient` added operation group `diagnostic_settings_category`
  - Client `MonitorManagementClient` added operation group `event_categories`
  - Client `MonitorManagementClient` added operation group `guest_diagnostics_settings`
  - Client `MonitorManagementClient` added operation group `guest_diagnostics_settings_association`
  - Client `MonitorManagementClient` added operation group `log_profiles`
  - Client `MonitorManagementClient` added operation group `metric_alerts`
  - Client `MonitorManagementClient` added operation group `metric_alerts_status`
  - Client `MonitorManagementClient` added operation group `metric_definitions`
  - Client `MonitorManagementClient` added operation group `metric_namespaces`
  - Client `MonitorManagementClient` added operation group `metrics`
  - Client `MonitorManagementClient` added operation group `operations`
  - Client `MonitorManagementClient` added operation group `scheduled_query_rules`
  - Client `MonitorManagementClient` added operation group `service_diagnostic_settings`
  - Client `MonitorManagementClient` added operation group `vm_insights`
  - Client `MonitorManagementClient` added operation group `private_link_scopes`
  - Client `MonitorManagementClient` added operation group `private_link_scope_operation_status`
  - Client `MonitorManagementClient` added operation group `private_link_resources`
  - Client `MonitorManagementClient` added operation group `private_endpoint_connections`
  - Client `MonitorManagementClient` added operation group `private_link_scoped_resources`
  - Client `MonitorManagementClient` added operation group `subscription_diagnostic_settings`
  - Added model `Action`
  - Added model `ActionDetail`
  - Added model `ActionGroupList`
  - Added model `ActionGroupResource`
  - Added model `ActivityLogAlertActionGroup`
  - Added model `ActivityLogAlertActionList`
  - Added model `ActivityLogAlertAllOfCondition`
  - Added model `ActivityLogAlertLeafCondition`
  - Added model `ActivityLogAlertList`
  - Added model `ActivityLogAlertPatchBody`
  - Added model `ActivityLogAlertResource`
  - Added enum `AggregationType`
  - Added enum `AggregationTypeEnum`
  - Added enum `AlertSeverity`
  - Added model `AlertingAction`
  - Added model `ArmRoleReceiver`
  - Added model `AutomationRunbookReceiver`
  - Added model `AutoscaleErrorResponse`
  - Added model `AutoscaleErrorResponseError`
  - Added model `AutoscaleNotification`
  - Added model `AutoscaleProfile`
  - Added model `AutoscaleSettingResource`
  - Added model `AutoscaleSettingResourceCollection`
  - Added model `AutoscaleSettingResourcePatch`
  - Added model `AzNsActionGroup`
  - Added model `AzureFunctionReceiver`
  - Added model `AzureMonitorPrivateLinkScope`
  - Added model `AzureMonitorPrivateLinkScopeListResult`
  - Added model `BaselineMetadata`
  - Added enum `BaselineSensitivity`
  - Added enum `CategoryType`
  - Added enum `ComparisonOperationType`
  - Added enum `ConditionalOperator`
  - Added model `Context`
  - Added enum `CreatedByType`
  - Added model `Criteria`
  - Added enum `CriterionType`
  - Added model `DataContainer`
  - Added model `DataSource`
  - Added model `DataSourceConfiguration`
  - Added enum `DataSourceKind`
  - Added enum `DataStatus`
  - Added model `DiagnosticSettingsCategoryResource`
  - Added model `DiagnosticSettingsCategoryResourceCollection`
  - Added model `DiagnosticSettingsResource`
  - Added model `DiagnosticSettingsResourceCollection`
  - Added model `Dimension`
  - Added model `DynamicMetricCriteria`
  - Added model `DynamicThresholdFailingPeriods`
  - Added enum `DynamicThresholdOperator`
  - Added enum `DynamicThresholdSensitivity`
  - Added model `EmailNotification`
  - Added model `EnableRequest`
  - Added enum `Enabled`
  - Added model `Error`
  - Added model `ErrorAdditionalInfo`
  - Added model `ErrorContract`
  - Added model `ErrorDetail`
  - Added model `ErrorDetailAdditionalInfoItem`
  - Added model `ErrorResponseAutoGenerated`
  - Added model `ErrorResponseAutoGenerated2`
  - Added model `ErrorResponseCommon`
  - Added model `ErrorResponseError`
  - Added model `ErrorResponseErrorAdditionalInfoItem`
  - Added model `EtwEventConfiguration`
  - Added model `EtwProviderConfiguration`
  - Added model `EventCategoryCollection`
  - Added model `EventData`
  - Added model `EventDataCollection`
  - Added model `EventHubReceiver`
  - Added enum `EventLevel`
  - Added model `EventLogConfiguration`
  - Added model `GuestDiagnosticSettingsAssociationList`
  - Added model `GuestDiagnosticSettingsAssociationResource`
  - Added model `GuestDiagnosticSettingsAssociationResourcePatch`
  - Added model `GuestDiagnosticSettingsList`
  - Added enum `GuestDiagnosticSettingsOsType`
  - Added model `GuestDiagnosticSettingsPatchResource`
  - Added model `GuestDiagnosticSettingsResource`
  - Added model `HttpRequestInfo`
  - Added model `Incident`
  - Added model `IncidentListResult`
  - Added model `ItsmReceiver`
  - Added model `LocalizableString`
  - Added model `LocalizableStringAutoGenerated`
  - Added model `LogMetricTrigger`
  - Added model `LogProfileCollection`
  - Added model `LogProfileResource`
  - Added model `LogProfileResourcePatch`
  - Added model `LogSearchRuleResource`
  - Added model `LogSearchRuleResourceCollection`
  - Added model `LogSearchRuleResourcePatch`
  - Added model `LogSettings`
  - Added model `LogSettingsAutoGenerated`
  - Added model `LogToMetricAction`
  - Added model `LogicAppReceiver`
  - Added model `MetadataValue`
  - Added model `Metric`
  - Added model `MetricAlertAction`
  - Added model `MetricAlertCriteria`
  - Added model `MetricAlertMultipleResourceMultipleMetricCriteria`
  - Added model `MetricAlertResource`
  - Added model `MetricAlertResourceCollection`
  - Added model `MetricAlertResourcePatch`
  - Added model `MetricAlertSingleResourceMultipleMetricCriteria`
  - Added model `MetricAlertStatus`
  - Added model `MetricAlertStatusCollection`
  - Added model `MetricAlertStatusProperties`
  - Added model `MetricAvailability`
  - Added model `MetricBaselinesResponse`
  - Added enum `MetricClass`
  - Added model `MetricCriteria`
  - Added model `MetricDefinition`
  - Added model `MetricDefinitionCollection`
  - Added model `MetricDimension`
  - Added model `MetricNamespace`
  - Added model `MetricNamespaceCollection`
  - Added model `MetricNamespaceName`
  - Added model `MetricSettings`
  - Added model `MetricSettingsAutoGenerated`
  - Added model `MetricSingleDimension`
  - Added enum `MetricStatisticType`
  - Added model `MetricTrigger`
  - Added enum `MetricTriggerType`
  - Added enum `MetricUnit`
  - Added model `MetricValue`
  - Added model `MultiMetricCriteria`
  - Added enum `NamespaceClassification`
  - Added model `NotificationRequestBody`
  - Added enum `Odatatype`
  - Added enum `OnboardingStatus`
  - Added model `Operation`
  - Added model `OperationDisplay`
  - Added model `OperationListResult`
  - Added model `OperationStatus`
  - Added enum `Operator`
  - Added model `PerformanceCounterConfiguration`
  - Added model `PredictiveAutoscalePolicy`
  - Added enum `PredictiveAutoscalePolicyScaleMode`
  - Added model `PredictiveResponse`
  - Added model `PredictiveValue`
  - Added model `PrivateEndpointConnection`
  - Added model `PrivateEndpointConnectionListResult`
  - Added model `PrivateEndpointProperty`
  - Added model `PrivateLinkResource`
  - Added model `PrivateLinkResourceListResult`
  - Added model `PrivateLinkScopesResource`
  - Added model `PrivateLinkServiceConnectionStateProperty`
  - Added enum `ProvisioningState`
  - Added model `ProxyOnlyResource`
  - Added model `ProxyResource`
  - Added enum `QueryType`
  - Added model `Recurrence`
  - Added enum `RecurrenceFrequency`
  - Added model `RecurrentSchedule`
  - Added model `Resource`
  - Added model `ResourceAutoGenerated`
  - Added model `ResourceAutoGenerated2`
  - Added model `ResourceAutoGenerated3`
  - Added model `Response`
  - Added model `ResponseWithError`
  - Added enum `ResultType`
  - Added model `RetentionPolicy`
  - Added model `ScaleAction`
  - Added model `ScaleCapacity`
  - Added enum `ScaleDirection`
  - Added model `ScaleRule`
  - Added model `ScaleRuleMetricDimension`
  - Added enum `ScaleRuleMetricDimensionOperationType`
  - Added enum `ScaleType`
  - Added model `Schedule`
  - Added model `ScopedResource`
  - Added model `ScopedResourceListResult`
  - Added model `SenderAuthorization`
  - Added model `ServiceDiagnosticSettingsResource`
  - Added model `ServiceDiagnosticSettingsResourcePatch`
  - Added model `SingleBaseline`
  - Added model `SingleMetricBaseline`
  - Added model `SinkConfiguration`
  - Added enum `SinkConfigurationKind`
  - Added model `Source`
  - Added model `SubscriptionDiagnosticSettingsResource`
  - Added model `SubscriptionDiagnosticSettingsResourceCollection`
  - Added model `SubscriptionLogSettings`
  - Added model `SubscriptionProxyOnlyResource`
  - Added model `SystemData`
  - Added model `TagsResource`
  - Added model `TestNotificationDetailsResponse`
  - Added enum `TimeAggregationType`
  - Added model `TimeSeriesBaseline`
  - Added model `TimeSeriesElement`
  - Added model `TimeWindow`
  - Added model `TriggerCondition`
  - Added model `VMInsightsOnboardingStatus`
  - Added model `WebhookNotification`
  - Added model `WebtestLocationAvailabilityCriteria`
  - Added model `WorkspaceInfo`

### Breaking Changes

  - This package now only targets the latest Api-Version available on Azure and removes APIs of other Api-Version. After this change, the package can have much smaller size. If your application requires a specific and non-latest Api-Version, it's recommended to pin this package to the previous released version; If your application always only use latest Api-Version, please ignore this change.
  - Deleted or renamed client operation group `MonitorManagementClient.tenant_action_groups`
  - Parameter `subscription_id` of client `MonitorManagementClient` is now required
  - Deleted or renamed model `TenantActionGroupList`
  - Deleted or renamed model `TenantActionGroupResource`
  - Deleted or renamed model `TenantActionGroupsOperations`

## 6.0.2 (2023-08-22)

### Bugs Fixed

  - Encode `{}` even if skip_quoto is True  #31346

## 6.0.1 (2023-05-04)

### Other Changes

  - Fixed annotation about namespace

## 6.0.0 (2023-03-20)

### Features Added

  - Added operation MetricDefinitionsOperations.list_at_subscription_scope
  - Added operation MetricsOperations.list_at_subscription_scope
  - Added operation MetricsOperations.list_at_subscription_scope_post
  - Added operation group AzureMonitorWorkspacesOperations
  - Added operation group MonitorOperationsOperations
  - Added operation group TenantActionGroupsOperations
  - Model AzureMonitorPrivateLinkScope has a new parameter system_data
  - Model Condition has a new parameter metric_name
  - Model DataCollectionEndpoint has a new parameter failover_configuration
  - Model DataCollectionEndpoint has a new parameter metadata
  - Model DataCollectionEndpoint has a new parameter metrics_ingestion
  - Model DataCollectionEndpoint has a new parameter private_link_scoped_resources
  - Model DataCollectionEndpointResource has a new parameter failover_configuration
  - Model DataCollectionEndpointResource has a new parameter identity
  - Model DataCollectionEndpointResource has a new parameter metadata
  - Model DataCollectionEndpointResource has a new parameter metrics_ingestion
  - Model DataCollectionEndpointResource has a new parameter private_link_scoped_resources
  - Model DataCollectionEndpointResourceProperties has a new parameter failover_configuration
  - Model DataCollectionEndpointResourceProperties has a new parameter metadata
  - Model DataCollectionEndpointResourceProperties has a new parameter metrics_ingestion
  - Model DataCollectionEndpointResourceProperties has a new parameter private_link_scoped_resources
  - Model DataCollectionRuleAssociationMetadata has a new parameter provisioned_by_resource_id
  - Model DataCollectionRuleDataSources has a new parameter data_imports
  - Model DataCollectionRuleDataSources has a new parameter platform_telemetry
  - Model DataCollectionRuleDataSources has a new parameter prometheus_forwarder
  - Model DataCollectionRuleDataSources has a new parameter windows_firewall_logs
  - Model DataCollectionRuleDestinations has a new parameter event_hubs
  - Model DataCollectionRuleDestinations has a new parameter event_hubs_direct
  - Model DataCollectionRuleDestinations has a new parameter monitoring_accounts
  - Model DataCollectionRuleDestinations has a new parameter storage_accounts
  - Model DataCollectionRuleDestinations has a new parameter storage_blobs_direct
  - Model DataCollectionRuleDestinations has a new parameter storage_tables_direct
  - Model DataCollectionRuleMetadata has a new parameter provisioned_by_resource_id
  - Model DataCollectionRuleResource has a new parameter identity
  - Model DataFlow has a new parameter built_in_transform
  - Model DataSourcesSpec has a new parameter data_imports
  - Model DataSourcesSpec has a new parameter platform_telemetry
  - Model DataSourcesSpec has a new parameter prometheus_forwarder
  - Model DataSourcesSpec has a new parameter windows_firewall_logs
  - Model DestinationsSpec has a new parameter event_hubs
  - Model DestinationsSpec has a new parameter event_hubs_direct
  - Model DestinationsSpec has a new parameter monitoring_accounts
  - Model DestinationsSpec has a new parameter storage_accounts
  - Model DestinationsSpec has a new parameter storage_blobs_direct
  - Model DestinationsSpec has a new parameter storage_tables_direct
  - Model Metadata has a new parameter provisioned_by_resource_id
  - Model Operation has a new parameter action_type
  - Model Operation has a new parameter origin
  - Model PrivateLinkResource has a new parameter required_zone_names
  - Model ResourceForUpdate has a new parameter identity
  - Model ScheduledQueryRuleResource has a new parameter auto_mitigate
  - Model ScheduledQueryRuleResource has a new parameter check_workspace_alerts_storage_configured
  - Model ScheduledQueryRuleResource has a new parameter identity
  - Model ScheduledQueryRuleResource has a new parameter is_workspace_alerts_storage_configured
  - Model ScheduledQueryRuleResource has a new parameter public_network_access
  - Model ScheduledQueryRuleResource has a new parameter rule_resolve_configuration
  - Model ScheduledQueryRuleResource has a new parameter skip_query_validation
  - Model ScheduledQueryRuleResource has a new parameter system_data
  - Model ScheduledQueryRuleResourceCollection has a new parameter next_link
  - Model ScheduledQueryRuleResourcePatch has a new parameter auto_mitigate
  - Model ScheduledQueryRuleResourcePatch has a new parameter check_workspace_alerts_storage_configured
  - Model ScheduledQueryRuleResourcePatch has a new parameter identity
  - Model ScheduledQueryRuleResourcePatch has a new parameter is_workspace_alerts_storage_configured
  - Model ScheduledQueryRuleResourcePatch has a new parameter public_network_access
  - Model ScheduledQueryRuleResourcePatch has a new parameter rule_resolve_configuration
  - Model ScheduledQueryRuleResourcePatch has a new parameter skip_query_validation
  - Model ScopedResource has a new parameter system_data
  - Operation MetricsOperations.list has a new optional parameter auto_adjust_timegrain
  - Operation MetricsOperations.list has a new optional parameter validate_dimensions

### Breaking Changes

  - Model AzureMonitorPrivateLinkScope has a new required parameter access_mode_settings
  - Model Operation no longer has parameter service_specification
  - Model OperationDisplay no longer has parameter publisher
  - Model PrivateEndpointConnectionListResult no longer has parameter next_link
  - Model PrivateLinkResourceListResult no longer has parameter next_link
  - Removed operation ActionGroupsOperations.begin_create_notifications_at_resource_group_level
  - Removed operation ActionGroupsOperations.begin_post_test_notifications
  - Removed operation ActionGroupsOperations.get_test_notifications
  - Removed operation ActionGroupsOperations.get_test_notifications_at_resource_group_level

## 5.0.1 (2022-09-30)

### Bugs Fixed
  
  - Fix paging problem about `api_version`

## 5.0.0 (2022-09-19)

### Features Added

  - Model Resource has a new parameter system_data
  - Model Resource has a new parameter tags

### Breaking Changes

  - Model Resource has a new required parameter location

## 4.0.1 (2022-08-02)

**Other Change**

  - Fix package structure

## 4.0.0 (2022-08-02)

**Features**

  - Added operation ActionGroupsOperations.begin_create_notifications_at_action_group_resource_level
  - Added operation ActionGroupsOperations.begin_create_notifications_at_resource_group_level
  - Added operation ActionGroupsOperations.get_test_notifications_at_action_group_resource_level
  - Added operation ActionGroupsOperations.get_test_notifications_at_resource_group_level

**Breaking changes**

  - Model ActionGroupResource no longer has parameter identity
  - Model ActionGroupResource no longer has parameter kind
  - Model AzureResource no longer has parameter identity
  - Model AzureResource no longer has parameter kind
  - Removed operation group BaselineOperations
  - Removed operation group MetricBaselineOperations

## 3.1.0 (2022-03-16)

**Features**

  - Added operation DataCollectionRuleAssociationsOperations.list_by_data_collection_endpoint
  - Model DataCollectionRule has a new parameter data_collection_endpoint_id
  - Model DataCollectionRule has a new parameter metadata
  - Model DataCollectionRule has a new parameter stream_declarations
  - Model DataCollectionRuleAssociation has a new parameter metadata
  - Model DataCollectionRuleAssociationProxyOnlyResource has a new parameter metadata
  - Model DataCollectionRuleAssociationProxyOnlyResourceProperties has a new parameter metadata
  - Model DataCollectionRuleDataSources has a new parameter iis_logs
  - Model DataCollectionRuleDataSources has a new parameter log_files
  - Model DataCollectionRuleResource has a new parameter data_collection_endpoint_id
  - Model DataCollectionRuleResource has a new parameter metadata
  - Model DataCollectionRuleResource has a new parameter stream_declarations
  - Model DataCollectionRuleResourceProperties has a new parameter data_collection_endpoint_id
  - Model DataCollectionRuleResourceProperties has a new parameter metadata
  - Model DataCollectionRuleResourceProperties has a new parameter stream_declarations
  - Model DataFlow has a new parameter output_stream
  - Model DataFlow has a new parameter transform_kql
  - Model DataSourcesSpec has a new parameter iis_logs
  - Model DataSourcesSpec has a new parameter log_files

## 3.0.0 (2021-11-05)

**Features**

  - Model LogAnalyticsDestination has a new parameter workspace_id
  - Model LogSettings has a new parameter category_group
  - Model Baseline has a new parameter timestamps
  - Model Baseline has a new parameter error_type
  - Model Baseline has a new parameter prediction_result_type
  - Model Metric has a new parameter error_message
  - Model Metric has a new parameter error_code
  - Model Metric has a new parameter display_description
  - Model ManagementGroupDiagnosticSettingsResource has a new parameter system_data
  - Model ManagementGroupDiagnosticSettingsResource has a new parameter marketplace_partner_id
  - Model DataCollectionRuleAssociationProxyOnlyResourceProperties has a new parameter data_collection_endpoint_id
  - Model SubscriptionDiagnosticSettingsResource has a new parameter system_data
  - Model SubscriptionDiagnosticSettingsResource has a new parameter marketplace_partner_id
  - Model TimeSeriesBaseline has a new parameter metadata_values
  - Model DataCollectionRuleAssociationProxyOnlyResource has a new parameter system_data
  - Model DataCollectionRuleAssociationProxyOnlyResource has a new parameter data_collection_endpoint_id
  - Model CalculateBaselineResponse has a new parameter internal_operation_id
  - Model CalculateBaselineResponse has a new parameter statistics
  - Model CalculateBaselineResponse has a new parameter error_type
  - Model DataCollectionRule has a new parameter immutable_id
  - Model AlertRuleResourcePatch has a new parameter provisioning_state
  - Model AlertRuleResourcePatch has a new parameter action
  - Model OperationDisplay has a new parameter description
  - Model OperationDisplay has a new parameter publisher
  - Model ManagementGroupLogSettings has a new parameter category_group
  - Model SubscriptionLogSettings has a new parameter category_group
  - Model DiagnosticSettingsCategoryResource has a new parameter system_data
  - Model DiagnosticSettingsCategoryResource has a new parameter category_groups
  - Model BaselineResponse has a new parameter internal_operation_id
  - Model BaselineResponse has a new parameter metdata
  - Model BaselineResponse has a new parameter error_type
  - Model BaselineResponse has a new parameter prediction_result_type
  - Model ActionGroupResource has a new parameter event_hub_receivers
  - Model ActionGroupResource has a new parameter kind
  - Model ActionGroupResource has a new parameter identity
  - Model AutoscaleSettingResource has a new parameter system_data
  - Model AutoscaleSettingResource has a new parameter predictive_autoscale_policy
  - Model AutoscaleSettingResource has a new parameter target_resource_location
  - Model ScheduledQueryRuleResourcePatch has a new parameter is_legacy_log_analytics_rule
  - Model ScheduledQueryRuleResourcePatch has a new parameter override_query_time_range
  - Model ScheduledQueryRuleResourcePatch has a new parameter display_name
  - Model ScheduledQueryRuleResourcePatch has a new parameter created_with_api_version
  - Model ExtensionDataSource has a new parameter input_data_sources
  - Model LogSearchRuleResource has a new parameter created_with_api_version
  - Model LogSearchRuleResource has a new parameter kind
  - Model LogSearchRuleResource has a new parameter auto_mitigate
  - Model LogSearchRuleResource has a new parameter display_name
  - Model LogSearchRuleResource has a new parameter etag
  - Model LogSearchRuleResource has a new parameter is_legacy_log_analytics_rule
  - Model AutoscaleSettingResourcePatch has a new parameter predictive_autoscale_policy
  - Model AutoscaleSettingResourcePatch has a new parameter target_resource_location
  - Model RuleDataSource has a new parameter resource_location
  - Model RuleDataSource has a new parameter metric_namespace
  - Model RuleDataSource has a new parameter legacy_resource_id
  - Model AlertRuleResource has a new parameter provisioning_state
  - Model AlertRuleResource has a new parameter action
  - Model Operation has a new parameter service_specification
  - Model Operation has a new parameter is_data_action
  - Model MetricDefinition has a new parameter metric_class
  - Model MetricDefinition has a new parameter category
  - Model MetricDefinition has a new parameter display_description
  - Model DataCollectionRuleAssociation has a new parameter data_collection_endpoint_id
  - Model MetricTrigger has a new parameter metric_resource_location
  - Model MetricTrigger has a new parameter divide_per_instance
  - Model MetricAlertResource has a new parameter is_migrated
  - Model RuleManagementEventDataSource has a new parameter resource_location
  - Model RuleManagementEventDataSource has a new parameter metric_namespace
  - Model RuleManagementEventDataSource has a new parameter legacy_resource_id
  - Model MetricAlertResourcePatch has a new parameter is_migrated
  - Model ScheduledQueryRuleResource has a new parameter created_with_api_version
  - Model ScheduledQueryRuleResource has a new parameter kind
  - Model ScheduledQueryRuleResource has a new parameter etag
  - Model ScheduledQueryRuleResource has a new parameter display_name
  - Model ScheduledQueryRuleResource has a new parameter is_legacy_log_analytics_rule
  - Model ScheduledQueryRuleResource has a new parameter override_query_time_range
  - Model RuleMetricDataSource has a new parameter resource_location
  - Model RuleMetricDataSource has a new parameter metric_namespace
  - Model RuleMetricDataSource has a new parameter legacy_resource_id
  - Model DiagnosticSettingsResource has a new parameter system_data
  - Model DiagnosticSettingsResource has a new parameter marketplace_partner_id
  - Model MetricNamespace has a new parameter classification
  - Model DataCollectionRuleResource has a new parameter system_data
  - Model DataCollectionRuleResource has a new parameter immutable_id
  - Model DataCollectionRuleResource has a new parameter kind
  - Model DataCollectionRuleResourceProperties has a new parameter immutable_id
  - Added operation ActionGroupsOperations.begin_post_test_notifications
  - Added operation ActionGroupsOperations.get_test_notifications
  - Added operation group PredictiveMetricOperations
  - Added operation group DataCollectionEndpointsOperations

**Breaking changes**

  - Parameter scopes of model MetricAlertResource is now required
  - Operation ActivityLogAlertsOperations.update has a new signature
  - Operation ActivityLogAlertsOperations.create_or_update has a new signature
  - Operation SubscriptionDiagnosticSettingsOperations.list has a new signature
  - Operation SubscriptionDiagnosticSettingsOperations.get has a new signature
  - Operation SubscriptionDiagnosticSettingsOperations.delete has a new signature
  - Operation SubscriptionDiagnosticSettingsOperations.create_or_update has a new signature
  - Model PerfCounterDataSource no longer has parameter scheduled_transfer_period
  - Model ManagementGroupDiagnosticSettingsResource no longer has parameter location
  - Model SubscriptionDiagnosticSettingsResource no longer has parameter location
  - Model TimeSeriesBaseline no longer has parameter metadata
  - Model ErrorResponse no longer has parameter target
  - Model ErrorResponse no longer has parameter details
  - Model ErrorResponse no longer has parameter additional_info
  - Model WindowsEventLogDataSource no longer has parameter scheduled_transfer_period
  - Model BaselineResponse no longer has parameter metadata


## 2.0.0 (2020-12-25)

**Breaking changes**

- Client name changed from MonitorClient to MonitorManagementClient

## 1.0.1 (2020-09-18)

**Bug fix**

  - Require azure-mgmt-core>=1.2.0 in setup.py

## 1.0.0 (2020-09-16)

**Features**

  - Model MultiMetricCriteria has a new parameter skip_metric_validation
  - Model DynamicMetricCriteria has a new parameter skip_metric_validation
  - Model MetricTrigger has a new parameter dimensions
  - Model MetricTrigger has a new parameter metric_namespace
  - Model MetricCriteria has a new parameter skip_metric_validation
  - Added operation group SubscriptionDiagnosticSettingsOperations
  - Added operation group ManagementGroupDiagnosticSettingsOperations

## 1.0.0b1 (2020-06-17)

This is beta preview version.

This version uses a next-generation code generator that introduces important breaking changes, but also important new features (like unified authentication and async programming).

**General breaking changes**

- Credential system has been completly revamped:

  - `azure.common.credentials` or `msrestazure.azure_active_directory` instances are no longer supported, use the `azure-identity` classes instead: https://pypi.org/project/azure-identity/
  - `credentials` parameter has been renamed `credential`

- The `config` attribute no longer exists on a client, configuration should be passed as kwarg. Example: `MyClient(credential, subscription_id, enable_logging=True)`. For a complete set of
  supported options, see the [parameters accept in init documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)
- You can't import a `version` module anymore, use `__version__` instead
- Operations that used to return a `msrest.polling.LROPoller` now returns a `azure.core.polling.LROPoller` and are prefixed with `begin_`.
- Exceptions tree have been simplified and most exceptions are now `azure.core.exceptions.HttpResponseError` (`CloudError` has been removed).
- Most of the operation kwarg have changed. Some of the most noticeable:

  - `raw` has been removed. Equivalent feature can be found using `cls`, a callback that will give access to internal HTTP response for advanced user
  - For a complete set of
  supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry) for an overview.


## 0.10.0 (2020-06-08)

**Features**

  - Model WebtestLocationAvailabilityCriteria has a new parameter additional_properties
  - Added operation group SubscriptionDiagnosticSettingsOperations

**Breaking changes**

  - Model WebtestLocationAvailabilityCriteria has a new required parameter odatatype

## 0.9.0 (2020-04-09)

**Features**

  - Model AzureMonitorPrivateLinkScope has a new parameter private_endpoint_connections

**Breaking changes**

  - Operation PrivateLinkScopedResourcesOperations.create_or_update has a new signature
  - Model PrivateEndpointConnection no longer has parameter tags
  - Model PrivateLinkResource no longer has parameter tags
  - Model ScopedResource no longer has parameter tags
  - Model ProxyResource no longer has parameter tags
  - Operation PrivateEndpointConnectionsOperations.create_or_update has a new signature
  - Model ErrorResponse has a new signature

## 0.8.0 (2020-03-14)

**Features**

- Model DiagnosticSettingsResource has a new parameter log_analytics_destination_type
- Model ProxyResource has a new parameter tags
- Model MetricAlertAction has a new parameter web_hook_properties
- Added operation group PrivateEndpointConnectionsOperations
- Added operation group PrivateLinkScopedResourcesOperations
- Added operation group PrivateLinkScopeOperationStatusOperations
- Added operation group PrivateLinkResourcesOperations
- Added operation group PrivateLinkScopesOperations

**Breaking changes**

- Model MetricAlertAction no longer has parameter webhook_properties
- Model ErrorResponse has a new signature


## 0.7.0 (2019-06-24)

This package now support profiles as parameter for sovereign cloud
support

**Features**

  - Model MultiMetricCriteria has a new parameter metric_namespace
  - Model MultiMetricCriteria has a new parameter dimensions
  - Added operation group ServiceDiagnosticSettingsOperations
  - Added operation group GuestDiagnosticsSettingsOperations
  - Added operation group BaselinesOperations
  - Added operation group GuestDiagnosticsSettingsAssociationOperations
  - Added operation group BaselineOperations

**Breaking changes**

  - Operation MetricBaselineOperations.get has a new signature
  - Model MultiMetricCriteria has a new required parameter name
  - Model MultiMetricCriteria has a new required parameter
    time_aggregation
  - Model MultiMetricCriteria has a new required parameter metric_name
  - Model ArmRoleReceiver has a new required parameter
    use_common_alert_schema
  - Model LogicAppReceiver has a new required parameter
    use_common_alert_schema
  - Model AzureFunctionReceiver has a new required parameter
    use_common_alert_schema
  - Model EmailReceiver has a new required parameter
    use_common_alert_schema
  - Model AutomationRunbookReceiver has a new required parameter
    use_common_alert_schema
  - Model WebhookReceiver has a new signature

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes for some imports. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - MonitorManagementClient cannot be imported from
    `azure.mgmt.monitor.monitor_management_client` anymore (import
    from `azure.mgmt.monitor` works like before)
  - MonitorManagementClientConfiguration import has been moved from
    `azure.mgmt.monitor.monitor_management_client` to
    `azure.mgmt.monitor`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.monitor.models.my_class` (import from
    `azure.mgmt.monitor.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.monitor.operations.my_class_operations` (import from
    `azure.mgmt.monitor.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.6.0 (2018-03-06)

**Features**

  - Model MetricCriteria has a new parameter additional_properties
  - Model MetricAlertResource has a new parameter
    target_resource_region
  - Model MetricAlertResource has a new parameter target_resource_type
  - Model MetricAlertResourcePatch has a new parameter
    target_resource_region
  - Model MetricAlertResourcePatch has a new parameter
    target_resource_type
  - Model ActionGroupResource has a new parameter arm_role_receivers
  - Model DiagnosticSettingsResource has a new parameter
    service_bus_rule_id
  - Added operation AutoscaleSettingsOperations.list_by_subscription
  - Added operation AlertRulesOperations.list_by_subscription
  - Added operation group MetricNamespacesOperations
  - Added operation group VMInsightsOperations

**Breaking changes**

  - Model MetricCriteria has a new required parameter criterion_type

## 0.5.2 (2018-06-06)

**Features**

  - Model ActionGroupResource has a new parameter voice_receivers
  - Model ActionGroupResource has a new parameter
    azure_function_receivers
  - Model ActionGroupResource has a new parameter logic_app_receivers
  - Added operation group MetricAlertsOperations
  - Added operation group ScheduledQueryRulesOperations
  - Added operation group MetricAlertsStatusOperations

## 0.5.1 (2018-04-16)

**Bugfixes**

  - Fix some invalid models in Python 3
  - Compatibility of the sdist with wheel 0.31.0

## 0.5.0 (2017-03-19)

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes.

  - Model signatures now use only keyword-argument syntax. All
    positional arguments must be re-written as keyword-arguments. To
    keep auto-completion in most cases, models are now generated for
    Python 2 and Python 3. Python 3 uses the "*" syntax for
    keyword-only arguments.
  - Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to
    improve the behavior when unrecognized enum values are encountered.
    While this is not a breaking change, the distinctions are important,
    and are documented here:
    <https://docs.python.org/3/library/enum.html#others> At a glance:
      - "is" should not be used at all.
      - "format" will return the string value, where "%s" string
        formatting will return `NameOfEnum.stringvalue`. Format syntax
        should be prefered.
  - New Long Running Operation:
      - Return type changes from
        `msrestazure.azure_operation.AzureOperationPoller` to
        `msrest.polling.LROPoller`. External API is the same.
      - Return type is now **always** a `msrest.polling.LROPoller`,
        regardless of the optional parameters used.
      - The behavior has changed when using `raw=True`. Instead of
        returning the initial call result as `ClientRawResponse`,
        without polling, now this returns an LROPoller. After polling,
        the final resource will be returned as a `ClientRawResponse`.
      - New `polling` parameter. The default behavior is
        `Polling=True` which will poll using ARM algorithm. When
        `Polling=False`, the response of the initial call will be
        returned without polling.
      - `polling` parameter accepts instances of subclasses of
        `msrest.polling.PollingMethod`.
      - `add_done_callback` will no longer raise if called after
        polling is finished, but will instead execute the callback right
        away.

**Bugfixes**

  - Fix invalid type of "top" in metrics.list operation

**Features**

  - New operation group metric_baseline
  - Add attribute action_group_resource itsm_receivers
  - Add operation action_groups.update
  - Add new parameter "metricnames" to metrics.list
  - Add new parameter "metricnamespace" to metrics.list
  - All operations group have now a "models" attribute

New ApiVersion version of metrics to 2018-01-01

## 0.4.0 (2017-10-25)

**Features**

  - Merge into this package the "azure-monitor" package including
    following operations groups
      - event categories
      - activity log
      - tenant activity log
      - metrics definitions
      - metrics
  - Adding new multi-dimensional metrics API

**Breaking changes**

  - Some exceptions have moved from CloudError to ErrorResponseException
  - "service_diagnostic_settings" renamed to "diagnostic_settings"
  - Update API version of "metrics". Migrating from "azure-monitor" to
    "metrics" here needs to be rewritten.

**Bug fixes**

  - Improving HTTP status code check for better exception

## 0.3.0 (2017-06-30)

**Features**

  - Add action_groups operation group
  - Add alert_rules.update method
  - Add autoscale_settings.update method
  - Add log_profiles.update method

**Breaking changes**

  - activity_log_alerts.update has now flatten parameters
    "tags/enabled"

## 0.2.1 (2017-04-26)

  - Removal of a REST endpoint not ready to release.

## 0.2.0 (2017-04-19)

  - Add ActivityLogAlerts and DiagnosticSettings
  - Minor improvements, might be breaking
  - This wheel package is now built with the azure wheel extension

## 0.1.0 (2017-02-16)

  - Initial Release
