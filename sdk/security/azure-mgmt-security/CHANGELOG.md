# Release History

## 8.0.0b2 (2026-05-11)

### Features Added

  - Model `AadExternalSecuritySolution` added property `system_data`
  - Model `AdvancedThreatProtectionSetting` added property `system_data`
  - Model `Alert` added property `system_data`
  - Model `AlertSyncSettings` added property `system_data`
  - Model `AlertsSuppressionRule` added property `system_data`
  - Model `AllowedConnectionsResource` added property `system_data`
  - Model `ApiCollection` added property `system_data`
  - Model `Application` added property `system_data`
  - Model `AscLocation` added property `system_data`
  - Enum `AssessedResourceType` added member `SERVER_VULNERABILITY_ASSESSMENT`
  - Enum `AssessmentType` added member `CUSTOM`
  - Enum `AssessmentType` added member `UNKNOWN`
  - Model `AtaExternalSecuritySolution` added property `system_data`
  - Enum `AuthenticationType` added member `ACCESS_TOKEN`
  - Model `AutoProvisioningSetting` added property `system_data`
  - Model `Automation` added property `system_data`
  - Model `CefExternalSecuritySolution` added property `system_data`
  - Model `Compliance` added property `system_data`
  - Model `ComplianceResult` added property `system_data`
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
  - Model `JitNetworkAccessPolicy` added property `system_data`
  - Model `MalwareScanningProperties` added property `automated_response`
  - Model `MdeOnboardingData` added property `system_data`
  - Model `OperationStatusResult` added property `resource_id`
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
  - Enum `RiskLevel` added member `CRITICAL`
  - Enum `RiskLevel` added member `NONE`
  - Model `RuleResults` added property `system_data`
  - Model `RuleResultsProperties` added property `latest_scan`
  - Enum `RuleStatus` added member `NOT_APPLICABLE`
  - Model `RulesResults` added property `next_link`
  - Model `ScanResult` added property `system_data`
  - Model `ScanSummary` added property `files`
  - Model `SecureScoreControlDefinitionItem` added property `system_data`
  - Model `SecureScoreControlDetails` added property `system_data`
  - Model `SecureScoreItem` added property `system_data`
  - Model `SecurityAssessment` added property `system_data`
  - Model `SecurityAssessmentMetadataResponse` added property `system_data`
  - Model `SecurityAssessmentResponse` added property `system_data`
  - Model `SecurityContact` added property `system_data`
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
  - Enum `SettingName` added member `MCAS`
  - Enum `SettingName` added member `SENTINEL`
  - Enum `SettingName` added member `WDATP`
  - Enum `SettingName` added member `WDATP_EXCLUDE_LINUX_PUBLIC_PREVIEW`
  - Enum `SettingName` added member `WDATP_UNIFIED_SOLUTION`
  - Enum `Severity` added member `CRITICAL`
  - Enum `Source` added member `AWS`
  - Enum `Source` added member `GCP`
  - Enum `Source` added member `ON_PREMISE_RESOURCE_DETAILS`
  - Model `StandardAssignment` added property `system_data`
  - Enum `State` added member `OFF`
  - Enum `State` added member `ON`
  - Model `TopologyResource` added property `system_data`
  - Model `TrackedResource` added property `system_data`
  - Model `WorkspaceSetting` added property `system_data`
  - Added enum `ArmActionType`
  - Added model `AssignedComponentItem`
  - Added model `Assignment`
  - Added model `AssignmentProperties`
  - Added model `AssignmentPropertiesAdditionalData`
  - Added enum `AutomatedResponseType`
  - Added model `CloudError`
  - Added model `CommonResourceDetails`
  - Added model `ExtensionResource`
  - Added model `FilesScanSummary`
  - Added model `IssueCreationRequest`
  - Added model `PrivateLinkGroupResource`
  - Added model `PrivateLinkProperties`
  - Added enum `PublicNetworkAccess`
  - Added enum `ResourceIdentityType`
  - Added enum `ScanOperationStatus`
  - Added model `ScanPropertiesV2`
  - Added model `ScanV2`
  - Added model `ScoreDetails`
  - Added model `SecurityAssessmentPropertiesBaseRiskPathsItemEdgeItem`
  - Added model `SecurityAssessmentPropertiesBaseRiskPathsItemNodesItem`
  - Added model `SqlVulnerabilityAssessmentScanOperationResult`
  - Added model `SqlVulnerabilityAssessmentScanOperationResultProperties`
  - Added model `SqlVulnerabilityAssessmentSettings`
  - Added model `SqlVulnerabilityAssessmentSettingsProperties`
  - Added enum `SqlVulnerabilityAssessmentState`
  - Added model `Standard`
  - Added model `StandardComponentProperties`
  - Added model `StandardProperties`
  - Added enum `StandardSupportedClouds`
  - Operation group `DefenderForStorageOperations` added method `list`
  - Operation group `SqlVulnerabilityAssessmentScansOperations` added method `begin_initiate_scan`
  - Operation group `SqlVulnerabilityAssessmentScansOperations` added method `get_scan_operation_result`
  - Added operation group `AssignmentsOperations`
  - Added operation group `GitHubIssuesOperations`
  - Added operation group `OperationResultsOperations`
  - Added operation group `OperationStatusesOperations`
  - Added operation group `SqlVulnerabilityAssessmentSettingsOperations`
  - Added operation group `StandardsOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Client `SecurityCenter` was renamed to `SecurityManagementClient`
  - Model `AdvancedThreatProtectionSetting` moved instance variable `is_enabled` under property `properties` whose type is `AdvancedThreatProtectionProperties`
  - Model `AlertSyncSettings` moved instance variable `enabled` under property `properties` whose type is `AlertSyncSettingProperties`
  - Model `AutomationUpdateModel` moved instance variable `description`, `is_enabled`, `scopes`, `sources` and `actions` under property `properties` whose type is `AutomationProperties`
  - Model `AzureServersSetting` moved instance variable `selected_provider` under property `properties` whose type is `ServerVulnerabilityAssessmentsAzureSettingProperties`
  - Model `DataExportSettings` moved instance variable `enabled` under property `properties` whose type is `DataExportSettingProperties`
  - Model `IoTSecuritySolutionModel` moved instance variable `workspace`, `display_name`, `status`, `export`, `disabled_data_sources`, `iot_hubs`, `user_defined_resources`, `auto_discovered_resources`, `recommendations_configuration`, `unmasked_ip_logging_status` and `additional_workspaces` under property `properties` whose type is `IoTSecuritySolutionProperties`
  - Model `SecureScoreControlDetails` moved instance variable `display_name`, `healthy_resource_count`, `unhealthy_resource_count`, `not_applicable_resource_count`, `weight`, `definition`, `max`, `current` and `percentage` under property `properties` whose type is `SecureScoreControlScoreDetails`
  - Model `SecurityAssessment` moved instance variable `risk`, `resource_details`, `display_name`, `additional_data`, `links`, `metadata`, `partners_data` and `status` under property `properties` whose type is `SecurityAssessmentProperties`
  - Model `SecurityAssessmentMetadataResponse` moved instance variable `display_name`, `policy_definition_id`, `description`, `remediation_description`, `categories`, `severity`, `user_impact`, `implementation_effort`, `threats`, `preview`, `assessment_type`, `partner_data`, `publish_dates`, `planned_deprecation_date`, `tactics` and `techniques` under property `properties` whose type is `SecurityAssessmentMetadataPropertiesResponse`
  - Model `SecurityAssessmentResponse` moved instance variable `risk`, `resource_details`, `display_name`, `additional_data`, `links`, `metadata`, `partners_data` and `status` under property `properties` whose type is `SecurityAssessmentPropertiesResponse`
  - Model `UpdateIotSecuritySolutionData` moved instance variable `user_defined_resources` and `recommendations_configuration` under property `properties` whose type is `UpdateIoTSecuritySolutionProperties`
  - Model `TrackedResource` deleted or renamed its instance variable `etag`
  - Model `TrackedResource` deleted or renamed its instance variable `kind`
  - Deleted or renamed enum value `AuthenticationType.AWS_ASSUME_ROLE`
  - Deleted or renamed enum value `AuthenticationType.AWS_CREDS`
  - Deleted or renamed enum value `AuthenticationType.GCP_CREDENTIALS`
  - Deleted or renamed model `AadConnectivityState`
  - Deleted or renamed model `ActiveConnectionsNotInAllowedRange`
  - Deleted or renamed model `AmqpC2DMessagesNotInAllowedRange`
  - Deleted or renamed model `AmqpC2DRejectedMessagesNotInAllowedRange`
  - Deleted or renamed model `AmqpD2CMessagesNotInAllowedRange`
  - Deleted or renamed model `ApplicationCondition`
  - Deleted or renamed model `ApplicationConditionOperator`
  - Deleted or renamed model `AuthenticationDetailsProperties`
  - Deleted or renamed model `AuthenticationProvisioningState`
  - Deleted or renamed model `AwAssumeRoleAuthenticationDetailsProperties`
  - Deleted or renamed model `AwsCredsAuthenticationDetailsProperties`
  - Deleted or renamed model `AzureDevOpsOrganizationConfiguration`
  - Deleted or renamed model `AzureDevOpsProjectConfiguration`
  - Deleted or renamed model `AzureTrackedResourceLocation`
  - Deleted or renamed model `BaseResourceConfiguration`
  - Deleted or renamed model `Code`
  - Deleted or renamed model `Components1Uu4J47SchemasSecurityassessmentpropertiesbasePropertiesRiskPropertiesPathsItemsPropertiesEdgesItems`
  - Deleted or renamed model `Condition`
  - Deleted or renamed model `ConnectionFromIpNotAllowed`
  - Deleted or renamed model `ConnectionToIpNotAllowed`
  - Deleted or renamed model `ConnectorSetting`
  - Deleted or renamed model `CustomAssessmentAutomation`
  - Deleted or renamed model `CustomAssessmentAutomationRequest`
  - Deleted or renamed model `CustomEntityStoreAssignment`
  - Deleted or renamed model `CustomEntityStoreAssignmentRequest`
  - Deleted or renamed model `DesiredOnboardingState`
  - Deleted or renamed model `DirectMethodInvokesNotInAllowedRange`
  - Deleted or renamed model `ETag`
  - Deleted or renamed model `EdgeIdentifiers`
  - Deleted or renamed model `EndOfSupportStatus`
  - Deleted or renamed model `ErrorDetailAutoGenerated`
  - Deleted or renamed model `ErrorDetailAutoGenerated2`
  - Deleted or renamed model `ErrorResponseAutoGenerated`
  - Deleted or renamed model `ErrorResponseAutoGenerated2`
  - Deleted or renamed model `ExternalSecuritySolutionKind`
  - Deleted or renamed model `FailedLocalLoginsNotInAllowedRange`
  - Deleted or renamed model `FileUploadsNotInAllowedRange`
  - Deleted or renamed model `GcpCredentialsDetailsProperties`
  - Deleted or renamed model `GitHubOwnerConfiguration`
  - Deleted or renamed model `GitLabGroupConfiguration`
  - Deleted or renamed model `GovernanceRuleConditionOperator`
  - Deleted or renamed model `HttpC2DMessagesNotInAllowedRange`
  - Deleted or renamed model `HttpC2DRejectedMessagesNotInAllowedRange`
  - Deleted or renamed model `HttpD2CMessagesNotInAllowedRange`
  - Deleted or renamed model `HybridComputeProvisioningState`
  - Deleted or renamed model `HybridComputeSettingsProperties`
  - Deleted or renamed model `Kind`
  - Deleted or renamed model `LocalUserNotAllowed`
  - Deleted or renamed model `Location`
  - Deleted or renamed model `MqttC2DMessagesNotInAllowedRange`
  - Deleted or renamed model `MqttC2DRejectedMessagesNotInAllowedRange`
  - Deleted or renamed model `MqttD2CMessagesNotInAllowedRange`
  - Deleted or renamed model `NodeIdentifier`
  - Deleted or renamed model `OperationStatusAutoGenerated`
  - Deleted or renamed model `Path`
  - Deleted or renamed model `PermissionProperty`
  - Deleted or renamed model `PrivateLinkParameters`
  - Deleted or renamed model `PrivateLinkResourceAutoGenerated`
  - Deleted or renamed model `ProcessNotAllowed`
  - Deleted or renamed model `ProxyServerProperties`
  - Deleted or renamed model `QueuePurgesNotInAllowedRange`
  - Deleted or renamed model `ResourceAutoGenerated`
  - Deleted or renamed model `ResourceAutoGenerated2`
  - Deleted or renamed model `ResourceAutoGenerated3`
  - Deleted or renamed model `ResourceDetailsAutoGenerated`
  - Deleted or renamed model `Scan`
  - Deleted or renamed model `ScanProperties`
  - Deleted or renamed model `SecureScoreControlScore`
  - Deleted or renamed model `SecurityAssessmentMetadata`
  - Deleted or renamed model `SecurityAssessmentPropertiesBaseRiskPathsPropertiesItemsItem`
  - Deleted or renamed model `ServicePrincipalProperties`
  - Deleted or renamed model `SettingNameAutoGenerated`
  - Deleted or renamed model `Software`
  - Deleted or renamed model `SupportedCloudEnum`
  - Deleted or renamed model `TrackedResourceAutoGenerated`
  - Deleted or renamed model `TwinUpdatesNotInAllowedRange`
  - Deleted or renamed model `UnauthorizedOperationsNotInAllowedRange`
  - Method `AlertsSuppressionRulesOperations.list` changed its parameter `alert_type` from `positional_or_keyword` to `keyword_only`
  - Method `AssessmentsOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PrivateEndpointConnectionsOperations.begin_create_or_update` renamed its parameter `private_link_parameters` to `private_link_name`
  - Method `PrivateEndpointConnectionsOperations.begin_delete` renamed its parameter `private_link_parameters` to `private_link_name`
  - Method `PrivateEndpointConnectionsOperations.get` renamed its parameter `private_link_parameters` to `private_link_name`
  - Method `PrivateEndpointConnectionsOperations.list` renamed its parameter `private_link_parameters` to `private_link_name`
  - Method `PrivateLinkResourcesOperations.get` renamed its parameter `private_link_parameters` to `private_link_name`
  - Method `PrivateLinkResourcesOperations.list` renamed its parameter `private_link_parameters` to `private_link_name`
  - Method `PrivateLinksOperations.begin_create` renamed its parameter `private_link_parameters` to `private_link_name`
  - Method `PrivateLinksOperations.begin_delete` renamed its parameter `private_link_parameters` to `private_link_name`
  - Method `PrivateLinksOperations.get` renamed its parameter `private_link_parameters` to `private_link_name`
  - Method `PrivateLinksOperations.head` renamed its parameter `private_link_parameters` to `private_link_name`
  - Method `PrivateLinksOperations.update` renamed its parameter `private_link_parameters` to `private_link_name`
  - Method `SecureScoreControlsOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `SecureScoreControlsOperations.list_by_secure_score` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `SqlVulnerabilityAssessmentBaselineRulesOperations.add` renamed its parameter `workspace_id` to `database_name`
  - Method `SqlVulnerabilityAssessmentBaselineRulesOperations.create_or_update` renamed its parameter `workspace_id` to `database_name`
  - Method `SqlVulnerabilityAssessmentBaselineRulesOperations.delete` renamed its parameter `workspace_id` to `database_name`
  - Method `SqlVulnerabilityAssessmentBaselineRulesOperations.get` renamed its parameter `workspace_id` to `database_name`
  - Method `SqlVulnerabilityAssessmentBaselineRulesOperations.list` renamed its parameter `workspace_id` to `database_name`
  - Method `SqlVulnerabilityAssessmentScanResultsOperations.get` renamed its parameter `workspace_id` to `database_name`
  - Method `SqlVulnerabilityAssessmentScanResultsOperations.list` renamed its parameter `workspace_id` to `database_name`
  - Method `SqlVulnerabilityAssessmentScansOperations.get` renamed its parameter `workspace_id` to `database_name`
  - Method `SqlVulnerabilityAssessmentScansOperations.list` renamed its parameter `workspace_id` to `database_name`
  - Deleted or renamed operation group `ConnectorsOperations`
  - Deleted or renamed operation group `CustomAssessmentAutomationsOperations`
  - Deleted or renamed operation group `CustomEntityStoreAssignmentsOperations`
  - Deleted or renamed operation group `SoftwareInventoriesOperations`

### Other Changes

  - Deleted model `AlertList`/`AlertsSuppressionRulesList`/`AllowedConnectionsList`/`ApiCollectionList`/`ApplicationsList`/`AscLocationList`/`AutoProvisioningSettingList`/`AutomationList`/`AzureDevOpsProjectListResponse`/`AzureDevOpsRepositoryListResponse`/`ComplianceList`/`ComplianceResultList`/`ConnectorSettingList`/`CustomRecommendationsList`/`DevOpsConfigurationListResponse`/`DeviceSecurityGroupList`/`DiscoveredSecuritySolutionList`/`ExternalSecuritySolutionList`/`GitHubRepositoryListResponse`/`GitLabProjectListResponse`/`GovernanceAssignmentsList`/`GovernanceRuleList`/`HealthReportsList`/`InformationProtectionPolicyList`/`IoTSecurityAggregatedAlertList`/`IoTSecurityAggregatedRecommendationList`/`IoTSecuritySolutionsList`/`JitNetworkAccessPoliciesList`/`PrivateLinksList`/`RegulatoryComplianceAssessmentList`/`RegulatoryComplianceControlList`/`RegulatoryComplianceStandardList`/`ScanResults`/`Scans`/`SecureScoreControlDefinitionList`/`SecureScoreControlList`/`SecureScoresList`/`SecurityAssessmentList`/`SecurityAssessmentMetadataResponseList`/`SecurityConnectorsList`/`SecurityContactList`/`SecurityOperatorList`/`SecuritySolutionList`/`SecurityStandardList`/`SecuritySubAssessmentList`/`SecurityTaskList`/`ServerVulnerabilityAssessmentsSettingsList`/`SettingsList`/`SoftwaresList`/`StandardAssignmentsList`/`TopologyList`/`WorkspaceSettingList` which actually were not used by SDK users

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
