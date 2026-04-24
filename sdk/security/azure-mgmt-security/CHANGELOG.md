# Release History

## 8.0.0b2 (2026-04-24)

### Features Added

  - Model `AadExternalSecuritySolution` added property `system_data`
  - Model `AdvancedThreatProtectionSetting` added property `properties`
  - Model `AdvancedThreatProtectionSetting` added property `system_data`
  - Model `Alert` added property `system_data`
  - Model `AlertSyncSettings` added property `properties`
  - Model `AlertSyncSettings` added property `system_data`
  - Model `AlertsSuppressionRule` added property `system_data`
  - Model `AllowedConnectionsResource` added property `system_data`
  - Model `ApiCollection` added property `system_data`
  - Model `Application` added property `system_data`
  - Model `AscLocation` added property `system_data`
  - Model `AtaExternalSecuritySolution` added property `system_data`
  - Model `AutoProvisioningSetting` added property `system_data`
  - Model `Automation` added property `system_data`
  - Model `AutomationUpdateModel` added property `properties`
  - Model `AzureServersSetting` added property `properties`
  - Model `CefExternalSecuritySolution` added property `system_data`
  - Model `Compliance` added property `system_data`
  - Model `ComplianceResult` added property `system_data`
  - Model `DataExportSettings` added property `properties`
  - Model `DataExportSettings` added property `system_data`
  - Model `DefenderForStorageSetting` added property `system_data`
  - Model `DeviceSecurityGroup` added property `system_data`
  - Model `DiscoveredSecuritySolution` added property `system_data`
  - Model `ExternalSecuritySolution` added property `properties`
  - Model `ExternalSecuritySolution` added property `system_data`
  - Model `GetSensitivitySettingsResponse` added property `system_data`
  - Model `GovernanceAssignment` added property `system_data`
  - Model `GovernanceRule` added property `system_data`
  - Model `HealthReport` added property `system_data`
  - Model `InformationProtectionPolicy` added property `system_data`
  - Model `IoTSecurityAggregatedAlert` added property `system_data`
  - Model `IoTSecurityAggregatedRecommendation` added property `system_data`
  - Model `IoTSecuritySolutionAnalyticsModel` added property `system_data`
  - Model `IoTSecuritySolutionModel` added property `properties`
  - Model `JitNetworkAccessPolicy` added property `system_data`
  - Model `MdeOnboardingData` added property `system_data`
  - Model `Pricing` added property `system_data`
  - Enum `ProvisioningState` added member `CANCELED`
  - Enum `ProvisioningState` added member `CREATING`
  - Enum `ProvisioningState` added member `DELETING`
  - Enum `ProvisioningState` added member `IN_PROGRESS`
  - Model `ProxyResource` added property `system_data`
  - Model `RegulatoryComplianceAssessment` added property `system_data`
  - Model `RegulatoryComplianceControl` added property `system_data`
  - Model `RegulatoryComplianceStandard` added property `system_data`
  - Model `Resource` added property `system_data`
  - Model `ResourceDetails` added property `id`
  - Model `ResourceDetails` added property `connector_id`
  - Model `RuleResults` added property `system_data`
  - Model `RulesResults` added property `next_link`
  - Model `ScanResult` added property `system_data`
  - Model `ScanV2` added property `system_data`
  - Model `SecureScoreControlDefinitionItem` added property `system_data`
  - Model `SecureScoreControlDetails` added property `properties`
  - Model `SecureScoreControlDetails` added property `system_data`
  - Model `SecureScoreItem` added property `system_data`
  - Model `SecurityAssessment` added property `properties`
  - Model `SecurityAssessment` added property `system_data`
  - Model `SecurityAssessmentMetadataResponse` added property `properties`
  - Model `SecurityAssessmentMetadataResponse` added property `system_data`
  - Model `SecurityAssessmentResponse` added property `properties`
  - Model `SecurityAssessmentResponse` added property `system_data`
  - Model `SecurityOperator` added property `system_data`
  - Model `SecuritySolution` added property `system_data`
  - Model `SecuritySolutionsReferenceData` added property `system_data`
  - Model `SecurityStandard` added property `system_data`
  - Model `SecuritySubAssessment` added property `system_data`
  - Model `SecurityTask` added property `system_data`
  - Model `ServerVulnerabilityAssessment` added property `system_data`
  - Model `ServerVulnerabilityAssessmentsSetting` added property `properties`
  - Model `Setting` added property `properties`
  - Model `Setting` added property `system_data`
  - Enum `SettingName` added member `CURRENT`
  - Enum `Severity` added member `CRITICAL`
  - Enum `Source` added member `AWS`
  - Enum `Source` added member `GCP`
  - Model `SqlVulnerabilityAssessmentScanOperationResult` added property `system_data`
  - Model `SqlVulnerabilityAssessmentSettings` added property `system_data`
  - Model `StandardAssignment` added property `system_data`
  - Enum `State` added member `OFF`
  - Enum `State` added member `ON`
  - Model `TopologyResource` added property `system_data`
  - Model `TrackedResource` added property `system_data`
  - Model `UpdateIotSecuritySolutionData` added property `properties`
  - Model `WorkspaceSetting` added property `system_data`
  - Added model `AdvancedThreatProtectionProperties`
  - Added model `AlertSyncSettingProperties`
  - Added enum `ArmActionType`
  - Added model `ArmErrorAdditionalInfo`
  - Added model `CloudError`
  - Added model `CommonResourceDetails`
  - Added model `DataExportSettingProperties`
  - Added model `DefenderCspmAwsOfferingCiemCiemDiscovery`
  - Added model `DefenderCspmAwsOfferingCiemCiemOidc`
  - Added model `ExtensionResource`
  - Added model `IoTSecuritySolutionProperties`
  - Added enum `MinimalRiskLevel`
  - Added enum `MinimalSeverity`
  - Added model `NotificationsSource`
  - Added model `NotificationsSourceAlert`
  - Added model `NotificationsSourceAttackPath`
  - Added enum `OperationResultStatus`
  - Added model `PrivateLinkGroupResource`
  - Added model `PrivateLinkProperties`
  - Added model `Private_link_parameters`
  - Added enum `ResourceIdentityType`
  - Added model `ScoreDetails`
  - Added model `SecureScoreControlScoreDetails`
  - Added model `SecurityAssessmentPropertiesBaseRiskPathsItemEdgeItem`
  - Added model `SecurityAssessmentPropertiesBaseRiskPathsItemNodesItem`
  - Added model `SecurityContact`
  - Added enum `SecurityContactName`
  - Added model `SecurityContactProperties`
  - Added model `SecurityContactPropertiesNotificationsByRole`
  - Added enum `SecurityContactRole`
  - Added model `ServerVulnerabilityAssessmentsAzureSettingProperties`
  - Added enum `SourceType`
  - Added enum `StatusEnum`
  - Added model `UpdateIoTSecuritySolutionProperties`
  - Added model `SecurityContactsOperations`

### Breaking Changes

  - Deleted or renamed model `SecurityCenter`
  - Method `MdeOnboardingsOperations.list` changed from `asynchronous` to `synchronous`
  - Method `PricingsOperations.list` changed from `asynchronous` to `synchronous`
  - Method `SecurityOperatorsOperations.list` changed from `asynchronous` to `synchronous`
  - Method `SensitivitySettingsOperations.list` changed from `asynchronous` to `synchronous`
  - Method `ServerVulnerabilityAssessmentOperations.list_by_extended_resource` changed from `asynchronous` to `synchronous`
  - Model `AdvancedThreatProtectionSetting` deleted or renamed its instance variable `is_enabled`
  - Model `AlertSyncSettings` deleted or renamed its instance variable `enabled`
  - Model `AutomationUpdateModel` deleted or renamed its instance variable `description`
  - Model `AutomationUpdateModel` deleted or renamed its instance variable `is_enabled`
  - Model `AutomationUpdateModel` deleted or renamed its instance variable `scopes`
  - Model `AutomationUpdateModel` deleted or renamed its instance variable `sources`
  - Model `AutomationUpdateModel` deleted or renamed its instance variable `actions`
  - Model `AzureServersSetting` deleted or renamed its instance variable `selected_provider`
  - Model `DataExportSettings` deleted or renamed its instance variable `enabled`
  - Model `Identity` deleted or renamed its instance variable `principal_id`
  - Model `Identity` deleted or renamed its instance variable `tenant_id`
  - Model `IoTSecuritySolutionModel` deleted or renamed its instance variable `workspace`
  - Model `IoTSecuritySolutionModel` deleted or renamed its instance variable `display_name`
  - Model `IoTSecuritySolutionModel` deleted or renamed its instance variable `status`
  - Model `IoTSecuritySolutionModel` deleted or renamed its instance variable `export`
  - Model `IoTSecuritySolutionModel` deleted or renamed its instance variable `disabled_data_sources`
  - Model `IoTSecuritySolutionModel` deleted or renamed its instance variable `iot_hubs`
  - Model `IoTSecuritySolutionModel` deleted or renamed its instance variable `user_defined_resources`
  - Model `IoTSecuritySolutionModel` deleted or renamed its instance variable `auto_discovered_resources`
  - Model `IoTSecuritySolutionModel` deleted or renamed its instance variable `recommendations_configuration`
  - Model `IoTSecuritySolutionModel` deleted or renamed its instance variable `unmasked_ip_logging_status`
  - Model `IoTSecuritySolutionModel` deleted or renamed its instance variable `additional_workspaces`
  - Model `SecureScoreControlDetails` deleted or renamed its instance variable `display_name`
  - Model `SecureScoreControlDetails` deleted or renamed its instance variable `healthy_resource_count`
  - Model `SecureScoreControlDetails` deleted or renamed its instance variable `unhealthy_resource_count`
  - Model `SecureScoreControlDetails` deleted or renamed its instance variable `not_applicable_resource_count`
  - Model `SecureScoreControlDetails` deleted or renamed its instance variable `weight`
  - Model `SecureScoreControlDetails` deleted or renamed its instance variable `definition`
  - Model `SecureScoreControlDetails` deleted or renamed its instance variable `max`
  - Model `SecureScoreControlDetails` deleted or renamed its instance variable `current`
  - Model `SecureScoreControlDetails` deleted or renamed its instance variable `percentage`
  - Model `SecurityAssessment` deleted or renamed its instance variable `risk`
  - Model `SecurityAssessment` deleted or renamed its instance variable `resource_details`
  - Model `SecurityAssessment` deleted or renamed its instance variable `display_name`
  - Model `SecurityAssessment` deleted or renamed its instance variable `additional_data`
  - Model `SecurityAssessment` deleted or renamed its instance variable `links`
  - Model `SecurityAssessment` deleted or renamed its instance variable `metadata`
  - Model `SecurityAssessment` deleted or renamed its instance variable `partners_data`
  - Model `SecurityAssessment` deleted or renamed its instance variable `status`
  - Model `SecurityAssessmentMetadataResponse` deleted or renamed its instance variable `display_name`
  - Model `SecurityAssessmentMetadataResponse` deleted or renamed its instance variable `policy_definition_id`
  - Model `SecurityAssessmentMetadataResponse` deleted or renamed its instance variable `description`
  - Model `SecurityAssessmentMetadataResponse` deleted or renamed its instance variable `remediation_description`
  - Model `SecurityAssessmentMetadataResponse` deleted or renamed its instance variable `categories`
  - Model `SecurityAssessmentMetadataResponse` deleted or renamed its instance variable `severity`
  - Model `SecurityAssessmentMetadataResponse` deleted or renamed its instance variable `user_impact`
  - Model `SecurityAssessmentMetadataResponse` deleted or renamed its instance variable `implementation_effort`
  - Model `SecurityAssessmentMetadataResponse` deleted or renamed its instance variable `threats`
  - Model `SecurityAssessmentMetadataResponse` deleted or renamed its instance variable `preview`
  - Model `SecurityAssessmentMetadataResponse` deleted or renamed its instance variable `assessment_type`
  - Model `SecurityAssessmentMetadataResponse` deleted or renamed its instance variable `partner_data`
  - Model `SecurityAssessmentMetadataResponse` deleted or renamed its instance variable `publish_dates`
  - Model `SecurityAssessmentMetadataResponse` deleted or renamed its instance variable `planned_deprecation_date`
  - Model `SecurityAssessmentMetadataResponse` deleted or renamed its instance variable `tactics`
  - Model `SecurityAssessmentMetadataResponse` deleted or renamed its instance variable `techniques`
  - Model `SecurityAssessmentResponse` deleted or renamed its instance variable `risk`
  - Model `SecurityAssessmentResponse` deleted or renamed its instance variable `resource_details`
  - Model `SecurityAssessmentResponse` deleted or renamed its instance variable `display_name`
  - Model `SecurityAssessmentResponse` deleted or renamed its instance variable `additional_data`
  - Model `SecurityAssessmentResponse` deleted or renamed its instance variable `links`
  - Model `SecurityAssessmentResponse` deleted or renamed its instance variable `metadata`
  - Model `SecurityAssessmentResponse` deleted or renamed its instance variable `partners_data`
  - Model `SecurityAssessmentResponse` deleted or renamed its instance variable `status`
  - Model `TrackedResource` deleted or renamed its instance variable `etag`
  - Model `TrackedResource` deleted or renamed its instance variable `kind`
  - Model `UpdateIotSecuritySolutionData` deleted or renamed its instance variable `user_defined_resources`
  - Model `UpdateIotSecuritySolutionData` deleted or renamed its instance variable `recommendations_configuration`
  - Deleted or renamed model `AadConnectivityState`
  - Deleted or renamed model `ActiveConnectionsNotInAllowedRange`
  - Deleted or renamed model `AlertList`
  - Deleted or renamed model `AlertsSuppressionRulesList`
  - Deleted or renamed model `AllowedConnectionsList`
  - Deleted or renamed model `AmqpC2DMessagesNotInAllowedRange`
  - Deleted or renamed model `AmqpC2DRejectedMessagesNotInAllowedRange`
  - Deleted or renamed model `AmqpD2CMessagesNotInAllowedRange`
  - Deleted or renamed model `ApiCollectionList`
  - Deleted or renamed model `ApplicationCondition`
  - Deleted or renamed model `ApplicationConditionOperator`
  - Deleted or renamed model `ApplicationsList`
  - Deleted or renamed model `AscLocationList`
  - Deleted or renamed model `AssignedStandardItemAutoGenerated`
  - Deleted or renamed model `AssignmentList`
  - Deleted or renamed model `AutoProvisioningSettingList`
  - Deleted or renamed model `AutomationList`
  - Deleted or renamed model `AzureDevOpsOrganizationConfiguration`
  - Deleted or renamed model `AzureDevOpsProjectConfiguration`
  - Deleted or renamed model `AzureDevOpsProjectListResponse`
  - Deleted or renamed model `AzureDevOpsRepositoryListResponse`
  - Deleted or renamed model `AzureTrackedResourceLocation`
  - Deleted or renamed model `BaseResourceConfiguration`
  - Deleted or renamed model `CloudErrorAutoGenerated`
  - Deleted or renamed model `CloudErrorAutoGenerated10`
  - Deleted or renamed model `CloudErrorAutoGenerated11`
  - Deleted or renamed model `CloudErrorAutoGenerated12`
  - Deleted or renamed model `CloudErrorAutoGenerated13`
  - Deleted or renamed model `CloudErrorAutoGenerated14`
  - Deleted or renamed model `CloudErrorAutoGenerated15`
  - Deleted or renamed model `CloudErrorAutoGenerated16`
  - Deleted or renamed model `CloudErrorAutoGenerated17`
  - Deleted or renamed model `CloudErrorAutoGenerated18`
  - Deleted or renamed model `CloudErrorAutoGenerated19`
  - Deleted or renamed model `CloudErrorAutoGenerated2`
  - Deleted or renamed model `CloudErrorAutoGenerated20`
  - Deleted or renamed model `CloudErrorAutoGenerated3`
  - Deleted or renamed model `CloudErrorAutoGenerated4`
  - Deleted or renamed model `CloudErrorAutoGenerated5`
  - Deleted or renamed model `CloudErrorAutoGenerated6`
  - Deleted or renamed model `CloudErrorAutoGenerated7`
  - Deleted or renamed model `CloudErrorAutoGenerated8`
  - Deleted or renamed model `CloudErrorAutoGenerated9`
  - Deleted or renamed model `CloudErrorBodyAutoGenerated`
  - Deleted or renamed model `CloudErrorBodyAutoGenerated10`
  - Deleted or renamed model `CloudErrorBodyAutoGenerated11`
  - Deleted or renamed model `CloudErrorBodyAutoGenerated12`
  - Deleted or renamed model `CloudErrorBodyAutoGenerated13`
  - Deleted or renamed model `CloudErrorBodyAutoGenerated14`
  - Deleted or renamed model `CloudErrorBodyAutoGenerated15`
  - Deleted or renamed model `CloudErrorBodyAutoGenerated16`
  - Deleted or renamed model `CloudErrorBodyAutoGenerated17`
  - Deleted or renamed model `CloudErrorBodyAutoGenerated18`
  - Deleted or renamed model `CloudErrorBodyAutoGenerated19`
  - Deleted or renamed model `CloudErrorBodyAutoGenerated2`
  - Deleted or renamed model `CloudErrorBodyAutoGenerated20`
  - Deleted or renamed model `CloudErrorBodyAutoGenerated3`
  - Deleted or renamed model `CloudErrorBodyAutoGenerated4`
  - Deleted or renamed model `CloudErrorBodyAutoGenerated5`
  - Deleted or renamed model `CloudErrorBodyAutoGenerated6`
  - Deleted or renamed model `CloudErrorBodyAutoGenerated7`
  - Deleted or renamed model `CloudErrorBodyAutoGenerated8`
  - Deleted or renamed model `CloudErrorBodyAutoGenerated9`
  - Deleted or renamed model `Code`
  - Deleted or renamed model `ComplianceList`
  - Deleted or renamed model `ComplianceResultList`
  - Deleted or renamed model `Components1Uu4J47SchemasSecurityassessmentpropertiesbasePropertiesRiskPropertiesPathsItemsPropertiesEdgesItems`
  - Deleted or renamed model `Condition`
  - Deleted or renamed model `ConnectionFromIpNotAllowed`
  - Deleted or renamed model `ConnectionToIpNotAllowed`
  - Deleted or renamed model `CustomRecommendationsList`
  - Deleted or renamed model `DefenderCspmAwsOfferingCiemDiscovery`
  - Deleted or renamed model `DefenderCspmAwsOfferingCiemOidc`
  - Deleted or renamed model `DefenderForStorageSettingList`
  - Deleted or renamed model `DesiredOnboardingState`
  - Deleted or renamed model `DevOpsConfigurationListResponse`
  - Deleted or renamed model `DeviceSecurityGroupList`
  - Deleted or renamed model `DirectMethodInvokesNotInAllowedRange`
  - Deleted or renamed model `DiscoveredSecuritySolutionList`
  - Deleted or renamed model `ETag`
  - Deleted or renamed model `EdgeIdentifiers`
  - Deleted or renamed model `ErrorAdditionalInfo`
  - Deleted or renamed model `ErrorDetailAutoGenerated`
  - Deleted or renamed model `ErrorDetailAutoGenerated2`
  - Deleted or renamed model `ErrorResponseAutoGenerated`
  - Deleted or renamed model `ErrorResponseAutoGenerated2`
  - Deleted or renamed model `ExternalSecuritySolutionKind`
  - Deleted or renamed model `ExternalSecuritySolutionList`
  - Deleted or renamed model `FailedLocalLoginsNotInAllowedRange`
  - Deleted or renamed model `FileUploadsNotInAllowedRange`
  - Deleted or renamed model `GetSensitivitySettingsListResponse`
  - Deleted or renamed model `GitHubOwnerConfiguration`
  - Deleted or renamed model `GitHubRepositoryListResponse`
  - Deleted or renamed model `GitLabGroupConfiguration`
  - Deleted or renamed model `GitLabProjectListResponse`
  - Deleted or renamed model `GovernanceAssignmentsList`
  - Deleted or renamed model `GovernanceRuleConditionOperator`
  - Deleted or renamed model `GovernanceRuleList`
  - Deleted or renamed model `HealthReportsList`
  - Deleted or renamed model `HttpC2DMessagesNotInAllowedRange`
  - Deleted or renamed model `HttpC2DRejectedMessagesNotInAllowedRange`
  - Deleted or renamed model `HttpD2CMessagesNotInAllowedRange`
  - Deleted or renamed model `InformationProtectionPolicyList`
  - Deleted or renamed model `IoTSecurityAggregatedAlertList`
  - Deleted or renamed model `IoTSecurityAggregatedRecommendationList`
  - Deleted or renamed model `IoTSecuritySolutionsList`
  - Deleted or renamed model `JitNetworkAccessPoliciesList`
  - Deleted or renamed model `Kind`
  - Deleted or renamed model `LocalUserNotAllowed`
  - Deleted or renamed model `Location`
  - Deleted or renamed model `MdeOnboardingDataList`
  - Deleted or renamed model `MqttC2DMessagesNotInAllowedRange`
  - Deleted or renamed model `MqttC2DRejectedMessagesNotInAllowedRange`
  - Deleted or renamed model `MqttD2CMessagesNotInAllowedRange`
  - Deleted or renamed model `NodeIdentifier`
  - Deleted or renamed model `OnPremiseResourceDetails`
  - Deleted or renamed model `OnPremiseSqlResourceDetails`
  - Deleted or renamed model `OperationResult`
  - Deleted or renamed model `OperationStatusAutoGenerated`
  - Deleted or renamed model `OperationStatusResultAutoGenerated`
  - Deleted or renamed model `Path`
  - Deleted or renamed model `PricingList`
  - Deleted or renamed model `PrivateLinkParameters`
  - Deleted or renamed model `PrivateLinkResourceAutoGenerated`
  - Deleted or renamed model `PrivateLinksList`
  - Deleted or renamed model `ProcessNotAllowed`
  - Deleted or renamed model `QueuePurgesNotInAllowedRange`
  - Deleted or renamed model `RegulatoryComplianceAssessmentList`
  - Deleted or renamed model `RegulatoryComplianceControlList`
  - Deleted or renamed model `RegulatoryComplianceStandardList`
  - Deleted or renamed model `ResourceAutoGenerated`
  - Deleted or renamed model `ResourceAutoGenerated2`
  - Deleted or renamed model `ResourceAutoGenerated3`
  - Deleted or renamed model `ResourceDetailsAutoGenerated`
  - Deleted or renamed model `ScanResults`
  - Deleted or renamed model `ScansV2`
  - Deleted or renamed model `SecureScoreControlDefinitionList`
  - Deleted or renamed model `SecureScoreControlList`
  - Deleted or renamed model `SecureScoreControlScore`
  - Deleted or renamed model `SecureScoresList`
  - Deleted or renamed model `SecurityAssessmentList`
  - Deleted or renamed model `SecurityAssessmentMetadata`
  - Deleted or renamed model `SecurityAssessmentMetadataResponseList`
  - Deleted or renamed model `SecurityAssessmentPropertiesBaseRiskPathsPropertiesItemsItem`
  - Deleted or renamed model `SecurityConnectorsList`
  - Deleted or renamed model `SecurityOperatorList`
  - Deleted or renamed model `SecuritySolutionList`
  - Deleted or renamed model `SecurityStandardList`
  - Deleted or renamed model `SecuritySubAssessmentList`
  - Deleted or renamed model `SecurityTaskList`
  - Deleted or renamed model `ServerVulnerabilityAssessmentsList`
  - Deleted or renamed model `ServerVulnerabilityAssessmentsSettingsList`
  - Deleted or renamed model `SettingNameAutoGenerated`
  - Deleted or renamed model `SettingsList`
  - Deleted or renamed model `StandardAssignmentsList`
  - Deleted or renamed model `StandardList`
  - Deleted or renamed model `Status`
  - Deleted or renamed model `TopologyList`
  - Deleted or renamed model `TrackedResourceAutoGenerated`
  - Deleted or renamed model `TwinUpdatesNotInAllowedRange`
  - Deleted or renamed model `UnauthorizedOperationsNotInAllowedRange`
  - Deleted or renamed model `WorkspaceSettingList`
  - Method `AlertsSuppressionRulesOperations.list` changed its parameter `alert_type` from `positional_or_keyword` to `keyword_only`
  - Method `AssessmentsOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PrivateEndpointConnectionsOperations.begin_create_or_update` inserted a `positional_or_keyword` parameter `private_link_name`
  - Method `PrivateEndpointConnectionsOperations.begin_create_or_update` deleted or renamed its parameter `private_link_parameters` of kind `positional_or_keyword`
  - Method `PrivateEndpointConnectionsOperations.begin_delete` inserted a `positional_or_keyword` parameter `private_link_name`
  - Method `PrivateEndpointConnectionsOperations.begin_delete` deleted or renamed its parameter `private_link_parameters` of kind `positional_or_keyword`
  - Method `PrivateEndpointConnectionsOperations.get` inserted a `positional_or_keyword` parameter `private_link_name`
  - Method `PrivateEndpointConnectionsOperations.get` deleted or renamed its parameter `private_link_parameters` of kind `positional_or_keyword`
  - Method `PrivateEndpointConnectionsOperations.list` inserted a `positional_or_keyword` parameter `private_link_name`
  - Method `PrivateEndpointConnectionsOperations.list` deleted or renamed its parameter `private_link_parameters` of kind `positional_or_keyword`
  - Method `PrivateLinkResourcesOperations.get` inserted a `positional_or_keyword` parameter `private_link_name`
  - Method `PrivateLinkResourcesOperations.get` deleted or renamed its parameter `private_link_parameters` of kind `positional_or_keyword`
  - Method `PrivateLinkResourcesOperations.list` inserted a `positional_or_keyword` parameter `private_link_name`
  - Method `PrivateLinkResourcesOperations.list` deleted or renamed its parameter `private_link_parameters` of kind `positional_or_keyword`
  - Method `PrivateLinksOperations.begin_create` inserted a `positional_or_keyword` parameter `private_link_name`
  - Method `PrivateLinksOperations.begin_create` deleted or renamed its parameter `private_link_parameters` of kind `positional_or_keyword`
  - Method `PrivateLinksOperations.begin_delete` inserted a `positional_or_keyword` parameter `private_link_name`
  - Method `PrivateLinksOperations.begin_delete` deleted or renamed its parameter `private_link_parameters` of kind `positional_or_keyword`
  - Method `PrivateLinksOperations.get` deleted or renamed its parameter `private_link_parameters` of kind `positional_or_keyword`
  - Method `PrivateLinksOperations.head` inserted a `positional_or_keyword` parameter `private_link_name`
  - Method `PrivateLinksOperations.head` deleted or renamed its parameter `private_link_parameters` of kind `positional_or_keyword`
  - Method `PrivateLinksOperations.update` inserted a `positional_or_keyword` parameter `private_link_name`
  - Method `PrivateLinksOperations.update` deleted or renamed its parameter `private_link_parameters` of kind `positional_or_keyword`
  - Method `SecureScoreControlsOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `SecureScoreControlsOperations.list_by_secure_score` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `SqlVulnerabilityAssessmentBaselineRulesOperations.add` changed its parameter `database_name` from `positional_or_keyword` to `keyword_only`
  - Method `SqlVulnerabilityAssessmentBaselineRulesOperations.create_or_update` changed its parameter `database_name` from `positional_or_keyword` to `keyword_only`
  - Method `SqlVulnerabilityAssessmentBaselineRulesOperations.delete` changed its parameter `database_name` from `positional_or_keyword` to `keyword_only`
  - Method `SqlVulnerabilityAssessmentBaselineRulesOperations.get` changed its parameter `database_name` from `positional_or_keyword` to `keyword_only`
  - Method `SqlVulnerabilityAssessmentBaselineRulesOperations.list` changed its parameter `database_name` from `positional_or_keyword` to `keyword_only`
  - Method `SqlVulnerabilityAssessmentScanResultsOperations.get` changed its parameter `database_name` from `positional_or_keyword` to `keyword_only`
  - Method `SqlVulnerabilityAssessmentScanResultsOperations.list` changed its parameter `database_name` from `positional_or_keyword` to `keyword_only`
  - Method `SqlVulnerabilityAssessmentScansOperations.begin_initiate_scan` changed its parameter `database_name` from `positional_or_keyword` to `keyword_only`
  - Method `SqlVulnerabilityAssessmentScansOperations.get` changed its parameter `database_name` from `positional_or_keyword` to `keyword_only`
  - Method `SqlVulnerabilityAssessmentScansOperations.get_scan_operation_result` changed its parameter `database_name` from `positional_or_keyword` to `keyword_only`
  - Method `SqlVulnerabilityAssessmentScansOperations.list` changed its parameter `database_name` from `positional_or_keyword` to `keyword_only`
  - Method `PrivateLinksOperations.begin_create` re-ordered its parameters from `['self', 'resource_group_name', 'private_link_parameters', 'private_link', 'kwargs']` to `['self', 'resource_group_name', 'private_link_name', 'private_link', 'kwargs']`
  - Method `PrivateLinksOperations.update` re-ordered its parameters from `['self', 'resource_group_name', 'private_link_parameters', 'private_link', 'kwargs']` to `['self', 'resource_group_name', 'private_link_name', 'private_link', 'kwargs']`
  - Method `PrivateLinksOperations.head` re-ordered its parameters from `['self', 'resource_group_name', 'private_link_parameters', 'kwargs']` to `['self', 'resource_group_name', 'private_link_name', 'kwargs']`
  - Method `PrivateLinksOperations.begin_delete` re-ordered its parameters from `['self', 'resource_group_name', 'private_link_parameters', 'kwargs']` to `['self', 'resource_group_name', 'private_link_name', 'kwargs']`
  - Method `PrivateLinkResourcesOperations.list` re-ordered its parameters from `['self', 'resource_group_name', 'private_link_parameters', 'kwargs']` to `['self', 'resource_group_name', 'private_link_name', 'kwargs']`
  - Method `PrivateLinkResourcesOperations.get` re-ordered its parameters from `['self', 'resource_group_name', 'group_id', 'private_link_parameters', 'kwargs']` to `['self', 'resource_group_name', 'private_link_name', 'group_id', 'kwargs']`
  - Method `PrivateEndpointConnectionsOperations.list` re-ordered its parameters from `['self', 'resource_group_name', 'private_link_parameters', 'kwargs']` to `['self', 'resource_group_name', 'private_link_name', 'kwargs']`
  - Method `PrivateEndpointConnectionsOperations.begin_delete` re-ordered its parameters from `['self', 'resource_group_name', 'private_endpoint_connection_name', 'private_link_parameters', 'kwargs']` to `['self', 'resource_group_name', 'private_link_name', 'private_endpoint_connection_name', 'kwargs']`
  - Method `PrivateEndpointConnectionsOperations.begin_create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'private_endpoint_connection_name', 'private_link_parameters', 'private_endpoint_connection', 'kwargs']` to `['self', 'resource_group_name', 'private_link_name', 'private_endpoint_connection_name', 'private_endpoint_connection', 'kwargs']`
  - Method `PrivateEndpointConnectionsOperations.get` re-ordered its parameters from `['self', 'resource_group_name', 'private_endpoint_connection_name', 'private_link_parameters', 'kwargs']` to `['self', 'resource_group_name', 'private_link_name', 'private_endpoint_connection_name', 'kwargs']`
  - Method `SqlVulnerabilityAssessmentBaselineRulesOperations.create_or_update` re-ordered its parameters from `['self', 'resource_id', 'rule_id', 'database_name', 'body', 'kwargs']` to `['self', 'resource_id', 'rule_id', 'body', 'database_name', 'kwargs']`
  - Method `SqlVulnerabilityAssessmentBaselineRulesOperations.add` re-ordered its parameters from `['self', 'resource_id', 'database_name', 'body', 'kwargs']` to `['self', 'resource_id', 'body', 'database_name', 'kwargs']`

## 8.0.0b1 (2025-08-25)

### Breaking Changes

- This package now only targets the latest Api-Version available on Azure and removes APIs of other Api-Version. After this change, the package can have much smaller size. If your application requires a specific and non-latest Api-Version, it's recommended to pin this package to the previous released version; If your application always only use latest Api-Version, please ignore this change.

## 7.0.0 (2024-05-20)

### Features Added

  - Added operation HealthReportsOperations.get
  - Added operation PricingsOperations.delete
  - Added operation group AzureDevOpsOrgsOperations
  - Added operation group AzureDevOpsProjectsOperations
  - Added operation group AzureDevOpsReposOperations
  - Added operation group DevOpsConfigurationsOperations
  - Added operation group DevOpsOperationResultsOperations
  - Added operation group GitHubOwnersOperations
  - Added operation group GitHubReposOperations
  - Added operation group GitLabGroupsOperations
  - Added operation group GitLabProjectsOperations
  - Added operation group GitLabSubgroupsOperations
  - Added operation group SensitivitySettingsOperations
  - Added operation group ServerVulnerabilityAssessmentsSettingsOperations
  - Model AwsEnvironmentData has a new parameter scan_interval
  - Model DefenderCspmAwsOffering has a new parameter ciem
  - Model DefenderCspmAwsOffering has a new parameter mdc_containers_agentless_discovery_k8_s
  - Model DefenderCspmAwsOffering has a new parameter mdc_containers_image_assessment
  - Model DefenderCspmGcpOffering has a new parameter ciem_discovery
  - Model DefenderCspmGcpOffering has a new parameter data_sensitivity_discovery
  - Model DefenderCspmGcpOffering has a new parameter mdc_containers_agentless_discovery_k8_s
  - Model DefenderCspmGcpOffering has a new parameter mdc_containers_image_assessment
  - Model DefenderCspmGcpOffering has a new parameter vm_scanners
  - Model DefenderForContainersAwsOffering has a new parameter mdc_containers_agentless_discovery_k8_s
  - Model DefenderForContainersAwsOffering has a new parameter mdc_containers_image_assessment
  - Model DefenderForContainersGcpOffering has a new parameter mdc_containers_agentless_discovery_k8_s
  - Model DefenderForContainersGcpOffering has a new parameter mdc_containers_image_assessment
  - Model GcpProjectEnvironmentData has a new parameter scan_interval
  - Model HealthReport has a new parameter affected_defenders_sub_plans
  - Model HealthReport has a new parameter report_additional_data
  - Model Pricing has a new parameter enforce
  - Model Pricing has a new parameter inherited
  - Model Pricing has a new parameter inherited_from
  - Model Pricing has a new parameter resources_coverage_status
  - Model Status has a new parameter last_scanned_date
  - Model Status has a new parameter reason
  - Operation PricingsOperations.list has a new optional parameter filter

### Breaking Changes

  - Operation PricingsOperations.get has a new required parameter scope_id
  - Operation PricingsOperations.list has a new required parameter scope_id
  - Operation PricingsOperations.update has a new required parameter scope_id
  - Removed operation group IngestionSettingsOperations

## 6.0.0 (2024-01-19)

### Features Added

  - Added operation group APICollectionsOperations
  - Added operation group DefenderForStorageOperations
  - Model SecurityContact has a new parameter emails
  - Model SecurityContact has a new parameter notifications_by_role

### Breaking Changes

  - Model SecurityContact no longer has parameter alerts_to_admins
  - Model SecurityContact no longer has parameter email
  - Removed operation SecurityContactsOperations.update

## 5.0.0 (2023-04-20)

### Features Added

  - Added operation group APICollectionOffboardingOperations
  - Added operation group APICollectionOnboardingOperations
  - Added operation group APICollectionOperations
  - Added operation group SecurityOperatorsOperations
  - Model AwsEnvironmentData has a new parameter account_name
  - Model AwsEnvironmentData has a new parameter regions
  - Model DefenderCspmAwsOffering has a new parameter data_sensitivity_discovery
  - Model DefenderCspmAwsOffering has a new parameter databases_dspm
  - Model DefenderFoDatabasesAwsOffering has a new parameter databases_dspm
  - Model DefenderFoDatabasesAwsOfferingArcAutoProvisioning has a new parameter configuration
  - Model DefenderForDatabasesGcpOfferingArcAutoProvisioning has a new parameter configuration
  - Model DefenderForDatabasesGcpOfferingArcAutoProvisioningConfiguration has a new parameter private_link_scope
  - Model DefenderForDatabasesGcpOfferingArcAutoProvisioningConfiguration has a new parameter proxy
  - Model DefenderForServersAwsOfferingArcAutoProvisioning has a new parameter configuration
  - Model DefenderForServersGcpOffering has a new parameter vm_scanners
  - Model DefenderForServersGcpOfferingArcAutoProvisioning has a new parameter configuration
  - Model DefenderForServersGcpOfferingArcAutoProvisioningConfiguration has a new parameter private_link_scope
  - Model DefenderForServersGcpOfferingArcAutoProvisioningConfiguration has a new parameter proxy
  - Model GcpOrganizationalDataOrganization has a new parameter organization_name
  - Model GcpProjectDetails has a new parameter project_name
  - Model Pricing has a new parameter enablement_time
  - Model Pricing has a new parameter extensions

### Breaking Changes

  - Model DefenderForDatabasesGcpOfferingArcAutoProvisioningConfiguration no longer has parameter agent_onboarding_service_account_numeric_id
  - Model DefenderForDatabasesGcpOfferingArcAutoProvisioningConfiguration no longer has parameter client_id
  - Model DefenderForServersGcpOfferingArcAutoProvisioningConfiguration no longer has parameter agent_onboarding_service_account_numeric_id
  - Model DefenderForServersGcpOfferingArcAutoProvisioningConfiguration no longer has parameter client_id

## 4.0.0 (2023-03-20)

### Features Added

  - Added operation GovernanceRulesOperations.begin_execute
  - Added operation GovernanceRulesOperations.list
  - Added operation GovernanceRulesOperations.operation_results
  - Added operation group HealthReportOperations
  - Added operation group HealthReportsOperations
  - Model GovernanceRule has a new parameter excluded_scopes
  - Model GovernanceRule has a new parameter include_member_scopes
  - Model GovernanceRule has a new parameter metadata
  - Model GovernanceRule has a new parameter tenant_id
  - Model ResourceDetails has a new parameter connector_id
  - Model ResourceDetails has a new parameter id
  - Model ScanProperties has a new parameter last_scan_time

### Breaking Changes

  - Operation GovernanceRulesOperations.create_or_update has a new required parameter scope
  - Operation GovernanceRulesOperations.get has a new required parameter scope
  - Removed operation GovernanceRulesOperations.begin_rule_id_execute_single_security_connector
  - Removed operation GovernanceRulesOperations.begin_rule_id_execute_single_subscription
  - Removed operation group GovernanceRuleOperations
  - Removed operation group SecurityConnectorGovernanceRuleOperations
  - Removed operation group SecurityConnectorGovernanceRulesExecuteStatusOperations
  - Removed operation group SecurityConnectorGovernanceRulesOperations
  - Removed operation group SubscriptionGovernanceRulesExecuteStatusOperations
  - Renamed operation GovernanceRulesOperations.delete to GovernanceRulesOperations.begin_delete

## 4.0.0b2 (2023-03-06)

### Features Added

  - Added operation GovernanceRulesOperations.begin_execute
  - Added operation GovernanceRulesOperations.list
  - Added operation GovernanceRulesOperations.operation_results
  - Model GovernanceRule has a new parameter excluded_scopes
  - Model GovernanceRule has a new parameter include_member_scopes
  - Model GovernanceRule has a new parameter metadata
  - Model GovernanceRule has a new parameter tenant_id

### Breaking Changes

  - Operation GovernanceRulesOperations.create_or_update has a new required parameter scope
  - Operation GovernanceRulesOperations.get has a new required parameter scope
  - Removed operation GovernanceRulesOperations.begin_rule_id_execute_single_security_connector
  - Removed operation GovernanceRulesOperations.begin_rule_id_execute_single_subscription
  - Removed operation group GovernanceRuleOperations
  - Removed operation group SecurityConnectorGovernanceRuleOperations
  - Removed operation group SecurityConnectorGovernanceRulesExecuteStatusOperations
  - Removed operation group SecurityConnectorGovernanceRulesOperations
  - Removed operation group SubscriptionGovernanceRulesExecuteStatusOperations
  - Renamed operation GovernanceRulesOperations.delete to GovernanceRulesOperations.begin_delete

## 4.0.0b1 (2023-02-16)

### Features Added

  - Added operation GovernanceRulesOperations.begin_execute
  - Added operation GovernanceRulesOperations.list
  - Added operation GovernanceRulesOperations.operation_results
  - Model GovernanceRule has a new parameter excluded_scopes
  - Model GovernanceRule has a new parameter include_member_scopes
  - Model GovernanceRule has a new parameter metadata
  - Model GovernanceRule has a new parameter tenant_id

### Breaking Changes

  - Operation GovernanceRulesOperations.create_or_update has a new required parameter scope
  - Operation GovernanceRulesOperations.get has a new required parameter scope
  - Removed operation GovernanceRulesOperations.begin_rule_id_execute_single_security_connector
  - Removed operation GovernanceRulesOperations.begin_rule_id_execute_single_subscription
  - Removed operation group GovernanceRuleOperations
  - Removed operation group SecurityConnectorGovernanceRuleOperations
  - Removed operation group SecurityConnectorGovernanceRulesExecuteStatusOperations
  - Removed operation group SecurityConnectorGovernanceRulesOperations
  - Removed operation group SubscriptionGovernanceRulesExecuteStatusOperations
  - Renamed operation GovernanceRulesOperations.delete to GovernanceRulesOperations.begin_delete

## 3.0.0 (2022-11-17)

### Features Added

  - Model DefenderFoDatabasesAwsOffering has a new parameter rds

### Breaking Changes

  - Model DefenderFoDatabasesAwsOfferingArcAutoProvisioning no longer has parameter service_principal_secret_metadata
  - Model DefenderForDatabasesGcpOfferingArcAutoProvisioning no longer has parameter configuration
  - Model DefenderForServersAwsOfferingArcAutoProvisioning no longer has parameter service_principal_secret_metadata
  - Model DefenderForServersGcpOfferingArcAutoProvisioning no longer has parameter configuration

## 2.0.0 (2022-09-28)

### Features Added

  - Added operation AlertsOperations.begin_simulate
  - Added operation AlertsOperations.get_resource_group_level
  - Added operation AlertsOperations.get_subscription_level
  - Added operation AlertsOperations.list_resource_group_level_by_region
  - Added operation AlertsOperations.list_subscription_level_by_region
  - Added operation AlertsOperations.update_resource_group_level_state_to_activate
  - Added operation AlertsOperations.update_resource_group_level_state_to_dismiss
  - Added operation AlertsOperations.update_resource_group_level_state_to_in_progress
  - Added operation AlertsOperations.update_subscription_level_state_to_activate
  - Added operation AlertsOperations.update_subscription_level_state_to_dismiss
  - Added operation AlertsOperations.update_subscription_level_state_to_in_progress
  - Added operation group ApplicationOperations
  - Added operation group ApplicationsOperations
  - Added operation group CustomAssessmentAutomationsOperations
  - Added operation group CustomEntityStoreAssignmentsOperations
  - Added operation group GovernanceAssignmentsOperations
  - Added operation group GovernanceRuleOperations
  - Added operation group GovernanceRulesOperations
  - Added operation group IngestionSettingsOperations
  - Added operation group MdeOnboardingsOperations
  - Added operation group SecurityConnectorApplicationOperations
  - Added operation group SecurityConnectorApplicationsOperations
  - Added operation group SecurityConnectorGovernanceRuleOperations
  - Added operation group SecurityConnectorGovernanceRulesExecuteStatusOperations
  - Added operation group SecurityConnectorGovernanceRulesOperations
  - Added operation group SecurityConnectorsOperations
  - Added operation group SoftwareInventoriesOperations
  - Added operation group SubscriptionGovernanceRulesExecuteStatusOperations
  - Model Alert has a new parameter sub_techniques
  - Model Alert has a new parameter supporting_evidence
  - Model Alert has a new parameter techniques
  - Model Alert has a new parameter version
  - Model IoTSecuritySolutionModel has a new parameter additional_workspaces
  - Model IoTSecuritySolutionModel has a new parameter system_data
  - Model Pricing has a new parameter deprecated
  - Model Pricing has a new parameter replaced_by
  - Model Pricing has a new parameter sub_plan
  - Model SecurityAssessmentMetadata has a new parameter categories
  - Model SecurityAssessmentMetadataProperties has a new parameter categories

### Breaking Changes

  - Model SecurityAssessmentMetadata no longer has parameter category
  - Model SecurityAssessmentMetadataProperties no longer has parameter category
  - Operation AdaptiveApplicationControlsOperations.delete has a new parameter asc_location
  - Operation AdaptiveApplicationControlsOperations.get has a new parameter asc_location
  - Operation AdaptiveApplicationControlsOperations.put has a new parameter asc_location
  - Operation AlertsOperations.update_resource_group_level_state_to_resolve has a new parameter asc_location
  - Operation AlertsOperations.update_subscription_level_state_to_resolve has a new parameter asc_location
  - Operation AllowedConnectionsOperations.get has a new parameter asc_location
  - Operation AllowedConnectionsOperations.list_by_home_region has a new parameter asc_location
  - Operation DiscoveredSecuritySolutionsOperations.get has a new parameter asc_location
  - Operation DiscoveredSecuritySolutionsOperations.list_by_home_region has a new parameter asc_location
  - Operation ExternalSecuritySolutionsOperations.get has a new parameter asc_location
  - Operation ExternalSecuritySolutionsOperations.list_by_home_region has a new parameter asc_location
  - Operation JitNetworkAccessPoliciesOperations.create_or_update has a new parameter asc_location
  - Operation JitNetworkAccessPoliciesOperations.delete has a new parameter asc_location
  - Operation JitNetworkAccessPoliciesOperations.get has a new parameter asc_location
  - Operation JitNetworkAccessPoliciesOperations.initiate has a new parameter asc_location
  - Operation JitNetworkAccessPoliciesOperations.list_by_region has a new parameter asc_location
  - Operation JitNetworkAccessPoliciesOperations.list_by_resource_group_and_region has a new parameter asc_location
  - Operation LocationsOperations.get has a new parameter asc_location
  - Operation SecuritySolutionsOperations.get has a new parameter asc_location
  - Operation SecuritySolutionsReferenceDataOperations.list_by_home_region has a new parameter asc_location
  - Operation TasksOperations.get_resource_group_level_task has a new parameter asc_location
  - Operation TasksOperations.get_subscription_level_task has a new parameter asc_location
  - Operation TasksOperations.list_by_home_region has a new parameter asc_location
  - Operation TasksOperations.list_by_resource_group has a new parameter asc_location
  - Operation TasksOperations.update_resource_group_level_task_state has a new parameter asc_location
  - Operation TasksOperations.update_subscription_level_task_state has a new parameter asc_location
  - Operation TopologyOperations.get has a new parameter asc_location
  - Operation TopologyOperations.list_by_home_region has a new parameter asc_location
  - Removed operation AlertsOperations.get_resource_group_level_alerts
  - Removed operation AlertsOperations.get_subscription_level_alert
  - Removed operation AlertsOperations.list_resource_group_level_alerts_by_region
  - Removed operation AlertsOperations.list_subscription_level_alerts_by_region
  - Removed operation AlertsOperations.update_resource_group_level_alert_state_to_dismiss
  - Removed operation AlertsOperations.update_resource_group_level_alert_state_to_reactivate
  - Removed operation AlertsOperations.update_subscription_level_alert_state_to_dismiss
  - Removed operation AlertsOperations.update_subscription_level_alert_state_to_reactivate
  - Removed operation group DeviceOperations
  - Removed operation group DevicesForHubOperations
  - Removed operation group DevicesForSubscriptionOperations
  - Removed operation group IotAlertTypesOperations
  - Removed operation group IotAlertsOperations
  - Removed operation group IotDefenderSettingsOperations
  - Removed operation group IotRecommendationTypesOperations
  - Removed operation group IotRecommendationsOperations
  - Removed operation group IotSensorsOperations
  - Removed operation group IotSitesOperations
  - Removed operation group OnPremiseIotSensorsOperations
  - Renamed operation ServerVulnerabilityAssessmentOperations.delete to ServerVulnerabilityAssessmentOperations.begin_delete

## 2.0.0b1 (2021-08-10)

**Features**

  - Model SecurityAssessmentMetadata has a new parameter categories
  - Model SecurityAssessmentMetadataProperties has a new parameter categories
  - Model IoTSecuritySolutionModel has a new parameter system_data
  - Model IoTSecuritySolutionModel has a new parameter additional_workspaces
  - Added operation ServerVulnerabilityAssessmentOperations.begin_delete
  - Added operation AlertsOperations.list_resource_group_level_by_region
  - Added operation AlertsOperations.get_resource_group_level
  - Added operation AlertsOperations.update_subscription_level_state_to_dismiss
  - Added operation AlertsOperations.update_resource_group_level_state_to_dismiss
  - Added operation AlertsOperations.update_resource_group_level_state_to_activate
  - Added operation AlertsOperations.get_subscription_level
  - Added operation AlertsOperations.update_subscription_level_state_to_activate
  - Added operation AlertsOperations.list_subscription_level_by_region
  - Added operation AlertsOperations.begin_simulate
  - Added operation group IngestionSettingsOperations
  - Added operation group SoftwareInventoriesOperations

**Breaking changes**

  - Model SecurityAssessmentMetadata no longer has parameter category
  - Model SecurityAssessmentMetadataProperties no longer has parameter category
  - Removed operation ServerVulnerabilityAssessmentOperations.delete
  - Removed operation AlertsOperations.update_resource_group_level_alert_state_to_reactivate
  - Removed operation AlertsOperations.get_resource_group_level_alerts
  - Removed operation AlertsOperations.update_subscription_level_alert_state_to_dismiss
  - Removed operation AlertsOperations.get_subscription_level_alert
  - Removed operation AlertsOperations.update_resource_group_level_alert_state_to_dismiss
  - Removed operation AlertsOperations.list_subscription_level_alerts_by_region
  - Removed operation AlertsOperations.update_subscription_level_alert_state_to_reactivate
  - Removed operation AlertsOperations.list_resource_group_level_alerts_by_region
  - Removed operation group OnPremiseIotSensorsOperations
  - Removed operation group IotRecommendationsOperations
  - Removed operation group IotSensorsOperations
  - Removed operation group DeviceOperations
  - Removed operation group IotRecommendationTypesOperations
  - Removed operation group DevicesForHubOperations
  - Removed operation group IotDefenderSettingsOperations
  - Removed operation group DevicesForSubscriptionOperations
  - Removed operation group IotSitesOperations
  - Removed operation group IotAlertTypesOperations
  - Removed operation group IotAlertsOperations

## 1.0.0 (2020-12-15)

**Bugfixes**

  - Fix unreasonable boolean enumeration type

## 1.0.0b1 (2020-11-02)

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

## 0.5.0 (2020-10-29)

**Features**

  - Model SecureScoreControlDetails has a new parameter weight
  - Model SecureScoreControlDetails has a new parameter percentage
  - Model SecureScoreItem has a new parameter weight
  - Model SecureScoreItem has a new parameter percentage
  - Model SecureScoreControlScore has a new parameter percentage
  - Added operation AlertsOperations.get_resource_group_level
  - Added operation AlertsOperations.get_subscription_level
  - Added operation AlertsOperations.update_resource_group_level_state_to_resolve
  - Added operation AlertsOperations.list_subscription_level_by_region
  - Added operation AlertsOperations.list_resource_group_level_by_region
  - Added operation AlertsOperations.update_subscription_level_state_to_resolve
  - Added operation AlertsOperations.update_subscription_level_state_to_dismiss
  - Added operation AlertsOperations.update_resource_group_level_state_to_dismiss
  - Added operation AlertsOperations.update_subscription_level_state_to_activate
  - Added operation AlertsOperations.update_resource_group_level_state_to_activate
  - Added operation group IotRecommendationTypesOperations
  - Added operation group ConnectorsOperations
  - Added operation group DeviceOperations
  - Added operation group DevicesForSubscriptionOperations
  - Added operation group IotDefenderSettingsOperations
  - Added operation group IotAlertsOperations
  - Added operation group DevicesForHubOperations
  - Added operation group IotSensorsOperations
  - Added operation group IotRecommendationsOperations
  - Added operation group SecuritySolutionsOperations
  - Added operation group SecuritySolutionsReferenceDataOperations
  - Added operation group OnPremiseIotSensorsOperations
  - Added operation group IotAlertTypesOperations

**Breaking changes**

  - Model Alert has a new signature
  - Removed operation AlertsOperations.list_subscription_level_alerts_by_region
  - Removed operation AlertsOperations.update_resource_group_level_alert_state_to_dismiss
  - Removed operation AlertsOperations.get_resource_group_level_alerts
  - Removed operation AlertsOperations.update_subscription_level_alert_state_to_reactivate
  - Removed operation AlertsOperations.get_subscription_level_alert
  - Removed operation AlertsOperations.list_resource_group_level_alerts_by_region
  - Removed operation AlertsOperations.update_resource_group_level_alert_state_to_reactivate
  - Removed operation AlertsOperations.update_subscription_level_alert_state_to_dismiss

## 0.4.1 (2020-06-12)

**Bugfixes**

  - skip url-encoding for resource id

## 0.4.0 (2020-06-05)

**Features**

  - Model IoTSecuritySolutionModel has a new parameter unmasked_ip_logging_status
  - Model InformationProtectionPolicy has a new parameter version
  - Model JitNetworkAccessRequest has a new parameter justification
  - Model SensitivityLabel has a new parameter description
  - Model SensitivityLabel has a new parameter rank
  - Model InformationType has a new parameter description
  - Model AppWhitelistingGroup has a new parameter protection_mode
  - Model JitNetworkAccessPolicyInitiateRequest has a new parameter justification
  - Model VmRecommendation has a new parameter enforcement_support
  - Model IoTSecurityAggregatedAlert has a new parameter top_devices_list
  - Added operation AdaptiveApplicationControlsOperations.delete
  - Added operation AlertsOperations.update_resource_group_level_alert_state_to_dismiss
  - Added operation AlertsOperations.update_subscription_level_alert_state_to_dismiss
  - Added operation AlertsOperations.update_subscription_level_alert_state_to_reactivate
  - Added operation AlertsOperations.update_resource_group_level_alert_state_to_reactivate
  - Added operation IotSecuritySolutionOperations.list_by_subscription
  - Added operation IotSecuritySolutionOperations.list_by_resource_group
  - Added operation IotSecuritySolutionOperations.create_or_update
  - Added operation group SecureScoreControlDefinitionsOperations
  - Added operation group AssessmentsMetadataOperations
  - Added operation group SecureScoreControlsOperations
  - Added operation group AlertsSuppressionRulesOperations
  - Added operation group IotSecuritySolutionsAnalyticsAggregatedAlertOperations
  - Added operation group SubAssessmentsOperations
  - Added operation group AutomationsOperations
  - Added operation group IotSecuritySolutionsAnalyticsRecommendationOperations
  - Added operation group SecureScoresOperations
  - Added operation group IotSecuritySolutionAnalyticsOperations
  - Added operation group AdaptiveNetworkHardeningsOperations
  - Added operation group AssessmentsOperations
  - Added operation group DeviceSecurityGroupsOperations

**Breaking changes**

  - Operation SettingsOperations.update has a new signature
  - Operation AlertsOperations.list has a new signature
  - Operation AlertsOperations.list_by_resource_group has a new signature
  - Operation AlertsOperations.list_resource_group_level_alerts_by_region has a new signature
  - Operation AlertsOperations.list_subscription_level_alerts_by_region has a new signature
  - Operation JitNetworkAccessPoliciesOperations.initiate has a new signature
  - Operation InformationProtectionPoliciesOperations.create_or_update has a new signature
  - Removed operation AlertsOperations.update_resource_group_level_alert_state
  - Removed operation AlertsOperations.update_subscription_level_alert_state
  - Removed operation IotSecuritySolutionOperations.create
  - Removed operation group IoTSecuritySolutionsResourceGroupOperations
  - Removed operation group IoTSecuritySolutionsAnalyticsRecommendationsOperations
  - Removed operation group IoTSecuritySolutionsAnalyticsRecommendationOperations
  - Removed operation group IoTSecuritySolutionsOperations
  - Removed operation group IoTSecuritySolutionsAnalyticsAggregatedAlertsOperations
  - Removed operation group IoTSecuritySolutionsAnalyticsAggregatedAlertOperations
  - Removed operation group IoTSecuritySolutionsAnalyticsOperations

## 0.3.0 (2019-08-01)

**Features**

  - Model JitNetworkAccessPolicyVirtualMachine has a new parameter
    public_ip_address
  - Model JitNetworkAccessRequestPort has a new parameter mapped_port
  - Added operation group RegulatoryComplianceControlsOperations
  - Added operation group ComplianceResultsOperations
  - Added operation group ServerVulnerabilityAssessmentOperations
  - Added operation group IoTSecuritySolutionsResourceGroupOperations
  - Added operation group AdaptiveApplicationControlsOperations
  - Added operation group IoTSecuritySolutionsOperations
  - Added operation group IotSecuritySolutionOperations
  - Added operation group RegulatoryComplianceStandardsOperations
  - Added operation group IoTSecuritySolutionsAnalyticsOperations
  - Added operation group
    IoTSecuritySolutionsAnalyticsAggregatedAlertOperations
  - Added operation group
    IoTSecuritySolutionsAnalyticsRecommendationsOperations
  - Added operation group RegulatoryComplianceAssessmentsOperations
  - Added operation group
    IoTSecuritySolutionsAnalyticsRecommendationOperations
  - Added operation group
    IoTSecuritySolutionsAnalyticsAggregatedAlertsOperations

**General breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if from some import. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - SecurityCenter cannot be imported from
    `azure.mgmt.security.security_center` anymore (import from
    `azure.mgmt.security` works like before)
  - SecurityCenterConfiguration import has been moved from
    `azure.mgmt.security.security_center` to `azure.mgmt.security`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.security.models.my_class` (import from
    `azure.mgmt.security.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.security.operations.my_class_operations` (import
    from `azure.mgmt.security.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.2.0 (2019-04-16)

**Features**

  - Model Pricing has a new parameter free_trial_remaining_time
  - Model Alert has a new parameter is_incident
  - Added operation PricingsOperations.get
  - Added operation PricingsOperations.update
  - Added operation group AllowedConnectionsOperations

**Breaking changes**

  - Operation SettingsOperations.update has a new signature
  - Removed operation PricingsOperations.update_subscription_pricing
  - Removed operation PricingsOperations.list_by_resource_group
  - Removed operation
    PricingsOperations.create_or_update_resource_group_pricing
  - Removed operation PricingsOperations.get_resource_group_pricing
  - Removed operation PricingsOperations.get_subscription_pricing

## 0.1.0 (2018-10-29)

  - Initial Release
