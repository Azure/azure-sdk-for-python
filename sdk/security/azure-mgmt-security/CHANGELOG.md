# Release History

## 7.1.0b1 (2025-08-21)

### Features Added

  - Model `SecurityCenter` added property `locations`
  - Model `SecurityCenter` added property `tasks`
  - Model `SecurityCenter` added property `auto_provisioning_settings`
  - Model `SecurityCenter` added property `compliances`
  - Model `SecurityCenter` added property `information_protection_policies`
  - Model `SecurityCenter` added property `workspace_settings`
  - Model `SecurityCenter` added property `alerts_suppression_rules`
  - Model `SecurityCenter` added property `regulatory_compliance_standards`
  - Model `SecurityCenter` added property `regulatory_compliance_controls`
  - Model `SecurityCenter` added property `regulatory_compliance_assessments`
  - Model `SecurityCenter` added property `sub_assessments`
  - Model `SecurityCenter` added property `connectors`
  - Model `SecurityCenter` added property `software_inventories`
  - Model `SecurityCenter` added property `custom_assessment_automations`
  - Model `SecurityCenter` added property `custom_entity_store_assignments`
  - Model `SecurityCenter` added property `mde_onboardings`
  - Model `SecurityCenter` added property `governance_assignments`
  - Model `SecurityCenter` added property `governance_rules`
  - Model `SecurityCenter` added property `applications`
  - Model `SecurityCenter` added property `application`
  - Model `SecurityCenter` added property `security_connector_applications`
  - Model `SecurityCenter` added property `security_connector_application`
  - Model `SecurityCenter` added property `security_operators`
  - Model `SecurityCenter` added property `sql_vulnerability_assessment_baseline_rules`
  - Model `SecurityCenter` added property `sql_vulnerability_assessment_scans`
  - Model `SecurityCenter` added property `sql_vulnerability_assessment_scan_results`
  - Model `SecurityCenter` added property `sensitivity_settings`
  - Model `SecurityCenter` added property `health_reports`
  - Model `SecurityCenter` added property `automations`
  - Model `SecurityCenter` added property `security_contacts`
  - Model `SecurityCenter` added property `security_connectors`
  - Model `SecurityCenter` added property `defender_for_storage`
  - Model `SecurityCenter` added property `operations`
  - Model `SecurityCenter` added property `assessments_metadata`
  - Model `SecurityCenter` added property `assessments`
  - Model `SecurityCenter` added property `private_links`
  - Model `SecurityCenter` added property `private_link_resources`
  - Model `SecurityCenter` added property `private_endpoint_connections`
  - Model `SecurityCenter` added property `compliance_results`
  - Model `SecurityCenter` added property `advanced_threat_protection`
  - Model `SecurityCenter` added property `device_security_groups`
  - Model `SecurityCenter` added property `iot_security_solution_analytics`
  - Model `SecurityCenter` added property `iot_security_solutions_analytics_aggregated_alert`
  - Model `SecurityCenter` added property `iot_security_solutions_analytics_recommendation`
  - Model `SecurityCenter` added property `iot_security_solution`
  - Model `SecurityCenter` added property `allowed_connections`
  - Model `SecurityCenter` added property `discovered_security_solutions`
  - Model `SecurityCenter` added property `external_security_solutions`
  - Model `SecurityCenter` added property `jit_network_access_policies`
  - Model `SecurityCenter` added property `secure_scores`
  - Model `SecurityCenter` added property `secure_score_controls`
  - Model `SecurityCenter` added property `secure_score_control_definitions`
  - Model `SecurityCenter` added property `security_solutions`
  - Model `SecurityCenter` added property `security_solutions_reference_data`
  - Model `SecurityCenter` added property `server_vulnerability_assessment`
  - Model `SecurityCenter` added property `topology`
  - Model `SecurityCenter` added property `alerts`
  - Model `SecurityCenter` added property `settings`
  - Model `SecurityCenter` added property `server_vulnerability_assessments_settings`
  - Model `SecurityCenter` added property `api_collections`
  - Model `SecurityCenter` added property `pricings`
  - Model `SecurityCenter` added property `security_standards`
  - Model `SecurityCenter` added property `standard_assignments`
  - Model `SecurityCenter` added property `custom_recommendations`
  - Model `DevOpsConfigurationProperties` added property `agentless_configuration`
  - Added model `AadConnectivityState`
  - Added enum `AadConnectivityStateEnum`
  - Added model `AadExternalSecuritySolution`
  - Added model `AadSolutionProperties`
  - Added model `AccessTokenAuthentication`
  - Added enum `ActionType`
  - Added model `ActiveConnectionsNotInAllowedRange`
  - Added model `AdditionalData`
  - Added enum `AdditionalWorkspaceDataType`
  - Added enum `AdditionalWorkspaceType`
  - Added model `AdditionalWorkspacesProperties`
  - Added model `AdvancedThreatProtectionSetting`
  - Added model `AgentlessConfiguration`
  - Added enum `AgentlessEnablement`
  - Added model `Alert`
  - Added model `AlertEntity`
  - Added model `AlertList`
  - Added model `AlertPropertiesSupportingEvidence`
  - Added enum `AlertSeverity`
  - Added model `AlertSimulatorBundlesRequestProperties`
  - Added model `AlertSimulatorRequestBody`
  - Added model `AlertSimulatorRequestProperties`
  - Added enum `AlertStatus`
  - Added model `AlertSyncSettings`
  - Added model `AlertsSuppressionRule`
  - Added model `AlertsSuppressionRulesList`
  - Added model `AllowedConnectionsList`
  - Added model `AllowedConnectionsResource`
  - Added model `AllowlistCustomAlertRule`
  - Added model `AmqpC2DMessagesNotInAllowedRange`
  - Added model `AmqpC2DRejectedMessagesNotInAllowedRange`
  - Added model `AmqpD2CMessagesNotInAllowedRange`
  - Added model `ApiCollection`
  - Added model `ApiCollectionList`
  - Added model `Application`
  - Added model `ApplicationCondition`
  - Added enum `ApplicationConditionOperator`
  - Added enum `ApplicationSourceResourceType`
  - Added model `ApplicationsList`
  - Added model `ArcAutoProvisioning`
  - Added model `ArcAutoProvisioningAws`
  - Added model `ArcAutoProvisioningConfiguration`
  - Added model `ArcAutoProvisioningGcp`
  - Added model `AscLocation`
  - Added model `AscLocationList`
  - Added enum `AssessedResourceType`
  - Added model `AssessmentLinks`
  - Added model `AssessmentStatus`
  - Added enum `AssessmentStatusCode`
  - Added model `AssessmentStatusResponse`
  - Added enum `AssessmentType`
  - Added model `AssignedAssessmentItem`
  - Added model `AssignedStandardItem`
  - Added model `AtaExternalSecuritySolution`
  - Added model `AtaSolutionProperties`
  - Added enum `AttestationComplianceState`
  - Added model `AttestationEvidence`
  - Added model `Authentication`
  - Added model `AuthenticationDetailsProperties`
  - Added enum `AuthenticationProvisioningState`
  - Added enum `AuthenticationType`
  - Added enum `AutoProvision`
  - Added model `AutoProvisioningSetting`
  - Added model `AutoProvisioningSettingList`
  - Added model `Automation`
  - Added model `AutomationAction`
  - Added model `AutomationActionEventHub`
  - Added model `AutomationActionLogicApp`
  - Added model `AutomationActionWorkspace`
  - Added model `AutomationList`
  - Added model `AutomationRuleSet`
  - Added model `AutomationScope`
  - Added model `AutomationSource`
  - Added model `AutomationTriggeringRule`
  - Added model `AutomationUpdateModel`
  - Added model `AutomationValidationStatus`
  - Added model `AwAssumeRoleAuthenticationDetailsProperties`
  - Added model `AwsCredsAuthenticationDetailsProperties`
  - Added model `AwsEnvironmentData`
  - Added model `AwsOrganizationalData`
  - Added model `AwsOrganizationalDataMaster`
  - Added model `AwsOrganizationalDataMember`
  - Added model `AzureDevOpsScopeEnvironmentData`
  - Added model `AzureResourceDetails`
  - Added model `AzureResourceIdentifier`
  - Added model `AzureResourceLink`
  - Added model `AzureServersSetting`
  - Added model `AzureTrackedResourceLocation`
  - Added model `Baseline`
  - Added model `BaselineAdjustedResult`
  - Added model `BenchmarkReference`
  - Added enum `BlobScanResultsOptions`
  - Added model `BlobsScanSummary`
  - Added model `BuiltInInfoType`
  - Added enum `BundleType`
  - Added model `CVE`
  - Added model `CVSS`
  - Added enum `Categories`
  - Added model `CefExternalSecuritySolution`
  - Added model `CefSolutionProperties`
  - Added model `CloudErrorBody`
  - Added enum `CloudName`
  - Added model `CloudOffering`
  - Added enum `Code`
  - Added model `Compliance`
  - Added model `ComplianceList`
  - Added model `ComplianceResult`
  - Added model `ComplianceResultList`
  - Added model `ComplianceSegment`
  - Added model `Components1Uu4J47SchemasSecurityassessmentpropertiesbasePropertiesRiskPropertiesPathsItemsPropertiesEdgesItems`
  - Added model `Condition`
  - Added model `ConnectableResource`
  - Added model `ConnectedResource`
  - Added model `ConnectedWorkspace`
  - Added model `ConnectionFromIpNotAllowed`
  - Added model `ConnectionToIpNotAllowed`
  - Added enum `ConnectionType`
  - Added model `ConnectorSetting`
  - Added model `ConnectorSettingList`
  - Added model `ContainerRegistryVulnerabilityProperties`
  - Added enum `ControlType`
  - Added model `CspmMonitorAwsOffering`
  - Added model `CspmMonitorAwsOfferingNativeCloudConnection`
  - Added model `CspmMonitorAzureDevOpsOffering`
  - Added model `CspmMonitorDockerHubOffering`
  - Added model `CspmMonitorGcpOffering`
  - Added model `CspmMonitorGcpOfferingNativeCloudConnection`
  - Added model `CspmMonitorGitLabOffering`
  - Added model `CspmMonitorGithubOffering`
  - Added model `CspmMonitorJFrogOffering`
  - Added model `CustomAlertRule`
  - Added model `CustomAssessmentAutomation`
  - Added model `CustomAssessmentAutomationRequest`
  - Added model `CustomAssessmentAutomationsListResult`
  - Added model `CustomEntityStoreAssignment`
  - Added model `CustomEntityStoreAssignmentRequest`
  - Added model `CustomEntityStoreAssignmentsListResult`
  - Added model `CustomRecommendation`
  - Added model `CustomRecommendationsList`
  - Added model `DataExportSettings`
  - Added enum `DataSource`
  - Added model `DefenderCspmAwsOffering`
  - Added model `DefenderCspmAwsOfferingCiem`
  - Added model `DefenderCspmAwsOfferingCiemDiscovery`
  - Added model `DefenderCspmAwsOfferingCiemOidc`
  - Added model `DefenderCspmAwsOfferingDataSensitivityDiscovery`
  - Added model `DefenderCspmAwsOfferingDatabasesDspm`
  - Added model `DefenderCspmAwsOfferingMdcContainersAgentlessDiscoveryK8S`
  - Added model `DefenderCspmAwsOfferingMdcContainersImageAssessment`
  - Added model `DefenderCspmAwsOfferingVmScanners`
  - Added model `DefenderCspmDockerHubOffering`
  - Added model `DefenderCspmGcpOffering`
  - Added model `DefenderCspmGcpOfferingCiemDiscovery`
  - Added model `DefenderCspmGcpOfferingDataSensitivityDiscovery`
  - Added model `DefenderCspmGcpOfferingMdcContainersAgentlessDiscoveryK8S`
  - Added model `DefenderCspmGcpOfferingMdcContainersImageAssessment`
  - Added model `DefenderCspmGcpOfferingVmScanners`
  - Added model `DefenderCspmJFrogOffering`
  - Added model `DefenderCspmJFrogOfferingMdcContainersImageAssessment`
  - Added model `DefenderFoDatabasesAwsOffering`
  - Added model `DefenderFoDatabasesAwsOfferingArcAutoProvisioning`
  - Added model `DefenderFoDatabasesAwsOfferingDatabasesDspm`
  - Added model `DefenderFoDatabasesAwsOfferingRds`
  - Added model `DefenderForContainersAwsOffering`
  - Added model `DefenderForContainersAwsOfferingCloudWatchToKinesis`
  - Added model `DefenderForContainersAwsOfferingKinesisToS3`
  - Added model `DefenderForContainersAwsOfferingKubernetesDataCollection`
  - Added model `DefenderForContainersAwsOfferingKubernetesService`
  - Added model `DefenderForContainersAwsOfferingMdcContainersAgentlessDiscoveryK8S`
  - Added model `DefenderForContainersAwsOfferingMdcContainersImageAssessment`
  - Added model `DefenderForContainersAwsOfferingVmScanners`
  - Added model `DefenderForContainersDockerHubOffering`
  - Added model `DefenderForContainersGcpOffering`
  - Added model `DefenderForContainersGcpOfferingDataPipelineNativeCloudConnection`
  - Added model `DefenderForContainersGcpOfferingMdcContainersAgentlessDiscoveryK8S`
  - Added model `DefenderForContainersGcpOfferingMdcContainersImageAssessment`
  - Added model `DefenderForContainersGcpOfferingNativeCloudConnection`
  - Added model `DefenderForContainersGcpOfferingVmScanners`
  - Added model `DefenderForContainersJFrogOffering`
  - Added model `DefenderForDatabasesGcpOffering`
  - Added model `DefenderForDatabasesGcpOfferingArcAutoProvisioning`
  - Added model `DefenderForDatabasesGcpOfferingDefenderForDatabasesArcAutoProvisioning`
  - Added model `DefenderForServersAwsOffering`
  - Added model `DefenderForServersAwsOfferingArcAutoProvisioning`
  - Added model `DefenderForServersAwsOfferingDefenderForServers`
  - Added model `DefenderForServersAwsOfferingMdeAutoProvisioning`
  - Added model `DefenderForServersAwsOfferingSubPlan`
  - Added model `DefenderForServersAwsOfferingVaAutoProvisioning`
  - Added model `DefenderForServersAwsOfferingVaAutoProvisioningConfiguration`
  - Added model `DefenderForServersAwsOfferingVmScanners`
  - Added model `DefenderForServersGcpOffering`
  - Added model `DefenderForServersGcpOfferingArcAutoProvisioning`
  - Added model `DefenderForServersGcpOfferingDefenderForServers`
  - Added model `DefenderForServersGcpOfferingMdeAutoProvisioning`
  - Added model `DefenderForServersGcpOfferingSubPlan`
  - Added model `DefenderForServersGcpOfferingVaAutoProvisioning`
  - Added model `DefenderForServersGcpOfferingVaAutoProvisioningConfiguration`
  - Added model `DefenderForServersGcpOfferingVmScanners`
  - Added model `DefenderForStorageSetting`
  - Added model `DefenderForStorageSettingProperties`
  - Added model `DenylistCustomAlertRule`
  - Added model `DeviceSecurityGroup`
  - Added model `DeviceSecurityGroupList`
  - Added model `DirectMethodInvokesNotInAllowedRange`
  - Added model `DiscoveredSecuritySolution`
  - Added model `DiscoveredSecuritySolutionList`
  - Added model `DockerHubEnvironmentData`
  - Added model `ETag`
  - Added model `EdgeIdentifiers`
  - Added enum `Effect`
  - Added enum `EndOfSupportStatus`
  - Added enum `Enforce`
  - Added model `EnvironmentData`
  - Added model `EnvironmentDetails`
  - Added enum `EnvironmentType`
  - Added model `ErrorDetailAutoGenerated`
  - Added model `ErrorDetailAutoGenerated2`
  - Added model `ErrorResponseAutoGenerated`
  - Added model `ErrorResponseAutoGenerated2`
  - Added enum `EventSource`
  - Added model `ExecuteGovernanceRuleParams`
  - Added enum `ExemptionCategory`
  - Added enum `ExpandControlsEnum`
  - Added enum `ExpandEnum`
  - Added enum `ExportData`
  - Added model `Extension`
  - Added model `ExternalSecuritySolution`
  - Added model `ExternalSecuritySolutionKind`
  - Added enum `ExternalSecuritySolutionKindEnum`
  - Added model `ExternalSecuritySolutionList`
  - Added model `ExternalSecuritySolutionProperties`
  - Added model `FailedLocalLoginsNotInAllowedRange`
  - Added model `FileUploadsNotInAllowedRange`
  - Added model `GcpCredentialsDetailsProperties`
  - Added model `GcpOrganizationalData`
  - Added model `GcpOrganizationalDataMember`
  - Added model `GcpOrganizationalDataOrganization`
  - Added model `GcpProjectDetails`
  - Added model `GcpProjectEnvironmentData`
  - Added model `GetSensitivitySettingsListResponse`
  - Added model `GetSensitivitySettingsResponse`
  - Added model `GetSensitivitySettingsResponseProperties`
  - Added model `GetSensitivitySettingsResponsePropertiesMipInformation`
  - Added model `GithubScopeEnvironmentData`
  - Added model `GitlabScopeEnvironmentData`
  - Added model `GovernanceAssignment`
  - Added model `GovernanceAssignmentAdditionalData`
  - Added model `GovernanceAssignmentsList`
  - Added model `GovernanceEmailNotification`
  - Added model `GovernanceRule`
  - Added enum `GovernanceRuleConditionOperator`
  - Added model `GovernanceRuleEmailNotification`
  - Added model `GovernanceRuleList`
  - Added model `GovernanceRuleMetadata`
  - Added model `GovernanceRuleOwnerSource`
  - Added enum `GovernanceRuleOwnerSourceType`
  - Added enum `GovernanceRuleSourceResourceType`
  - Added enum `GovernanceRuleType`
  - Added model `HealthDataClassification`
  - Added model `HealthReport`
  - Added model `HealthReportsList`
  - Added model `HttpC2DMessagesNotInAllowedRange`
  - Added model `HttpC2DRejectedMessagesNotInAllowedRange`
  - Added model `HttpD2CMessagesNotInAllowedRange`
  - Added enum `HybridComputeProvisioningState`
  - Added model `HybridComputeSettingsProperties`
  - Added model `Identity`
  - Added enum `ImplementationEffort`
  - Added model `InfoType`
  - Added model `InformationProtectionKeyword`
  - Added model `InformationProtectionPolicy`
  - Added model `InformationProtectionPolicyList`
  - Added enum `InformationProtectionPolicyName`
  - Added model `InformationType`
  - Added enum `Inherited`
  - Added enum `Intent`
  - Added enum `InventoryKind`
  - Added model `InventoryList`
  - Added enum `InventoryListKind`
  - Added model `IoTSecurityAggregatedAlert`
  - Added model `IoTSecurityAggregatedAlertList`
  - Added model `IoTSecurityAggregatedAlertPropertiesTopDevicesListItem`
  - Added model `IoTSecurityAggregatedRecommendation`
  - Added model `IoTSecurityAggregatedRecommendationList`
  - Added model `IoTSecurityAlertedDevice`
  - Added model `IoTSecurityDeviceAlert`
  - Added model `IoTSecurityDeviceRecommendation`
  - Added model `IoTSecuritySolutionAnalyticsModel`
  - Added model `IoTSecuritySolutionAnalyticsModelList`
  - Added model `IoTSecuritySolutionAnalyticsModelPropertiesDevicesMetricsItem`
  - Added model `IoTSecuritySolutionModel`
  - Added model `IoTSecuritySolutionsList`
  - Added model `IoTSeverityMetrics`
  - Added enum `IsEnabled`
  - Added model `Issue`
  - Added model `JFrogEnvironmentData`
  - Added model `JitNetworkAccessPoliciesList`
  - Added model `JitNetworkAccessPolicy`
  - Added model `JitNetworkAccessPolicyInitiatePort`
  - Added model `JitNetworkAccessPolicyInitiateRequest`
  - Added model `JitNetworkAccessPolicyInitiateVirtualMachine`
  - Added model `JitNetworkAccessPolicyVirtualMachine`
  - Added model `JitNetworkAccessPortRule`
  - Added model `JitNetworkAccessRequest`
  - Added model `JitNetworkAccessRequestPort`
  - Added model `JitNetworkAccessRequestVirtualMachine`
  - Added model `Kind`
  - Added enum `KindEnum`
  - Added model `Label`
  - Added model `ListCustomAlertRule`
  - Added model `LocalUserNotAllowed`
  - Added model `Location`
  - Added model `LogAnalyticsIdentifier`
  - Added model `MalwareScan`
  - Added model `MalwareScanProperties`
  - Added model `MalwareScanningProperties`
  - Added model `MdeOnboardingData`
  - Added model `MdeOnboardingDataList`
  - Added enum `MinimalRiskLevel`
  - Added enum `MinimalSeverity`
  - Added enum `MipIntegrationStatus`
  - Added model `MqttC2DMessagesNotInAllowedRange`
  - Added model `MqttC2DRejectedMessagesNotInAllowedRange`
  - Added model `MqttD2CMessagesNotInAllowedRange`
  - Added model `NodeIdentifier`
  - Added model `NotificationsSource`
  - Added model `NotificationsSourceAlert`
  - Added model `NotificationsSourceAttackPath`
  - Added enum `OfferingType`
  - Added model `OnPremiseResourceDetails`
  - Added model `OnPremiseSqlResourceDetails`
  - Added model `OnUploadFilters`
  - Added model `OnUploadProperties`
  - Added model `Operation`
  - Added model `OperationDisplay`
  - Added model `OperationListResult`
  - Added enum `OperationResult`
  - Added model `OperationResultAutoGenerated`
  - Added model `OperationStatus`
  - Added model `OperationStatusAutoGenerated`
  - Added enum `Operator`
  - Added enum `OrganizationMembershipType`
  - Added enum `Origin`
  - Added model `PartialAssessmentProperties`
  - Added model `Path`
  - Added enum `PermissionProperty`
  - Added model `Pricing`
  - Added model `PricingList`
  - Added enum `PricingTier`
  - Added model `PrivateEndpoint`
  - Added model `PrivateEndpointConnection`
  - Added model `PrivateEndpointConnectionListResult`
  - Added enum `PrivateEndpointConnectionProvisioningState`
  - Added enum `PrivateEndpointServiceConnectionStatus`
  - Added model `PrivateLinkParameters`
  - Added model `PrivateLinkResource`
  - Added model `PrivateLinkResourceAutoGenerated`
  - Added model `PrivateLinkResourceListResult`
  - Added model `PrivateLinkServiceConnectionState`
  - Added model `PrivateLinkUpdate`
  - Added model `PrivateLinksList`
  - Added model `ProcessNotAllowed`
  - Added enum `PropertyType`
  - Added enum `ProtocolEnum`
  - Added enum `ProvisioningState`
  - Added model `ProxyServerProperties`
  - Added model `QueryCheck`
  - Added model `QueuePurgesNotInAllowedRange`
  - Added enum `Rank`
  - Added enum `RecommendationConfigStatus`
  - Added model `RecommendationConfigurationProperties`
  - Added enum `RecommendationSupportedClouds`
  - Added enum `RecommendationType`
  - Added model `RegulatoryComplianceAssessment`
  - Added model `RegulatoryComplianceAssessmentList`
  - Added model `RegulatoryComplianceControl`
  - Added model `RegulatoryComplianceControlList`
  - Added model `RegulatoryComplianceStandard`
  - Added model `RegulatoryComplianceStandardList`
  - Added model `Remediation`
  - Added model `RemediationEta`
  - Added enum `ReportedSeverity`
  - Added model `ResourceAutoGenerated`
  - Added model `ResourceAutoGenerated2`
  - Added model `ResourceAutoGenerated3`
  - Added model `ResourceDetails`
  - Added model `ResourceDetailsAutoGenerated`
  - Added model `ResourceIdentifier`
  - Added enum `ResourceIdentifierType`
  - Added enum `ResourceStatus`
  - Added enum `ResourcesCoverageStatus`
  - Added enum `RiskLevel`
  - Added model `RuleResults`
  - Added model `RuleResultsInput`
  - Added model `RuleResultsProperties`
  - Added enum `RuleSeverity`
  - Added enum `RuleState`
  - Added enum `RuleStatus`
  - Added enum `RuleType`
  - Added model `RulesResults`
  - Added model `RulesResultsInput`
  - Added model `Scan`
  - Added model `ScanProperties`
  - Added model `ScanResult`
  - Added model `ScanResultProperties`
  - Added model `ScanResults`
  - Added enum `ScanState`
  - Added model `ScanSummary`
  - Added enum `ScanTriggerType`
  - Added enum `ScanningMode`
  - Added model `Scans`
  - Added model `ScopeElement`
  - Added model `SecureScoreControlDefinitionItem`
  - Added model `SecureScoreControlDefinitionList`
  - Added model `SecureScoreControlDefinitionSource`
  - Added model `SecureScoreControlDetails`
  - Added model `SecureScoreControlList`
  - Added model `SecureScoreControlScore`
  - Added model `SecureScoreItem`
  - Added model `SecureScoresList`
  - Added model `SecurityAssessment`
  - Added model `SecurityAssessmentList`
  - Added model `SecurityAssessmentMetadata`
  - Added model `SecurityAssessmentMetadataPartnerData`
  - Added model `SecurityAssessmentMetadataProperties`
  - Added model `SecurityAssessmentMetadataPropertiesResponse`
  - Added model `SecurityAssessmentMetadataPropertiesResponsePublishDates`
  - Added model `SecurityAssessmentMetadataResponse`
  - Added model `SecurityAssessmentMetadataResponseList`
  - Added model `SecurityAssessmentPartnerData`
  - Added model `SecurityAssessmentProperties`
  - Added model `SecurityAssessmentPropertiesBase`
  - Added model `SecurityAssessmentPropertiesBaseRisk`
  - Added model `SecurityAssessmentPropertiesBaseRiskPathsItem`
  - Added model `SecurityAssessmentPropertiesBaseRiskPathsPropertiesItemsItem`
  - Added model `SecurityAssessmentPropertiesResponse`
  - Added model `SecurityAssessmentResponse`
  - Added model `SecurityConnector`
  - Added model `SecurityConnectorsList`
  - Added model `SecurityContact`
  - Added model `SecurityContactList`
  - Added enum `SecurityContactName`
  - Added model `SecurityContactPropertiesNotificationsByRole`
  - Added enum `SecurityContactRole`
  - Added enum `SecurityFamily`
  - Added enum `SecurityIssue`
  - Added model `SecurityOperator`
  - Added model `SecurityOperatorList`
  - Added model `SecuritySolution`
  - Added model `SecuritySolutionList`
  - Added enum `SecuritySolutionStatus`
  - Added model `SecuritySolutionsReferenceData`
  - Added model `SecuritySolutionsReferenceDataList`
  - Added model `SecurityStandard`
  - Added model `SecurityStandardList`
  - Added model `SecuritySubAssessment`
  - Added model `SecuritySubAssessmentList`
  - Added model `SecurityTask`
  - Added model `SecurityTaskList`
  - Added model `SecurityTaskParameters`
  - Added model `SensitiveDataDiscoveryProperties`
  - Added model `SensitivityLabel`
  - Added model `ServerVulnerabilityAssessment`
  - Added enum `ServerVulnerabilityAssessmentPropertiesProvisioningState`
  - Added enum `ServerVulnerabilityAssessmentsAzureSettingSelectedProvider`
  - Added model `ServerVulnerabilityAssessmentsList`
  - Added model `ServerVulnerabilityAssessmentsSetting`
  - Added enum `ServerVulnerabilityAssessmentsSettingKind`
  - Added enum `ServerVulnerabilityAssessmentsSettingKindName`
  - Added model `ServerVulnerabilityAssessmentsSettingsList`
  - Added model `ServerVulnerabilityProperties`
  - Added model `ServicePrincipalProperties`
  - Added model `Setting`
  - Added enum `SettingKind`
  - Added enum `SettingName`
  - Added enum `SettingNameAutoGenerated`
  - Added model `SettingsList`
  - Added enum `Severity`
  - Added enum `SeverityEnum`
  - Added model `Software`
  - Added model `SoftwaresList`
  - Added enum `Source`
  - Added enum `SourceType`
  - Added model `SqlServerVulnerabilityProperties`
  - Added model `StandardAssignment`
  - Added model `StandardAssignmentMetadata`
  - Added model `StandardAssignmentPropertiesAttestationData`
  - Added model `StandardAssignmentPropertiesExemptionData`
  - Added model `StandardAssignmentsList`
  - Added model `StandardMetadata`
  - Added enum `StandardSupportedCloud`
  - Added enum `StandardType`
  - Added enum `State`
  - Added enum `Status`
  - Added model `StatusAutoGenerated`
  - Added enum `StatusName`
  - Added enum `StatusReason`
  - Added model `SubAssessmentStatus`
  - Added enum `SubAssessmentStatusCode`
  - Added enum `SubPlan`
  - Added enum `SupportedCloudEnum`
  - Added model `SuppressionAlertsScope`
  - Added enum `Tactics`
  - Added model `Tags`
  - Added model `TagsResource`
  - Added enum `TaskUpdateActionType`
  - Added enum `Techniques`
  - Added enum `Threats`
  - Added model `ThresholdCustomAlertRule`
  - Added model `TimeWindowCustomAlertRule`
  - Added model `TopologyList`
  - Added model `TopologyResource`
  - Added model `TopologySingleResource`
  - Added model `TopologySingleResourceChild`
  - Added model `TopologySingleResourceParent`
  - Added model `TrackedResource`
  - Added model `TrackedResourceAutoGenerated`
  - Added model `TwinUpdatesNotInAllowedRange`
  - Added enum `Type`
  - Added model `UnauthorizedOperationsNotInAllowedRange`
  - Added enum `UnmaskedIpLoggingStatus`
  - Added model `UpdateIotSecuritySolutionData`
  - Added model `UpdateSensitivitySettingsRequest`
  - Added model `UserDefinedResourcesProperties`
  - Added enum `UserImpact`
  - Added model `VaRule`
  - Added enum `ValueType`
  - Added model `VendorReference`
  - Added model `VmScannersAws`
  - Added model `VmScannersBase`
  - Added model `VmScannersBaseConfiguration`
  - Added model `VmScannersGcp`
  - Added model `WorkspaceSetting`
  - Added model `WorkspaceSettingList`
  - Added model `APICollectionsOperations`
  - Added model `AdvancedThreatProtectionOperations`
  - Added model `AlertsOperations`
  - Added model `AlertsSuppressionRulesOperations`
  - Added model `AllowedConnectionsOperations`
  - Added model `ApplicationOperations`
  - Added model `ApplicationsOperations`
  - Added model `AssessmentsMetadataOperations`
  - Added model `AssessmentsOperations`
  - Added model `AutoProvisioningSettingsOperations`
  - Added model `AutomationsOperations`
  - Added model `ComplianceResultsOperations`
  - Added model `CompliancesOperations`
  - Added model `ConnectorsOperations`
  - Added model `CustomAssessmentAutomationsOperations`
  - Added model `CustomEntityStoreAssignmentsOperations`
  - Added model `CustomRecommendationsOperations`
  - Added model `DefenderForStorageOperations`
  - Added model `DeviceSecurityGroupsOperations`
  - Added model `DiscoveredSecuritySolutionsOperations`
  - Added model `ExternalSecuritySolutionsOperations`
  - Added model `GovernanceAssignmentsOperations`
  - Added model `GovernanceRulesOperations`
  - Added model `HealthReportsOperations`
  - Added model `InformationProtectionPoliciesOperations`
  - Added model `IotSecuritySolutionAnalyticsOperations`
  - Added model `IotSecuritySolutionOperations`
  - Added model `IotSecuritySolutionsAnalyticsAggregatedAlertOperations`
  - Added model `IotSecuritySolutionsAnalyticsRecommendationOperations`
  - Added model `JitNetworkAccessPoliciesOperations`
  - Added model `LocationsOperations`
  - Added model `MdeOnboardingsOperations`
  - Added model `Operations`
  - Added model `PricingsOperations`
  - Added model `PrivateEndpointConnectionsOperations`
  - Added model `PrivateLinkResourcesOperations`
  - Added model `PrivateLinksOperations`
  - Added model `RegulatoryComplianceAssessmentsOperations`
  - Added model `RegulatoryComplianceControlsOperations`
  - Added model `RegulatoryComplianceStandardsOperations`
  - Added model `SecureScoreControlDefinitionsOperations`
  - Added model `SecureScoreControlsOperations`
  - Added model `SecureScoresOperations`
  - Added model `SecurityConnectorApplicationOperations`
  - Added model `SecurityConnectorApplicationsOperations`
  - Added model `SecurityConnectorsOperations`
  - Added model `SecurityContactsOperations`
  - Added model `SecurityOperatorsOperations`
  - Added model `SecuritySolutionsOperations`
  - Added model `SecuritySolutionsReferenceDataOperations`
  - Added model `SecurityStandardsOperations`
  - Added model `SensitivitySettingsOperations`
  - Added model `ServerVulnerabilityAssessmentOperations`
  - Added model `ServerVulnerabilityAssessmentsSettingsOperations`
  - Added model `SettingsOperations`
  - Added model `SoftwareInventoriesOperations`
  - Added model `SqlVulnerabilityAssessmentBaselineRulesOperations`
  - Added model `SqlVulnerabilityAssessmentScanResultsOperations`
  - Added model `SqlVulnerabilityAssessmentScansOperations`
  - Added model `StandardAssignmentsOperations`
  - Added model `SubAssessmentsOperations`
  - Added model `TasksOperations`
  - Added model `TopologyOperations`
  - Added model `WorkspaceSettingsOperations`

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
