# Release History

## 4.0.0 (2026-06-24)

### Features Added

  - Client `SqlManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `SqlManagementClient` added method `send_request`
  - Client `SqlManagementClient` added operation group `sql_vulnerability_assessment_baseline`
  - Client `SqlManagementClient` added operation group `sql_vulnerability_assessments`
  - Client `SqlManagementClient` added operation group `sql_vulnerability_assessments_settings`
  - Client `SqlManagementClient` added operation group `database_sql_vulnerability_assessment_rule_baselines`
  - Client `SqlManagementClient` added operation group `sql_vulnerability_assessment_rule_baseline`
  - Client `SqlManagementClient` added operation group `database_sql_vulnerability_assessment_scan_result`
  - Client `SqlManagementClient` added operation group `sql_vulnerability_assessment_scan_result`
  - Client `SqlManagementClient` added operation group `sql_vulnerability_assessment_scans`
  - Client `SqlManagementClient` added operation group `distributed_availability_groups`
  - Client `SqlManagementClient` added operation group `endpoint_certificates`
  - Client `SqlManagementClient` added operation group `instance_pool_operations`
  - Client `SqlManagementClient` added operation group `ipv6_firewall_rules`
  - Client `SqlManagementClient` added operation group `job_private_endpoints`
  - Client `SqlManagementClient` added operation group `managed_instance_dtcs`
  - Client `SqlManagementClient` added operation group `managed_server_dns_aliases`
  - Client `SqlManagementClient` added operation group `network_security_perimeter_configurations`
  - Client `SqlManagementClient` added operation group `server_configuration_options`
  - Client `SqlManagementClient` added operation group `server_trust_certificates`
  - Client `SqlManagementClient` added operation group `start_stop_managed_instance_schedules`
  - Client `SqlManagementClient` added operation group `database_encryption_protectors`
  - Client `SqlManagementClient` added operation group `synapse_link_workspaces`
  - Client `SqlManagementClient` added operation group `database_advanced_threat_protection_settings`
  - Client `SqlManagementClient` added operation group `database_sql_vulnerability_assessment_baselines`
  - Client `SqlManagementClient` added operation group `sql_vulnerability_assessment_baselines`
  - Client `SqlManagementClient` added operation group `database_sql_vulnerability_assessments_settings`
  - Client `SqlManagementClient` added operation group `database_sql_vulnerability_assessment_execute_scan`
  - Client `SqlManagementClient` added operation group `sql_vulnerability_assessment_execute_scan`
  - Client `SqlManagementClient` added operation group `sql_vulnerability_assessment_rule_baselines`
  - Client `SqlManagementClient` added operation group `database_sql_vulnerability_assessment_scans`
  - Client `SqlManagementClient` added operation group `managed_database_advanced_threat_protection_settings`
  - Client `SqlManagementClient` added operation group `managed_database_move_operations`
  - Client `SqlManagementClient` added operation group `managed_instance_advanced_threat_protection_settings`
  - Client `SqlManagementClient` added operation group `managed_ledger_digest_uploads`
  - Client `SqlManagementClient` added operation group `server_advanced_threat_protection_settings`
  - Model `Advisor` added property `system_data`
  - Model `BackupShortTermRetentionPolicy` added property `system_data`
  - Enum `BackupStorageRedundancy` added member `GEO_ZONE`
  - Enum `CapabilityGroup` added member `SUPPORTED_JOB_AGENT_VERSIONS`
  - Model `CheckNameAvailabilityRequest` added property `type`
  - Model `DataMaskingPolicy` added property `system_data`
  - Model `DataMaskingRule` added property `system_data`
  - Model `DataWarehouseUserActivities` added property `system_data`
  - Model `Database` added property `identity`
  - Model `Database` added property `system_data`
  - Model `DatabaseAutomaticTuning` added property `system_data`
  - Model `DatabaseBlobAuditingPolicy` added property `system_data`
  - Model `DatabaseColumn` added property `system_data`
  - Model `DatabaseExtensions` added property `system_data`
  - Model `DatabaseOperation` added property `system_data`
  - Model `DatabaseSchema` added property `system_data`
  - Enum `DatabaseStatus` added member `STARTING`
  - Enum `DatabaseStatus` added member `STOPPED`
  - Enum `DatabaseStatus` added member `STOPPING`
  - Model `DatabaseTable` added property `system_data`
  - Model `DatabaseUpdate` added property `identity`
  - Model `DatabaseUsage` added property `system_data`
  - Model `DatabaseVulnerabilityAssessment` added property `system_data`
  - Model `DatabaseVulnerabilityAssessmentRuleBaseline` added property `system_data`
  - Model `DatabaseVulnerabilityAssessmentScansExport` added property `system_data`
  - Model `DeletedServer` added property `system_data`
  - Model `EditionCapability` added property `zone_pinning`
  - Model `ElasticPool` added property `system_data`
  - Model `ElasticPoolEditionCapability` added property `zone_pinning`
  - Model `ElasticPoolOperation` added property `system_data`
  - Model `ElasticPoolPerDatabaseSettings` added property `auto_pause_delay`
  - Model `ElasticPoolPerformanceLevelCapability` added property `supported_min_capacities`
  - Model `ElasticPoolPerformanceLevelCapability` added property `supported_auto_pause_delay`
  - Model `ElasticPoolPerformanceLevelCapability` added property `supported_per_database_auto_pause_delay`
  - Model `ElasticPoolPerformanceLevelCapability` added property `supported_zones`
  - Model `EncryptionProtector` added property `system_data`
  - Model `ExtendedDatabaseBlobAuditingPolicy` added property `system_data`
  - Model `ExtendedServerBlobAuditingPolicy` added property `system_data`
  - Model `FailoverGroup` added property `system_data`
  - Model `FailoverGroupReadOnlyEndpoint` added property `target_server`
  - Model `GeoBackupPolicy` added property `system_data`
  - Model `ImportExportExtensionsOperationResult` added property `system_data`
  - Model `ImportExportOperationResult` added property `system_data`
  - Model `InstanceFailoverGroup` added property `system_data`
  - Model `InstancePool` added property `system_data`
  - Model `InstancePoolUpdate` added property `sku`
  - Model `InstancePoolUpdate` added property `properties`
  - Model `Job` added property `system_data`
  - Model `JobAgent` added property `identity`
  - Model `JobAgent` added property `system_data`
  - Model `JobAgentUpdate` added property `identity`
  - Model `JobAgentUpdate` added property `sku`
  - Model `JobCredential` added property `system_data`
  - Model `JobExecution` added property `system_data`
  - Model `JobStep` added property `system_data`
  - Model `JobTargetGroup` added property `system_data`
  - Model `JobVersion` added property `system_data`
  - Model `LedgerDigestUploads` added property `system_data`
  - Model `LocationCapabilities` added property `supported_job_agent_versions`
  - Model `LocationCapabilities` added property `is_zone_resilient_provisioning_allowed`
  - Model `LongTermRetentionBackup` added property `system_data`
  - Model `LongTermRetentionBackupOperationResult` added property `system_data`
  - Model `LongTermRetentionPolicy` added property `system_data`
  - Model `MaintenanceWindowOptions` added property `system_data`
  - Model `MaintenanceWindows` added property `system_data`
  - Model `ManagedBackupShortTermRetentionPolicy` added property `system_data`
  - Model `ManagedDatabase` added property `system_data`
  - Model `ManagedDatabaseRestoreDetailsResult` added property `system_data`
  - Model `ManagedDatabaseSecurityAlertPolicy` added property `system_data`
  - Enum `ManagedDatabaseStatus` added member `DB_COPYING`
  - Enum `ManagedDatabaseStatus` added member `DB_MOVING`
  - Enum `ManagedDatabaseStatus` added member `STARTING`
  - Enum `ManagedDatabaseStatus` added member `STOPPED`
  - Enum `ManagedDatabaseStatus` added member `STOPPING`
  - Model `ManagedInstance` added property `system_data`
  - Model `ManagedInstanceAdministrator` added property `system_data`
  - Model `ManagedInstanceAzureADOnlyAuthentication` added property `system_data`
  - Model `ManagedInstanceEditionCapability` added property `is_general_purpose_v2`
  - Model `ManagedInstanceEncryptionProtector` added property `system_data`
  - Model `ManagedInstanceFamilyCapability` added property `zone_redundant`
  - Model `ManagedInstanceKey` added property `system_data`
  - Model `ManagedInstanceLongTermRetentionBackup` added property `system_data`
  - Model `ManagedInstanceLongTermRetentionPolicy` added property `system_data`
  - Model `ManagedInstanceOperation` added property `system_data`
  - Model `ManagedInstancePrivateEndpointConnection` added property `system_data`
  - Model `ManagedInstancePrivateLink` added property `system_data`
  - Model `ManagedInstancePrivateLinkProperties` added property `required_zone_names`
  - Model `ManagedInstanceQuery` added property `system_data`
  - Model `ManagedInstanceVcoresCapability` added property `supported_memory_sizes_in_gb`
  - Model `ManagedInstanceVcoresCapability` added property `supported_memory_limits_mb`
  - Model `ManagedInstanceVcoresCapability` added property `included_storage_i_ops`
  - Model `ManagedInstanceVcoresCapability` added property `supported_storage_i_ops`
  - Model `ManagedInstanceVcoresCapability` added property `iops_min_value_override_factor_per_selected_storage_gb`
  - Model `ManagedInstanceVcoresCapability` added property `iops_included_value_override_factor_per_selected_storage_gb`
  - Model `ManagedInstanceVcoresCapability` added property `included_storage_throughput_m_bps`
  - Model `ManagedInstanceVcoresCapability` added property `supported_storage_throughput_m_bps`
  - Model `ManagedInstanceVcoresCapability` added property `throughput_m_bps_min_value_override_factor_per_selected_storage_gb`
  - Model `ManagedInstanceVcoresCapability` added property `throughput_m_bps_included_value_override_factor_per_selected_storage_gb`
  - Model `ManagedInstanceVulnerabilityAssessment` added property `system_data`
  - Model `ManagedTransparentDataEncryption` added property `system_data`
  - Enum `OperationMode` added member `EXPORT`
  - Enum `OperationMode` added member `IMPORT`
  - Model `OutboundFirewallRule` added property `system_data`
  - Model `PrivateEndpointConnection` added property `system_data`
  - Model `PrivateEndpointConnectionProperties` added property `group_ids`
  - Model `PrivateLinkResource` added property `system_data`
  - Model `ProxyResource` added property `system_data`
  - Model `QueryStatistics` added property `system_data`
  - Model `RecommendedAction` added property `system_data`
  - Model `RecommendedSensitivityLabelUpdate` added property `system_data`
  - Model `RecoverableDatabase` added property `system_data`
  - Model `RecoverableManagedDatabase` added property `system_data`
  - Model `ReplicationLink` added property `system_data`
  - Enum `ReplicationLinkType` added member `STANDBY`
  - Model `Resource` added property `system_data`
  - Model `RestorableDroppedDatabase` added property `system_data`
  - Model `RestorableDroppedManagedDatabase` added property `system_data`
  - Model `RestorePoint` added property `system_data`
  - Enum `SecondaryType` added member `STANDBY`
  - Model `SecurityEvent` added property `system_data`
  - Model `SensitivityLabel` added property `system_data`
  - Model `SensitivityLabelUpdate` added property `system_data`
  - Model `Server` added property `system_data`
  - Model `ServerAutomaticTuning` added property `system_data`
  - Model `ServerAzureADAdministrator` added property `system_data`
  - Model `ServerAzureADOnlyAuthentication` added property `system_data`
  - Model `ServerBlobAuditingPolicy` added property `system_data`
  - Model `ServerConnectionPolicy` added property `system_data`
  - Model `ServerDnsAlias` added property `system_data`
  - Model `ServerKey` added property `system_data`
  - Model `ServerOperation` added property `system_data`
  - Model `ServerTrustGroup` added property `system_data`
  - Model `ServerUsage` added property `id`
  - Model `ServerUsage` added property `type`
  - Model `ServerUsage` added property `system_data`
  - Model `ServerVulnerabilityAssessment` added property `system_data`
  - Model `ServiceObjectiveCapability` added property `zone_pinning`
  - Model `ServiceObjectiveCapability` added property `supported_zones`
  - Model `ServiceObjectiveCapability` added property `supported_free_limit_exhaustion_behaviors`
  - Model `SqlAgentConfiguration` added property `system_data`
  - Enum `StorageCapabilityStorageAccountType` added member `GZRS`
  - Enum `StorageKeyType` added member `MANAGED_IDENTITY`
  - Model `SubscriptionUsage` added property `system_data`
  - Model `SyncAgent` added property `system_data`
  - Model `SyncAgentLinkedDatabase` added property `system_data`
  - Model `SyncGroup` added property `system_data`
  - Model `SyncMember` added property `system_data`
  - Model `TdeCertificate` added property `system_data`
  - Model `TimeZone` added property `system_data`
  - Model `TrackedResource` added property `system_data`
  - Model `VirtualCluster` added property `system_data`
  - Model `VirtualNetworkRule` added property `system_data`
  - Model `VulnerabilityAssessmentScanRecord` added property `system_data`
  - Model `WorkloadClassifier` added property `system_data`
  - Model `WorkloadGroup` added property `system_data`
  - Added enum `AdvancedThreatProtectionName`
  - Added model `AdvancedThreatProtectionProperties`
  - Added enum `AdvancedThreatProtectionState`
  - Added enum `AlwaysEncryptedEnclaveType`
  - Added enum `AuthMetadataLookupModes`
  - Added enum `AvailabilityZoneType`
  - Added enum `BackupStorageAccessTier`
  - Added model `Baseline`
  - Added model `BaselineAdjustedResult`
  - Added enum `BaselineName`
  - Added model `BenchmarkReference`
  - Added model `CertificateInfo`
  - Added model `ChangeLongTermRetentionBackupAccessTierParameters`
  - Added enum `CheckNameAvailabilityResourceType`
  - Added enum `ClientClassificationSource`
  - Added enum `DNSRefreshOperationStatus`
  - Added model `DatabaseAdvancedThreatProtection`
  - Added model `DatabaseIdentity`
  - Added enum `DatabaseIdentityType`
  - Added model `DatabaseKey`
  - Added enum `DatabaseKeyType`
  - Added model `DatabaseSqlVulnerabilityAssessmentBaselineSet`
  - Added model `DatabaseSqlVulnerabilityAssessmentBaselineSetProperties`
  - Added model `DatabaseSqlVulnerabilityAssessmentRuleBaseline`
  - Added model `DatabaseSqlVulnerabilityAssessmentRuleBaselineInput`
  - Added model `DatabaseSqlVulnerabilityAssessmentRuleBaselineInputProperties`
  - Added model `DatabaseSqlVulnerabilityAssessmentRuleBaselineListInput`
  - Added model `DatabaseSqlVulnerabilityAssessmentRuleBaselineListInputProperties`
  - Added model `DatabaseSqlVulnerabilityAssessmentRuleBaselineProperties`
  - Added model `DatabaseUserIdentity`
  - Added enum `DevOpsAuditingSettingsName`
  - Added model `DistributedAvailabilityGroup`
  - Added model `DistributedAvailabilityGroupDatabase`
  - Added model `DistributedAvailabilityGroupProperties`
  - Added model `DistributedAvailabilityGroupSetRole`
  - Added model `DistributedAvailabilityGroupsFailoverRequest`
  - Added enum `DtcName`
  - Added model `EndpointCertificate`
  - Added model `EndpointCertificateProperties`
  - Added model `EndpointDependency`
  - Added model `EndpointDetail`
  - Added model `ErrorAdditionalInfo`
  - Added model `ErrorDetail`
  - Added model `ErrorResponse`
  - Added enum `ErrorType`
  - Added enum `ExternalGovernanceStatus`
  - Added enum `FailoverGroupDatabasesSecondaryType`
  - Added enum `FailoverModeType`
  - Added enum `FailoverType`
  - Added enum `FreeLimitExhaustionBehavior`
  - Added model `FreeLimitExhaustionBehaviorCapability`
  - Added enum `HybridSecondaryUsage`
  - Added enum `HybridSecondaryUsageDetected`
  - Added model `IPv6FirewallRule`
  - Added model `IPv6ServerFirewallRuleProperties`
  - Added enum `InaccessibilityReason`
  - Added model `InstancePoolOperation`
  - Added model `InstancePoolOperationProperties`
  - Added enum `InstanceRole`
  - Added model `JobAgentEditionCapability`
  - Added model `JobAgentIdentity`
  - Added enum `JobAgentIdentityType`
  - Added model `JobAgentServiceLevelObjectiveCapability`
  - Added model `JobAgentUserAssignedIdentity`
  - Added model `JobAgentVersionCapability`
  - Added model `JobPrivateEndpoint`
  - Added model `JobPrivateEndpointProperties`
  - Added enum `LinkRole`
  - Added model `LogicalDatabaseTransparentDataEncryption`
  - Added model `ManagedDatabaseAdvancedThreatProtection`
  - Added model `ManagedDatabaseExtendedAccessibilityInfo`
  - Added model `ManagedDatabaseMoveDefinition`
  - Added model `ManagedDatabaseMoveOperationResult`
  - Added model `ManagedDatabaseMoveOperationResultProperties`
  - Added model `ManagedDatabaseRestoreDetailsBackupSetProperties`
  - Added model `ManagedDatabaseRestoreDetailsUnrestorableFileProperties`
  - Added model `ManagedDatabaseStartMoveDefinition`
  - Added model `ManagedInstanceAdvancedThreatProtection`
  - Added enum `ManagedInstanceDatabaseFormat`
  - Added model `ManagedInstanceDtc`
  - Added model `ManagedInstanceDtcProperties`
  - Added model `ManagedInstanceDtcSecuritySettings`
  - Added model `ManagedInstanceDtcTransactionManagerCommunicationSettings`
  - Added model `ManagedInstanceValidateAzureKeyVaultEncryptionKeyRequest`
  - Added model `ManagedLedgerDigestUploads`
  - Added enum `ManagedLedgerDigestUploadsName`
  - Added model `ManagedLedgerDigestUploadsProperties`
  - Added enum `ManagedLedgerDigestUploadsState`
  - Added model `ManagedServerDnsAlias`
  - Added model `ManagedServerDnsAliasAcquisition`
  - Added model `ManagedServerDnsAliasCreation`
  - Added model `ManagedServerDnsAliasProperties`
  - Added model `MaxLimitRangeCapability`
  - Added enum `MinimalTlsVersion`
  - Added enum `MoveOperationMode`
  - Added model `NSPConfigAccessRule`
  - Added model `NSPConfigAccessRuleProperties`
  - Added model `NSPConfigAssociation`
  - Added model `NSPConfigNetworkSecurityPerimeterRule`
  - Added model `NSPConfigPerimeter`
  - Added model `NSPConfigProfile`
  - Added model `NSPProvisioningIssue`
  - Added model `NSPProvisioningIssueProperties`
  - Added model `NetworkSecurityPerimeterConfiguration`
  - Added model `NetworkSecurityPerimeterConfigurationProperties`
  - Added model `OutboundEnvironmentEndpoint`
  - Added model `PerDatabaseAutoPauseDelayTimeRange`
  - Added enum `Phase`
  - Added model `PhaseDetails`
  - Added enum `PricingModel`
  - Added model `QueryCheck`
  - Added model `RefreshExternalGovernanceStatusOperationResult`
  - Added model `RefreshExternalGovernanceStatusOperationResultMI`
  - Added model `RefreshExternalGovernanceStatusOperationResultProperties`
  - Added model `RefreshExternalGovernanceStatusOperationResultPropertiesMI`
  - Added model `Remediation`
  - Added enum `ReplicaConnectedState`
  - Added enum `ReplicaSynchronizationHealth`
  - Added model `ReplicationLinkUpdate`
  - Added model `ReplicationLinkUpdateProperties`
  - Added enum `ReplicationModeType`
  - Added enum `RoleChangeType`
  - Added enum `RuleSeverity`
  - Added enum `RuleStatus`
  - Added enum `RuleType`
  - Added model `ScheduleItem`
  - Added enum `SecondaryInstanceType`
  - Added enum `SeedingModeType`
  - Added model `ServerAdvancedThreatProtection`
  - Added model `ServerConfigurationOption`
  - Added enum `ServerConfigurationOptionName`
  - Added model `ServerConfigurationOptionProperties`
  - Added enum `ServerCreateMode`
  - Added enum `ServerPublicNetworkAccessFlag`
  - Added model `ServerTrustCertificate`
  - Added model `ServerTrustCertificateProperties`
  - Added model `ServicePrincipal`
  - Added enum `ServicePrincipalType`
  - Added enum `SetLegalHoldImmutability`
  - Added model `SqlVulnerabilityAssessment`
  - Added enum `SqlVulnerabilityAssessmentName`
  - Added model `SqlVulnerabilityAssessmentPolicyProperties`
  - Added model `SqlVulnerabilityAssessmentScanError`
  - Added model `SqlVulnerabilityAssessmentScanRecord`
  - Added model `SqlVulnerabilityAssessmentScanRecordProperties`
  - Added model `SqlVulnerabilityAssessmentScanResultProperties`
  - Added model `SqlVulnerabilityAssessmentScanResults`
  - Added enum `SqlVulnerabilityAssessmentState`
  - Added model `StartStopManagedInstanceSchedule`
  - Added model `StartStopManagedInstanceScheduleProperties`
  - Added enum `StartStopScheduleName`
  - Added model `SynapseLinkWorkspace`
  - Added model `SynapseLinkWorkspaceInfoProperties`
  - Added model `SynapseLinkWorkspaceProperties`
  - Added enum `SyncGroupsType`
  - Added enum `TimeBasedImmutability`
  - Added enum `TimeBasedImmutabilityMode`
  - Added model `TransparentDataEncryptionProperties`
  - Added enum `TransparentDataEncryptionScanState`
  - Added model `UpdateVirtualClusterDnsServersOperation`
  - Added model `UpsertManagedServerOperationStepWithEstimatesAndDuration`
  - Added enum `UpsertManagedServerOperationStepWithEstimatesAndDurationStatus`
  - Added model `VaRule`
  - Added model `VirtualClusterDnsServersProperties`
  - Added model `ZonePinningCapability`
  - Operation group `BackupShortTermRetentionPoliciesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `CapabilitiesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `DataMaskingPoliciesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `DataMaskingRulesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `DataWarehouseUserActivitiesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `DatabaseAdvisorsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `DatabaseAutomaticTuningOperations` added parameter `kwargs` in method `__init__`
  - Operation group `DatabaseBlobAuditingPoliciesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `DatabaseColumnsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `DatabaseExtensionsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `DatabaseOperationsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `DatabaseRecommendedActionsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `DatabaseSchemasOperations` added parameter `kwargs` in method `__init__`
  - Operation group `DatabaseSecurityAlertPoliciesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `DatabaseTablesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `DatabaseUsagesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `DatabaseVulnerabilityAssessmentRuleBaselinesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `DatabaseVulnerabilityAssessmentScansOperations` added parameter `kwargs` in method `__init__`
  - Operation group `DatabaseVulnerabilityAssessmentsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `DatabasesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `DatabasesOperations` added parameter `expand` in method `get`
  - Operation group `DatabasesOperations` added parameter `filter` in method `get`
  - Operation group `DeletedServersOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ElasticPoolOperationsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ElasticPoolsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `EncryptionProtectorsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ExtendedDatabaseBlobAuditingPoliciesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ExtendedServerBlobAuditingPoliciesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `FailoverGroupsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `FailoverGroupsOperations` added method `begin_try_planned_before_forced_failover`
  - Operation group `FirewallRulesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `GeoBackupPoliciesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `GeoBackupPoliciesOperations` added method `list`
  - Operation group `InstanceFailoverGroupsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `InstancePoolsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `JobAgentsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `JobCredentialsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `JobExecutionsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `JobStepExecutionsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `JobStepsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `JobTargetExecutionsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `JobTargetGroupsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `JobVersionsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `JobsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `LedgerDigestUploadsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `LedgerDigestUploadsOperations` added method `begin_create_or_update`
  - Operation group `LedgerDigestUploadsOperations` added method `begin_disable`
  - Operation group `LongTermRetentionBackupsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `LongTermRetentionBackupsOperations` added method `begin_change_access_tier`
  - Operation group `LongTermRetentionBackupsOperations` added method `begin_change_access_tier_by_resource_group`
  - Operation group `LongTermRetentionBackupsOperations` added method `begin_lock_time_based_immutability`
  - Operation group `LongTermRetentionBackupsOperations` added method `begin_lock_time_based_immutability_by_resource_group`
  - Operation group `LongTermRetentionBackupsOperations` added method `begin_remove_legal_hold_immutability`
  - Operation group `LongTermRetentionBackupsOperations` added method `begin_remove_legal_hold_immutability_by_resource_group`
  - Operation group `LongTermRetentionBackupsOperations` added method `begin_remove_time_based_immutability`
  - Operation group `LongTermRetentionBackupsOperations` added method `begin_remove_time_based_immutability_by_resource_group`
  - Operation group `LongTermRetentionBackupsOperations` added method `begin_set_legal_hold_immutability`
  - Operation group `LongTermRetentionBackupsOperations` added method `begin_set_legal_hold_immutability_by_resource_group`
  - Operation group `LongTermRetentionManagedInstanceBackupsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `LongTermRetentionManagedInstanceBackupsOperations` added parameter `skip` in method `list_by_location`
  - Operation group `LongTermRetentionManagedInstanceBackupsOperations` added parameter `top` in method `list_by_location`
  - Operation group `LongTermRetentionManagedInstanceBackupsOperations` added parameter `filter` in method `list_by_location`
  - Operation group `LongTermRetentionManagedInstanceBackupsOperations` added parameter `skip` in method `list_by_resource_group_location`
  - Operation group `LongTermRetentionManagedInstanceBackupsOperations` added parameter `top` in method `list_by_resource_group_location`
  - Operation group `LongTermRetentionManagedInstanceBackupsOperations` added parameter `filter` in method `list_by_resource_group_location`
  - Operation group `LongTermRetentionPoliciesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `MaintenanceWindowOptionsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `MaintenanceWindowsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedBackupShortTermRetentionPoliciesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedDatabaseColumnsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedDatabaseQueriesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedDatabaseRecommendedSensitivityLabelsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedDatabaseRestoreDetailsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedDatabaseSchemasOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedDatabaseSecurityAlertPoliciesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedDatabaseSecurityEventsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedDatabaseSensitivityLabelsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedDatabaseSensitivityLabelsOperations` added method `list_by_database`
  - Operation group `ManagedDatabaseTablesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedDatabaseTransparentDataEncryptionOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedDatabaseVulnerabilityAssessmentRuleBaselinesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedDatabaseVulnerabilityAssessmentScansOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedDatabaseVulnerabilityAssessmentsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedDatabasesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedDatabasesOperations` added method `begin_cancel_move`
  - Operation group `ManagedDatabasesOperations` added method `begin_complete_move`
  - Operation group `ManagedDatabasesOperations` added method `begin_reevaluate_inaccessible_database_state`
  - Operation group `ManagedDatabasesOperations` added method `begin_start_move`
  - Operation group `ManagedInstanceAdministratorsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedInstanceAzureADOnlyAuthenticationsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedInstanceEncryptionProtectorsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedInstanceKeysOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedInstanceLongTermRetentionPoliciesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedInstanceLongTermRetentionPoliciesOperations` added method `begin_delete`
  - Operation group `ManagedInstanceOperationsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedInstancePrivateEndpointConnectionsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedInstancePrivateLinkResourcesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedInstanceTdeCertificatesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedInstanceVulnerabilityAssessmentsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedInstancesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedInstancesOperations` added method `begin_reevaluate_inaccessible_database_state`
  - Operation group `ManagedInstancesOperations` added method `begin_refresh_status`
  - Operation group `ManagedInstancesOperations` added method `begin_start`
  - Operation group `ManagedInstancesOperations` added method `begin_stop`
  - Operation group `ManagedInstancesOperations` added method `begin_validate_azure_key_vault_encryption_key`
  - Operation group `ManagedInstancesOperations` added method `list_outbound_network_dependencies_by_managed_instance`
  - Operation group `ManagedRestorableDroppedDatabaseBackupShortTermRetentionPoliciesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ManagedServerSecurityAlertPoliciesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `Operations` added parameter `kwargs` in method `__init__`
  - Operation group `OutboundFirewallRulesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `PrivateEndpointConnectionsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `PrivateLinkResourcesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `RecommendedSensitivityLabelsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `RecoverableDatabasesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `RecoverableDatabasesOperations` added parameter `expand` in method `get`
  - Operation group `RecoverableDatabasesOperations` added parameter `filter` in method `get`
  - Operation group `RecoverableManagedDatabasesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ReplicationLinksOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ReplicationLinksOperations` added method `begin_create_or_update`
  - Operation group `ReplicationLinksOperations` added method `begin_delete`
  - Operation group `ReplicationLinksOperations` added method `begin_update`
  - Operation group `RestorableDroppedDatabasesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `RestorableDroppedDatabasesOperations` added parameter `expand` in method `get`
  - Operation group `RestorableDroppedDatabasesOperations` added parameter `filter` in method `get`
  - Operation group `RestorableDroppedManagedDatabasesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `RestorePointsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `SensitivityLabelsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `SensitivityLabelsOperations` added method `list_by_database`
  - Operation group `ServerAdvisorsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ServerAutomaticTuningOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ServerAzureADAdministratorsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ServerAzureADOnlyAuthenticationsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ServerBlobAuditingPoliciesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ServerConnectionPoliciesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ServerConnectionPoliciesOperations` added method `begin_create_or_update`
  - Operation group `ServerConnectionPoliciesOperations` added method `list_by_server`
  - Operation group `ServerDevOpsAuditSettingsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ServerDnsAliasesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ServerKeysOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ServerOperationsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ServerSecurityAlertPoliciesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ServerTrustGroupsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ServerUsagesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ServerVulnerabilityAssessmentsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ServersOperations` added parameter `kwargs` in method `__init__`
  - Operation group `ServersOperations` added method `begin_refresh_status`
  - Operation group `SqlAgentOperations` added parameter `kwargs` in method `__init__`
  - Operation group `SubscriptionUsagesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `SyncAgentsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `SyncGroupsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `SyncMembersOperations` added parameter `kwargs` in method `__init__`
  - Operation group `TdeCertificatesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `TimeZonesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `TransparentDataEncryptionsOperations` added parameter `kwargs` in method `__init__`
  - Operation group `TransparentDataEncryptionsOperations` added method `begin_create_or_update`
  - Operation group `TransparentDataEncryptionsOperations` added method `begin_resume`
  - Operation group `TransparentDataEncryptionsOperations` added method `begin_suspend`
  - Operation group `TransparentDataEncryptionsOperations` added method `list_by_database`
  - Operation group `UsagesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `VirtualClustersOperations` added parameter `kwargs` in method `__init__`
  - Operation group `VirtualClustersOperations` added method `begin_create_or_update`
  - Operation group `VirtualClustersOperations` added method `begin_update_dns_servers`
  - Operation group `VirtualNetworkRulesOperations` added parameter `kwargs` in method `__init__`
  - Operation group `WorkloadClassifiersOperations` added parameter `kwargs` in method `__init__`
  - Operation group `WorkloadGroupsOperations` added parameter `kwargs` in method `__init__`
  - Added operation group `DatabaseAdvancedThreatProtectionSettingsOperations`
  - Added operation group `DatabaseEncryptionProtectorsOperations`
  - Added operation group `DatabaseSqlVulnerabilityAssessmentBaselinesOperations`
  - Added operation group `DatabaseSqlVulnerabilityAssessmentExecuteScanOperations`
  - Added operation group `DatabaseSqlVulnerabilityAssessmentRuleBaselinesOperations`
  - Added operation group `DatabaseSqlVulnerabilityAssessmentScanResultOperations`
  - Added operation group `DatabaseSqlVulnerabilityAssessmentScansOperations`
  - Added operation group `DatabaseSqlVulnerabilityAssessmentsSettingsOperations`
  - Added operation group `DistributedAvailabilityGroupsOperations`
  - Added operation group `EndpointCertificatesOperations`
  - Added operation group `IPv6FirewallRulesOperations`
  - Added operation group `InstancePoolOperationsOperations`
  - Added operation group `JobPrivateEndpointsOperations`
  - Added operation group `ManagedDatabaseAdvancedThreatProtectionSettingsOperations`
  - Added operation group `ManagedDatabaseMoveOperationsOperations`
  - Added operation group `ManagedInstanceAdvancedThreatProtectionSettingsOperations`
  - Added operation group `ManagedInstanceDtcsOperations`
  - Added operation group `ManagedLedgerDigestUploadsOperations`
  - Added operation group `ManagedServerDnsAliasesOperations`
  - Added operation group `NetworkSecurityPerimeterConfigurationsOperations`
  - Added operation group `ServerAdvancedThreatProtectionSettingsOperations`
  - Added operation group `ServerConfigurationOptionsOperations`
  - Added operation group `ServerTrustCertificatesOperations`
  - Added operation group `SqlVulnerabilityAssessmentBaselineOperations`
  - Added operation group `SqlVulnerabilityAssessmentBaselinesOperations`
  - Added operation group `SqlVulnerabilityAssessmentExecuteScanOperations`
  - Added operation group `SqlVulnerabilityAssessmentRuleBaselineOperations`
  - Added operation group `SqlVulnerabilityAssessmentRuleBaselinesOperations`
  - Added operation group `SqlVulnerabilityAssessmentScanResultOperations`
  - Added operation group `SqlVulnerabilityAssessmentScansOperations`
  - Added operation group `SqlVulnerabilityAssessmentsOperations`
  - Added operation group `SqlVulnerabilityAssessmentsSettingsOperations`
  - Added operation group `StartStopManagedInstanceSchedulesOperations`
  - Added operation group `SynapseLinkWorkspacesOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Deleted or renamed client operation group `SqlManagementClient.server_communication_links`
  - Deleted or renamed client operation group `SqlManagementClient.service_objectives`
  - Deleted or renamed client operation group `SqlManagementClient.elastic_pool_activities`
  - Deleted or renamed client operation group `SqlManagementClient.elastic_pool_database_activities`
  - Deleted or renamed client operation group `SqlManagementClient.transparent_data_encryption_activities`
  - Deleted or renamed client operation group `SqlManagementClient.operations_health`
  - Model `Advisor` moved instance variable `advisor_status`, `auto_execute_status`, `auto_execute_status_inherited_from`, `recommendations_status`, `last_checked` and `recommended_actions` under property `properties` whose type is `AdvisorProperties`
  - Model `BackupShortTermRetentionPolicy` moved instance variable `retention_days` and `diff_backup_interval_in_hours` under property `properties` whose type is `BackupShortTermRetentionPolicyProperties`
  - Model `CopyLongTermRetentionBackupParameters` moved instance variable `target_subscription_id`, `target_resource_group`, `target_server_resource_id`, `target_server_fully_qualified_domain_name`, `target_database_name` and `target_backup_storage_redundancy` under property `properties` whose type is `CopyLongTermRetentionBackupParametersProperties`
  - Model `DataMaskingPolicy` moved instance variable `data_masking_state`, `exempt_principals`, `application_principals` and `masking_level` under property `properties` whose type is `DataMaskingPolicyProperties`
  - Model `DataMaskingRule` moved instance variable `id_properties_id`, `alias_name`, `rule_state`, `schema_name`, `table_name`, `column_name`, `masking_function`, `number_from`, `number_to`, `prefix_size`, `suffix_size` and `replacement_string` under property `properties` whose type is `DataMaskingRuleProperties`
  - Model `DataWarehouseUserActivities` moved instance variable `active_queries_count` under property `properties` whose type is `DataWarehouseUserActivitiesProperties`
  - Model `Database` moved instance variable `create_mode`, `collation`, `max_size_bytes`, `sample_name`, `elastic_pool_id`, `source_database_id`, `status`, `database_id`, `creation_date`, `current_service_objective_name`, `requested_service_objective_name`, `default_secondary_location`, `failover_group_id`, `restore_point_in_time`, `source_database_deletion_date`, `recovery_services_recovery_point_id`, `long_term_retention_backup_resource_id`, `recoverable_database_id`, `restorable_dropped_database_id`, `catalog_collation`, `zone_redundant`, `license_type`, `max_log_size_bytes`, `earliest_restore_date`, `read_scale`, `high_availability_replica_count`, `secondary_type`, `current_sku`, `auto_pause_delay`, `current_backup_storage_redundancy`, `requested_backup_storage_redundancy`, `min_capacity`, `paused_date`, `resumed_date`, `maintenance_configuration_id`, `is_ledger_on` and `is_infra_encryption_enabled` under property `properties` whose type is `DatabaseProperties`
  - Model `DatabaseAutomaticTuning` moved instance variable `desired_state`, `actual_state` and `options` under property `properties` whose type is `DatabaseAutomaticTuningProperties`
  - Model `DatabaseBlobAuditingPolicy` moved instance variable `retention_days`, `audit_actions_and_groups`, `is_storage_secondary_key_in_use`, `is_azure_monitor_target_enabled`, `queue_delay_ms`, `state`, `storage_endpoint`, `storage_account_access_key` and `storage_account_subscription_id` under property `properties` whose type is `DatabaseBlobAuditingPolicyProperties`
  - Model `DatabaseColumn` moved instance variable `column_type`, `temporal_type`, `memory_optimized` and `is_computed` under property `properties` whose type is `DatabaseColumnProperties`
  - Model `DatabaseExtensions` moved instance variable `operation_mode`, `storage_key_type`, `storage_key` and `storage_uri` under property `properties` whose type is `DatabaseExtensionsProperties`
  - Model `DatabaseOperation` moved instance variable `database_name`, `operation`, `operation_friendly_name`, `percent_complete`, `server_name`, `start_time`, `state`, `error_code`, `error_description`, `error_severity`, `is_user_error`, `estimated_completion_time`, `description` and `is_cancellable` under property `properties` whose type is `DatabaseOperationProperties`
  - Model `DatabaseSecurityAlertPolicy` moved instance variable `state`, `disabled_alerts`, `email_addresses`, `email_account_admins`, `storage_endpoint`, `storage_account_access_key`, `retention_days` and `creation_time` under property `properties` whose type is `SecurityAlertsPolicyProperties`
  - Model `DatabaseTable` moved instance variable `temporal_type` and `memory_optimized` under property `properties` whose type is `DatabaseTableProperties`
  - Model `DatabaseUpdate` moved instance variable `create_mode`, `collation`, `max_size_bytes`, `sample_name`, `elastic_pool_id`, `source_database_id`, `status`, `database_id`, `creation_date`, `current_service_objective_name`, `requested_service_objective_name`, `default_secondary_location`, `failover_group_id`, `restore_point_in_time`, `source_database_deletion_date`, `recovery_services_recovery_point_id`, `long_term_retention_backup_resource_id`, `recoverable_database_id`, `restorable_dropped_database_id`, `catalog_collation`, `zone_redundant`, `license_type`, `max_log_size_bytes`, `earliest_restore_date`, `read_scale`, `high_availability_replica_count`, `secondary_type`, `current_sku`, `auto_pause_delay`, `current_backup_storage_redundancy`, `requested_backup_storage_redundancy`, `min_capacity`, `paused_date`, `resumed_date`, `maintenance_configuration_id`, `is_ledger_on` and `is_infra_encryption_enabled` under property `properties` whose type is `DatabaseUpdateProperties`
  - Model `DatabaseUsage` moved instance variable `display_name`, `current_value`, `limit` and `unit` under property `properties` whose type is `DatabaseUsageProperties`
  - Model `DatabaseVulnerabilityAssessment` moved instance variable `storage_container_path`, `storage_container_sas_key`, `storage_account_access_key` and `recurring_scans` under property `properties` whose type is `DatabaseVulnerabilityAssessmentProperties`
  - Model `DatabaseVulnerabilityAssessmentRuleBaseline` moved instance variable `baseline_results` under property `properties` whose type is `DatabaseVulnerabilityAssessmentRuleBaselineProperties`
  - Model `DatabaseVulnerabilityAssessmentScansExport` moved instance variable `exported_report_location` under property `properties` whose type is `DatabaseVulnerabilityAssessmentScanExportProperties`
  - Model `DeletedServer` moved instance variable `version`, `deletion_time`, `original_id` and `fully_qualified_domain_name` under property `properties` whose type is `DeletedServerProperties`
  - Model `ElasticPool` moved instance variable `state`, `creation_date`, `max_size_bytes`, `per_database_settings`, `zone_redundant`, `license_type` and `maintenance_configuration_id` under property `properties` whose type is `ElasticPoolProperties`
  - Model `ElasticPoolOperation` moved instance variable `elastic_pool_name`, `operation`, `operation_friendly_name`, `percent_complete`, `server_name`, `start_time`, `state`, `error_code`, `error_description`, `error_severity`, `is_user_error`, `estimated_completion_time`, `description` and `is_cancellable` under property `properties` whose type is `ElasticPoolOperationProperties`
  - Model `ElasticPoolUpdate` moved instance variable `max_size_bytes`, `per_database_settings`, `zone_redundant`, `license_type` and `maintenance_configuration_id` under property `properties` whose type is `ElasticPoolUpdateProperties`
  - Model `EncryptionProtector` moved instance variable `subregion`, `server_key_name`, `server_key_type`, `uri`, `thumbprint` and `auto_rotation_enabled` under property `properties` whose type is `EncryptionProtectorProperties`
  - Model `ExtendedDatabaseBlobAuditingPolicy` moved instance variable `predicate_expression`, `retention_days`, `audit_actions_and_groups`, `is_storage_secondary_key_in_use`, `is_azure_monitor_target_enabled`, `queue_delay_ms`, `state`, `storage_endpoint`, `storage_account_access_key` and `storage_account_subscription_id` under property `properties` whose type is `ExtendedDatabaseBlobAuditingPolicyProperties`
  - Model `ExtendedServerBlobAuditingPolicy` moved instance variable `is_devops_audit_enabled`, `predicate_expression`, `retention_days`, `audit_actions_and_groups`, `is_storage_secondary_key_in_use`, `is_azure_monitor_target_enabled`, `queue_delay_ms`, `state`, `storage_endpoint`, `storage_account_access_key` and `storage_account_subscription_id` under property `properties` whose type is `ExtendedServerBlobAuditingPolicyProperties`
  - Model `FailoverGroup` moved instance variable `read_write_endpoint`, `read_only_endpoint`, `replication_role`, `replication_state`, `partner_servers` and `databases` under property `properties` whose type is `FailoverGroupProperties`
  - Model `FailoverGroupUpdate` moved instance variable `read_write_endpoint`, `read_only_endpoint` and `databases` under property `properties` whose type is `FailoverGroupUpdateProperties`
  - Model `FirewallRule` moved instance variable `start_ip_address` and `end_ip_address` under property `properties` whose type is `ServerFirewallRuleProperties`
  - Model `FirewallRuleList` renamed its instance variable `values` to `values_property`
  - Model `GeoBackupPolicy` moved instance variable `state` and `storage_type` under property `properties` whose type is `GeoBackupPolicyProperties`
  - Model `ImportExportExtensionsOperationResult` moved instance variable `request_id`, `request_type`, `last_modified_time`, `server_name`, `database_name`, `status` and `error_message` under property `properties` whose type is `ImportExportExtensionsOperationResultProperties`
  - Model `ImportExportOperationResult` moved instance variable `request_id`, `request_type`, `queued_time`, `last_modified_time`, `blob_uri`, `server_name`, `database_name`, `status`, `error_message` and `private_endpoint_connections` under property `properties` whose type is `ImportExportOperationResultProperties`
  - Model `InstanceFailoverGroup` moved instance variable `read_write_endpoint`, `read_only_endpoint`, `replication_role`, `replication_state`, `partner_regions` and `managed_instance_pairs` under property `properties` whose type is `InstanceFailoverGroupProperties`
  - Model `InstancePool` moved instance variable `subnet_id`, `v_cores` and `license_type` under property `properties` whose type is `InstancePoolProperties`
  - Model `Job` moved instance variable `description`, `version` and `schedule` under property `properties` whose type is `JobProperties`
  - Model `JobAgent` moved instance variable `database_id` and `state` under property `properties` whose type is `JobAgentProperties`
  - Model `JobCredential` moved instance variable `username` and `password` under property `properties` whose type is `JobCredentialProperties`
  - Model `JobExecution` moved instance variable `job_version`, `step_name`, `step_id`, `job_execution_id`, `lifecycle`, `provisioning_state`, `create_time`, `start_time`, `end_time`, `current_attempts`, `current_attempt_start_time`, `last_message` and `target` under property `properties` whose type is `JobExecutionProperties`
  - Model `JobStep` moved instance variable `step_id`, `target_group`, `credential`, `action`, `output` and `execution_options` under property `properties` whose type is `JobStepProperties`
  - Model `JobTargetGroup` moved instance variable `members` under property `properties` whose type is `JobTargetGroupProperties`
  - Model `LedgerDigestUploads` moved instance variable `digest_storage_endpoint` and `state` under property `properties` whose type is `LedgerDigestUploadsProperties`
  - Model `LongTermRetentionBackup` moved instance variable `server_name`, `server_create_time`, `database_name`, `database_deletion_time`, `backup_time`, `backup_expiration_time`, `backup_storage_redundancy` and `requested_backup_storage_redundancy` under property `properties` whose type is `LongTermRetentionBackupProperties`
  - Model `LongTermRetentionBackupOperationResult` moved instance variable `request_id`, `operation_type`, `from_backup_resource_id`, `to_backup_resource_id`, `target_backup_storage_redundancy`, `status` and `message` under property `properties` whose type is `LongTermRetentionOperationResultProperties`
  - Model `LongTermRetentionPolicy` moved instance variable `weekly_retention`, `monthly_retention`, `yearly_retention` and `week_of_year` under property `properties` whose type is `LongTermRetentionPolicyProperties`
  - Model `MaintenanceWindowOptions` moved instance variable `is_enabled`, `maintenance_window_cycles`, `min_duration_in_minutes`, `default_duration_in_minutes`, `min_cycles`, `time_granularity_in_minutes` and `allow_multiple_maintenance_windows_per_cycle` under property `properties` whose type is `MaintenanceWindowOptionsProperties`
  - Model `MaintenanceWindows` moved instance variable `time_ranges` under property `properties` whose type is `MaintenanceWindowsProperties`
  - Model `ManagedBackupShortTermRetentionPolicy` moved instance variable `retention_days` under property `properties` whose type is `ManagedBackupShortTermRetentionPolicyProperties`
  - Model `ManagedDatabase` moved instance variable `collation`, `status`, `creation_date`, `earliest_restore_point`, `restore_point_in_time`, `default_secondary_location`, `catalog_collation`, `create_mode`, `storage_container_uri`, `source_database_id`, `restorable_dropped_database_id`, `storage_container_sas_token`, `failover_group_id`, `recoverable_database_id`, `long_term_retention_backup_resource_id`, `auto_complete_restore` and `last_backup_name` under property `properties` whose type is `ManagedDatabaseProperties`
  - Model `ManagedDatabaseRestoreDetailsResult` moved instance variable `status`, `current_restoring_file_name`, `last_restored_file_name`, `last_restored_file_time`, `percent_completed`, `unrestorable_files`, `number_of_files_detected`, `last_uploaded_file_name`, `last_uploaded_file_time` and `block_reason` under property `properties` whose type is `ManagedDatabaseRestoreDetailsProperties`
  - Model `ManagedDatabaseSecurityAlertPolicy` moved instance variable `state`, `disabled_alerts`, `email_addresses`, `email_account_admins`, `storage_endpoint`, `storage_account_access_key`, `retention_days` and `creation_time` under property `properties` whose type is `SecurityAlertPolicyProperties`
  - Model `ManagedDatabaseUpdate` moved instance variable `collation`, `status`, `creation_date`, `earliest_restore_point`, `restore_point_in_time`, `default_secondary_location`, `catalog_collation`, `create_mode`, `storage_container_uri`, `source_database_id`, `restorable_dropped_database_id`, `storage_container_sas_token`, `failover_group_id`, `recoverable_database_id`, `long_term_retention_backup_resource_id`, `auto_complete_restore` and `last_backup_name` under property `properties` whose type is `ManagedDatabaseProperties`
  - Model `ManagedInstance` moved instance variable `provisioning_state`, `managed_instance_create_mode`, `fully_qualified_domain_name`, `administrator_login`, `administrator_login_password`, `subnet_id`, `state`, `license_type`, `v_cores`, `storage_size_in_gb`, `collation`, `dns_zone`, `dns_zone_partner`, `public_data_endpoint_enabled`, `source_managed_instance_id`, `restore_point_in_time`, `proxy_override`, `timezone_id`, `instance_pool_id`, `maintenance_configuration_id`, `private_endpoint_connections`, `minimal_tls_version`, `storage_account_type`, `zone_redundant`, `primary_user_assigned_identity_id`, `key_id` and `administrators` under property `properties` whose type is `ManagedInstanceProperties`
  - Model `ManagedInstanceAdministrator` moved instance variable `administrator_type`, `login`, `sid` and `tenant_id` under property `properties` whose type is `ManagedInstanceAdministratorProperties`
  - Model `ManagedInstanceAzureADOnlyAuthentication` moved instance variable `azure_ad_only_authentication` under property `properties` whose type is `ManagedInstanceAzureADOnlyAuthProperties`
  - Model `ManagedInstanceEditionCapability` deleted or renamed its instance variable `zone_redundant`
  - Model `ManagedInstanceEncryptionProtector` moved instance variable `server_key_name`, `server_key_type`, `uri`, `thumbprint` and `auto_rotation_enabled` under property `properties` whose type is `ManagedInstanceEncryptionProtectorProperties`
  - Model `ManagedInstanceKey` moved instance variable `server_key_type`, `uri`, `thumbprint`, `creation_date` and `auto_rotation_enabled` under property `properties` whose type is `ManagedInstanceKeyProperties`
  - Model `ManagedInstanceLongTermRetentionBackup` moved instance variable `managed_instance_name`, `managed_instance_create_time`, `database_name`, `database_deletion_time`, `backup_time`, `backup_expiration_time` and `backup_storage_redundancy` under property `properties` whose type is `ManagedInstanceLongTermRetentionBackupProperties`
  - Model `ManagedInstanceLongTermRetentionPolicy` moved instance variable `weekly_retention`, `monthly_retention`, `yearly_retention` and `week_of_year` under property `properties` whose type is `ManagedInstanceLongTermRetentionPolicyProperties`
  - Model `ManagedInstanceOperation` moved instance variable `managed_instance_name`, `operation`, `operation_friendly_name`, `percent_complete`, `start_time`, `state`, `error_code`, `error_description`, `error_severity`, `is_user_error`, `estimated_completion_time`, `description`, `is_cancellable`, `operation_parameters` and `operation_steps` under property `properties` whose type is `ManagedInstanceOperationProperties`
  - Model `ManagedInstancePrivateEndpointConnection` moved instance variable `private_endpoint`, `private_link_service_connection_state` and `provisioning_state` under property `properties` whose type is `ManagedInstancePrivateEndpointConnectionProperties`
  - Model `ManagedInstanceQuery` moved instance variable `query_text` under property `properties` whose type is `QueryProperties`
  - Model `ManagedInstanceUpdate` moved instance variable `provisioning_state`, `managed_instance_create_mode`, `fully_qualified_domain_name`, `administrator_login`, `administrator_login_password`, `subnet_id`, `state`, `license_type`, `v_cores`, `storage_size_in_gb`, `collation`, `dns_zone`, `dns_zone_partner`, `public_data_endpoint_enabled`, `source_managed_instance_id`, `restore_point_in_time`, `proxy_override`, `timezone_id`, `instance_pool_id`, `maintenance_configuration_id`, `private_endpoint_connections`, `minimal_tls_version`, `storage_account_type`, `zone_redundant`, `primary_user_assigned_identity_id`, `key_id` and `administrators` under property `properties` whose type is `ManagedInstanceProperties`
  - Model `ManagedInstanceVulnerabilityAssessment` moved instance variable `storage_container_path`, `storage_container_sas_key`, `storage_account_access_key` and `recurring_scans` under property `properties` whose type is `ManagedInstanceVulnerabilityAssessmentProperties`
  - Model `ManagedServerSecurityAlertPolicy` moved instance variable `state`, `disabled_alerts`, `email_addresses`, `email_account_admins`, `storage_endpoint`, `storage_account_access_key`, `retention_days` and `creation_time` under property `properties` whose type is `SecurityAlertsPolicyProperties`
  - Model `ManagedTransparentDataEncryption` moved instance variable `state` under property `properties` whose type is `ManagedTransparentDataEncryptionProperties`
  - Model `OutboundFirewallRule` moved instance variable `provisioning_state` under property `properties` whose type is `OutboundFirewallRuleProperties`
  - Model `PrivateEndpointConnection` moved instance variable `private_endpoint`, `private_link_service_connection_state` and `provisioning_state` under property `properties` whose type is `PrivateEndpointConnectionProperties`
  - Model `QueryStatistics` moved instance variable `database_name`, `query_id`, `start_time`, `end_time` and `intervals` under property `properties` whose type is `QueryStatisticsProperties`
  - Model `RecommendedAction` moved instance variable `recommendation_reason`, `valid_since`, `last_refresh`, `state`, `is_executable_action`, `is_revertable_action`, `is_archived_action`, `execute_action_start_time`, `execute_action_duration`, `revert_action_start_time`, `revert_action_duration`, `execute_action_initiated_by`, `execute_action_initiated_time`, `revert_action_initiated_by`, `revert_action_initiated_time`, `score`, `implementation_details`, `error_details`, `estimated_impact`, `observed_impact`, `time_series`, `linked_objects` and `details` under property `properties` whose type is `RecommendedActionProperties`
  - Model `RecommendedSensitivityLabelUpdate` moved instance variable `op`, `schema`, `table` and `column` under property `properties` whose type is `RecommendedSensitivityLabelUpdateProperties`
  - Model `RecoverableDatabase` moved instance variable `edition`, `service_level_objective`, `elastic_pool_name` and `last_available_backup_date` under property `properties` whose type is `RecoverableDatabaseProperties`
  - Model `RecoverableManagedDatabase` moved instance variable `last_available_backup_date` under property `properties` whose type is `RecoverableManagedDatabaseProperties`
  - Model `ReplicationLink` moved instance variable `partner_server`, `partner_database`, `partner_location`, `role`, `partner_role`, `replication_mode`, `start_time`, `percent_complete`, `replication_state`, `is_termination_allowed` and `link_type` under property `properties` whose type is `ReplicationLinkProperties`
  - Model `RestorableDroppedDatabase` moved instance variable `database_name`, `max_size_bytes`, `elastic_pool_id`, `creation_date`, `deletion_date`, `earliest_restore_date` and `backup_storage_redundancy` under property `properties` whose type is `RestorableDroppedDatabaseProperties`
  - Model `RestorableDroppedManagedDatabase` moved instance variable `database_name`, `creation_date`, `deletion_date` and `earliest_restore_date` under property `properties` whose type is `RestorableDroppedManagedDatabaseProperties`
  - Model `RestorePoint` moved instance variable `restore_point_type`, `earliest_restore_date`, `restore_point_creation_date` and `restore_point_label` under property `properties` whose type is `RestorePointProperties`
  - Model `SecurityEvent` moved instance variable `event_time`, `security_event_type`, `subscription`, `server`, `database`, `client_ip`, `application_name`, `principal_name` and `security_event_sql_injection_additional_properties` under property `properties` whose type is `SecurityEventProperties`
  - Model `SensitivityLabel` moved instance variable `schema_name`, `table_name`, `column_name`, `label_name`, `label_id`, `information_type`, `information_type_id`, `is_disabled` and `rank` under property `properties` whose type is `SensitivityLabelProperties`
  - Model `SensitivityLabelUpdate` moved instance variable `op`, `schema`, `table`, `column` and `sensitivity_label` under property `properties` whose type is `SensitivityLabelUpdateProperties`
  - Model `Server` moved instance variable `administrator_login`, `administrator_login_password`, `version`, `state`, `fully_qualified_domain_name`, `private_endpoint_connections`, `minimal_tls_version`, `public_network_access`, `workspace_feature`, `primary_user_assigned_identity_id`, `federated_client_id`, `key_id`, `administrators` and `restrict_outbound_network_access` under property `properties` whose type is `ServerProperties`
  - Model `ServerAutomaticTuning` moved instance variable `desired_state`, `actual_state` and `options` under property `properties` whose type is `AutomaticTuningServerProperties`
  - Model `ServerAzureADAdministrator` moved instance variable `administrator_type`, `login`, `sid`, `tenant_id` and `azure_ad_only_authentication` under property `properties` whose type is `AdministratorProperties`
  - Model `ServerAzureADOnlyAuthentication` moved instance variable `azure_ad_only_authentication` under property `properties` whose type is `AzureADOnlyAuthProperties`
  - Model `ServerBlobAuditingPolicy` moved instance variable `is_devops_audit_enabled`, `retention_days`, `audit_actions_and_groups`, `is_storage_secondary_key_in_use`, `is_azure_monitor_target_enabled`, `queue_delay_ms`, `state`, `storage_endpoint`, `storage_account_access_key` and `storage_account_subscription_id` under property `properties` whose type is `ServerBlobAuditingPolicyProperties`
  - Model `ServerConnectionPolicy` moved instance variable `connection_type` under property `properties` whose type is `ServerConnectionPolicyProperties`
  - Model `ServerDevOpsAuditingSettings` moved instance variable `is_azure_monitor_target_enabled`, `state`, `storage_endpoint`, `storage_account_access_key` and `storage_account_subscription_id` under property `properties` whose type is `ServerDevOpsAuditSettingsProperties`
  - Model `ServerDnsAlias` moved instance variable `azure_dns_record` under property `properties` whose type is `ServerDnsAliasProperties`
  - Model `ServerKey` moved instance variable `subregion`, `server_key_type`, `uri`, `thumbprint`, `creation_date` and `auto_rotation_enabled` under property `properties` whose type is `ServerKeyProperties`
  - Model `ServerOperation` moved instance variable `operation`, `operation_friendly_name`, `percent_complete`, `server_name`, `start_time`, `state`, `error_code`, `error_description`, `error_severity`, `is_user_error`, `estimated_completion_time`, `description` and `is_cancellable` under property `properties` whose type is `ServerOperationProperties`
  - Model `ServerSecurityAlertPolicy` moved instance variable `state`, `disabled_alerts`, `email_addresses`, `email_account_admins`, `storage_endpoint`, `storage_account_access_key`, `retention_days` and `creation_time` under property `properties` whose type is `SecurityAlertsPolicyProperties`
  - Model `ServerTrustGroup` moved instance variable `group_members` and `trust_scopes` under property `properties` whose type is `ServerTrustGroupProperties`
  - Model `ServerUpdate` moved instance variable `administrator_login`, `administrator_login_password`, `version`, `state`, `fully_qualified_domain_name`, `private_endpoint_connections`, `minimal_tls_version`, `public_network_access`, `workspace_feature`, `primary_user_assigned_identity_id`, `federated_client_id`, `key_id`, `administrators` and `restrict_outbound_network_access` under property `properties` whose type is `ServerProperties`
  - Model `ServerUsage` moved instance variable `resource_name`, `display_name`, `current_value`, `limit`, `unit` and `next_reset_time` under property `properties` whose type is `ServerUsageProperties`
  - Model `ServerVulnerabilityAssessment` moved instance variable `storage_container_path`, `storage_container_sas_key`, `storage_account_access_key` and `recurring_scans` under property `properties` whose type is `ServerVulnerabilityAssessmentProperties`
  - Model `SqlAgentConfiguration` moved instance variable `state` under property `properties` whose type is `SqlAgentConfigurationProperties`
  - Model `SubscriptionUsage` moved instance variable `display_name`, `current_value`, `limit` and `unit` under property `properties` whose type is `SubscriptionUsageProperties`
  - Model `SyncAgent` moved instance variable `name_properties_name`, `sync_database_id`, `last_alive_time`, `state`, `is_up_to_date`, `expiry_time` and `version` under property `properties` whose type is `SyncAgentProperties`
  - Model `SyncAgentLinkedDatabase` moved instance variable `database_type`, `database_id`, `description`, `server_name`, `database_name` and `user_name` under property `properties` whose type is `SyncAgentLinkedDatabaseProperties`
  - Model `SyncGroup` moved instance variable `interval`, `last_sync_time`, `conflict_resolution_policy`, `sync_database_id`, `hub_database_user_name`, `hub_database_password`, `sync_state`, `schema`, `enable_conflict_logging`, `conflict_logging_retention_in_days`, `use_private_link_connection` and `private_endpoint_name` under property `properties` whose type is `SyncGroupProperties`
  - Model `SyncMember` moved instance variable `database_type`, `sync_agent_id`, `sql_server_database_id`, `sync_member_azure_database_resource_id`, `use_private_link_connection`, `private_endpoint_name`, `server_name`, `database_name`, `user_name`, `password`, `sync_direction` and `sync_state` under property `properties` whose type is `SyncMemberProperties`
  - Model `TdeCertificate` moved instance variable `private_blob` and `cert_password` under property `properties` whose type is `TdeCertificateProperties`
  - Model `TimeZone` moved instance variable `time_zone_id` and `display_name` under property `properties` whose type is `TimeZoneProperties`
  - Model `UpdateLongTermRetentionBackupParameters` moved instance variable `requested_backup_storage_redundancy` under property `properties` whose type is `UpdateLongTermRetentionBackupParametersProperties`
  - Model `VirtualCluster` moved instance variable `subnet_id`, `family`, `child_resources` and `maintenance_configuration_id` under property `properties` whose type is `VirtualClusterProperties`
  - Model `VirtualClusterUpdate` moved instance variable `subnet_id`, `family`, `child_resources` and `maintenance_configuration_id` under property `properties` whose type is `VirtualClusterProperties`
  - Model `VirtualNetworkRule` moved instance variable `virtual_network_subnet_id`, `ignore_missing_vnet_service_endpoint` and `state` under property `properties` whose type is `VirtualNetworkRuleProperties`
  - Model `VulnerabilityAssessmentScanRecord` moved instance variable `scan_id`, `trigger_type`, `state`, `start_time`, `end_time`, `errors`, `storage_container_path` and `number_of_failed_security_checks` under property `properties` whose type is `VulnerabilityAssessmentScanRecordProperties`
  - Model `WorkloadClassifier` moved instance variable `member_name`, `label`, `context`, `start_time`, `end_time` and `importance` under property `properties` whose type is `WorkloadClassifierProperties`
  - Model `WorkloadGroup` moved instance variable `min_resource_percent`, `max_resource_percent`, `min_resource_percent_per_request`, `max_resource_percent_per_request`, `importance` and `query_execution_timeout` under property `properties` whose type is `WorkloadGroupProperties`
  - Deleted or renamed model `CurrentBackupStorageRedundancy`
  - Deleted or renamed model `DnsRefreshConfigurationPropertiesStatus`
  - Deleted or renamed model `ElasticPoolActivity`
  - Deleted or renamed model `ElasticPoolDatabaseActivity`
  - Deleted or renamed model `Enum77`
  - Deleted or renamed model `ManagedInstancePropertiesProvisioningState`
  - Deleted or renamed model `ManagedInstanceQueryStatistics`
  - Deleted or renamed model `Metric`
  - Deleted or renamed model `MetricAvailability`
  - Deleted or renamed model `MetricDefinition`
  - Deleted or renamed model `MetricName`
  - Deleted or renamed model `MetricValue`
  - Deleted or renamed model `OperationImpact`
  - Deleted or renamed model `OperationsHealth`
  - Deleted or renamed model `PrimaryAggregationType`
  - Deleted or renamed model `RequestedBackupStorageRedundancy`
  - Deleted or renamed model `RestorableDroppedDatabasePropertiesBackupStorageRedundancy`
  - Deleted or renamed model `SecurityAlertPolicyNameAutoGenerated`
  - Deleted or renamed model `SecurityEventsFilterParameters`
  - Deleted or renamed model `ServerCommunicationLink`
  - Deleted or renamed model `ServiceObjective`
  - Deleted or renamed model `ServiceObjectiveName`
  - Deleted or renamed model `SloUsageMetric`
  - Deleted or renamed model `StorageAccountType`
  - Deleted or renamed model `TargetBackupStorageRedundancy`
  - Deleted or renamed model `TransparentDataEncryption`
  - Deleted or renamed model `TransparentDataEncryptionActivity`
  - Deleted or renamed model `TransparentDataEncryptionActivityStatus`
  - Deleted or renamed model `TransparentDataEncryptionStatus`
  - Deleted or renamed model `UnitDefinitionType`
  - Deleted or renamed model `UnitType`
  - Deleted or renamed model `UnlinkParameters`
  - Deleted or renamed model `UpdateManagedInstanceDnsServersOperation`
  - Deleted or renamed model `UpsertManagedServerOperationStep`
  - Deleted or renamed model `UpsertManagedServerOperationStepStatus`
  - Method `CapabilitiesOperations.list_by_location` changed its parameter `include` from `positional_or_keyword` to `keyword_only`
  - Method `DatabaseAdvisorsOperations.list_by_database` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `DatabaseColumnsOperations.list_by_database` changed its parameter `schema`/`table`/`column`/`order_by`/`skiptoken` from `positional_or_keyword` to `keyword_only`
  - Method `DatabasesOperations.begin_failover` changed its parameter `replica_type` from `positional_or_keyword` to `keyword_only`
  - Method `DatabasesOperations.list_by_server` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Deleted or renamed method `DatabasesOperations.list_metric_definitions`
  - Deleted or renamed method `DatabasesOperations.list_metrics`
  - Deleted or renamed method `ElasticPoolsOperations.list_metric_definitions`
  - Deleted or renamed method `ElasticPoolsOperations.list_metrics`
  - Deleted or renamed method `GeoBackupPoliciesOperations.list_by_database`
  - Method `JobExecutionsOperations.list_by_agent` changed its parameter `create_time_min`/`create_time_max`/`end_time_min`/`end_time_max`/`is_active` from `positional_or_keyword` to `keyword_only`
  - Method `JobExecutionsOperations.list_by_job` changed its parameter `create_time_min`/`create_time_max`/`end_time_min`/`end_time_max`/`is_active` from `positional_or_keyword` to `keyword_only`
  - Method `JobStepExecutionsOperations.list_by_job_execution` changed its parameter `create_time_min`/`create_time_max`/`end_time_min`/`end_time_max`/`is_active` from `positional_or_keyword` to `keyword_only`
  - Method `JobTargetExecutionsOperations.list_by_job_execution` changed its parameter `create_time_min`/`create_time_max`/`end_time_min`/`end_time_max`/`is_active` from `positional_or_keyword` to `keyword_only`
  - Method `JobTargetExecutionsOperations.list_by_step` changed its parameter `create_time_min`/`create_time_max`/`end_time_min`/`end_time_max`/`is_active` from `positional_or_keyword` to `keyword_only`
  - Deleted or renamed method `LedgerDigestUploadsOperations.create_or_update`
  - Deleted or renamed method `LedgerDigestUploadsOperations.disable`
  - Method `LongTermRetentionBackupsOperations.list_by_database` changed its parameter `only_latest_per_database`/`database_state` from `positional_or_keyword` to `keyword_only`
  - Method `LongTermRetentionBackupsOperations.list_by_location` changed its parameter `only_latest_per_database`/`database_state` from `positional_or_keyword` to `keyword_only`
  - Method `LongTermRetentionBackupsOperations.list_by_resource_group_database` changed its parameter `only_latest_per_database`/`database_state` from `positional_or_keyword` to `keyword_only`
  - Method `LongTermRetentionBackupsOperations.list_by_resource_group_location` changed its parameter `only_latest_per_database`/`database_state` from `positional_or_keyword` to `keyword_only`
  - Method `LongTermRetentionBackupsOperations.list_by_resource_group_server` changed its parameter `only_latest_per_database`/`database_state` from `positional_or_keyword` to `keyword_only`
  - Method `LongTermRetentionBackupsOperations.list_by_server` changed its parameter `only_latest_per_database`/`database_state` from `positional_or_keyword` to `keyword_only`
  - Method `LongTermRetentionManagedInstanceBackupsOperations.list_by_database` changed its parameter `only_latest_per_database`/`database_state` from `positional_or_keyword` to `keyword_only`
  - Method `LongTermRetentionManagedInstanceBackupsOperations.list_by_instance` changed its parameter `only_latest_per_database`/`database_state` from `positional_or_keyword` to `keyword_only`
  - Method `LongTermRetentionManagedInstanceBackupsOperations.list_by_location` changed its parameter `only_latest_per_database`/`database_state` from `positional_or_keyword` to `keyword_only`
  - Method `LongTermRetentionManagedInstanceBackupsOperations.list_by_resource_group_database` changed its parameter `only_latest_per_database`/`database_state` from `positional_or_keyword` to `keyword_only`
  - Method `LongTermRetentionManagedInstanceBackupsOperations.list_by_resource_group_instance` changed its parameter `only_latest_per_database`/`database_state` from `positional_or_keyword` to `keyword_only`
  - Method `LongTermRetentionManagedInstanceBackupsOperations.list_by_resource_group_location` changed its parameter `only_latest_per_database`/`database_state` from `positional_or_keyword` to `keyword_only`
  - Method `MaintenanceWindowOptionsOperations.get` changed its parameter `maintenance_window_options_name` from `positional_or_keyword` to `keyword_only`
  - Method `MaintenanceWindowsOperations.create_or_update` changed its parameter `maintenance_window_name` from `positional_or_keyword` to `keyword_only`
  - Method `MaintenanceWindowsOperations.get` changed its parameter `maintenance_window_name` from `positional_or_keyword` to `keyword_only`
  - Method `ManagedDatabaseColumnsOperations.list_by_database` changed its parameter `schema`/`table`/`column`/`order_by`/`skiptoken` from `positional_or_keyword` to `keyword_only`
  - Method `ManagedDatabaseQueriesOperations.list_by_query` changed its parameter `start_time`/`end_time`/`interval` from `positional_or_keyword` to `keyword_only`
  - Method `ManagedDatabaseSecurityEventsOperations.list_by_database` changed its parameter `skiptoken` from `positional_or_keyword` to `keyword_only`
  - Method `ManagedDatabaseSensitivityLabelsOperations.list_current_by_database` changed its parameter `skip_token`/`count` from `positional_or_keyword` to `keyword_only`
  - Method `ManagedDatabaseSensitivityLabelsOperations.list_recommended_by_database` changed its parameter `skip_token`/`include_disabled_recommendations` from `positional_or_keyword` to `keyword_only`
  - Method `ManagedInstancesOperations.begin_failover` changed its parameter `replica_type` from `positional_or_keyword` to `keyword_only`
  - Method `ManagedInstancesOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `ManagedInstancesOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `ManagedInstancesOperations.list_by_instance_pool` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `ManagedInstancesOperations.list_by_managed_instance` changed its parameter `number_of_queries`/`databases`/`start_time`/`end_time`/`interval`/`aggregation_function`/`observation_metric` from `positional_or_keyword` to `keyword_only`
  - Method `ManagedInstancesOperations.list_by_resource_group` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `OutboundFirewallRulesOperations.begin_create_or_update` deleted or renamed its parameter `parameters` of kind `positional_or_keyword`
  - Deleted or renamed method `ReplicationLinksOperations.begin_unlink`
  - Deleted or renamed method `ReplicationLinksOperations.delete`
  - Method `SensitivityLabelsOperations.list_current_by_database` changed its parameter `skip_token`/`count` from `positional_or_keyword` to `keyword_only`
  - Method `SensitivityLabelsOperations.list_recommended_by_database` changed its parameter `skip_token`/`include_disabled_recommendations` from `positional_or_keyword` to `keyword_only`
  - Method `ServerAdvisorsOperations.list_by_server` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Deleted or renamed method `ServerConnectionPoliciesOperations.create_or_update`
  - Method `ServersOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `ServersOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `ServersOperations.list_by_resource_group` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `SyncGroupsOperations.list_logs` changed its parameter `start_time`/`end_time`/`type`/`continuation_token_parameter` from `positional_or_keyword` to `keyword_only`
  - Method `TransparentDataEncryptionsOperations.get` renamed its parameter `transparent_data_encryption_name` to `tde_name`
  - Deleted or renamed method `TransparentDataEncryptionsOperations.create_or_update`
  - Method `UsagesOperations.list_by_instance_pool` changed its parameter `expand_children` from `positional_or_keyword` to `keyword_only`
  - Deleted or renamed method `VirtualClustersOperations.update_dns_servers`
  - Deleted or renamed model `ElasticPoolActivitiesOperations`
  - Deleted or renamed model `ElasticPoolDatabaseActivitiesOperations`
  - Deleted or renamed model `OperationsHealthOperations`
  - Deleted or renamed model `ServerCommunicationLinksOperations`
  - Deleted or renamed model `ServiceObjectivesOperations`
  - Deleted or renamed model `TransparentDataEncryptionActivitiesOperations`
  - Method `BackupShortTermRetentionPoliciesOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.BackupShortTermRetentionPolicy]` to `AsyncLROPoller[BackupShortTermRetentionPolicy]`
  - Method `BackupShortTermRetentionPoliciesOperations.begin_update` changed return type from `AsyncLROPoller[_models.BackupShortTermRetentionPolicy]` to `AsyncLROPoller[BackupShortTermRetentionPolicy]`
  - Method `BackupShortTermRetentionPoliciesOperations.get` changed return type from `_models.BackupShortTermRetentionPolicy` to `BackupShortTermRetentionPolicy`
  - Method `BackupShortTermRetentionPoliciesOperations.list_by_database` changed return type from `AsyncIterable[_models.BackupShortTermRetentionPolicyListResult]` to `AsyncItemPaged[_models.BackupShortTermRetentionPolicy]`
  - Method `CapabilitiesOperations.list_by_location` changed return type from `_models.LocationCapabilities` to `LocationCapabilities`
  - Method `DataMaskingPoliciesOperations.create_or_update` changed return type from `_models.DataMaskingPolicy` to `DataMaskingPolicy`
  - Method `DataMaskingPoliciesOperations.get` changed return type from `_models.DataMaskingPolicy` to `DataMaskingPolicy`
  - Method `DataMaskingRulesOperations.create_or_update` changed return type from `_models.DataMaskingRule` to `DataMaskingRule`
  - Method `DataMaskingRulesOperations.list_by_database` changed return type from `AsyncIterable[_models.DataMaskingRuleListResult]` to `AsyncItemPaged[_models.DataMaskingRule]`
  - Method `DataWarehouseUserActivitiesOperations.get` changed return type from `_models.DataWarehouseUserActivities` to `DataWarehouseUserActivities`
  - Method `DataWarehouseUserActivitiesOperations.list_by_database` changed return type from `AsyncIterable[_models.DataWarehouseUserActivitiesListResult]` to `AsyncItemPaged[_models.DataWarehouseUserActivities]`
  - Method `DatabaseAdvisorsOperations.get` changed return type from `_models.Advisor` to `Advisor`
  - Method `DatabaseAdvisorsOperations.list_by_database` changed return type from `List[_models.Advisor]` to `List[Advisor]`
  - Method `DatabaseAdvisorsOperations.update` changed return type from `_models.Advisor` to `Advisor`
  - Method `DatabaseAutomaticTuningOperations.get` changed return type from `_models.DatabaseAutomaticTuning` to `DatabaseAutomaticTuning`
  - Method `DatabaseAutomaticTuningOperations.update` changed return type from `_models.DatabaseAutomaticTuning` to `DatabaseAutomaticTuning`
  - Method `DatabaseBlobAuditingPoliciesOperations.create_or_update` changed return type from `_models.DatabaseBlobAuditingPolicy` to `DatabaseBlobAuditingPolicy`
  - Method `DatabaseBlobAuditingPoliciesOperations.get` changed return type from `_models.DatabaseBlobAuditingPolicy` to `DatabaseBlobAuditingPolicy`
  - Method `DatabaseBlobAuditingPoliciesOperations.list_by_database` changed return type from `AsyncIterable[_models.DatabaseBlobAuditingPolicyListResult]` to `AsyncItemPaged[_models.DatabaseBlobAuditingPolicy]`
  - Method `DatabaseColumnsOperations.get` changed return type from `_models.DatabaseColumn` to `DatabaseColumn`
  - Method `DatabaseColumnsOperations.list_by_database` changed return type from `AsyncIterable[_models.DatabaseColumnListResult]` to `AsyncItemPaged[_models.DatabaseColumn]`
  - Method `DatabaseColumnsOperations.list_by_table` changed return type from `AsyncIterable[_models.DatabaseColumnListResult]` to `AsyncItemPaged[_models.DatabaseColumn]`
  - Method `DatabaseExtensionsOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.ImportExportExtensionsOperationResult]` to `AsyncLROPoller[ImportExportExtensionsOperationResult]`
  - Method `DatabaseExtensionsOperations.list_by_database` changed return type from `AsyncIterable[_models.ImportExportExtensionsOperationListResult]` to `AsyncItemPaged[_models.ImportExportExtensionsOperationResult]`
  - Method `DatabaseOperationsOperations.list_by_database` changed return type from `AsyncIterable[_models.DatabaseOperationListResult]` to `AsyncItemPaged[_models.DatabaseOperation]`
  - Method `DatabaseRecommendedActionsOperations.get` changed return type from `_models.RecommendedAction` to `RecommendedAction`
  - Method `DatabaseRecommendedActionsOperations.list_by_database_advisor` changed return type from `List[_models.RecommendedAction]` to `List[RecommendedAction]`
  - Method `DatabaseRecommendedActionsOperations.update` changed return type from `_models.RecommendedAction` to `RecommendedAction`
  - Method `DatabaseSchemasOperations.get` changed return type from `_models.DatabaseSchema` to `DatabaseSchema`
  - Method `DatabaseSchemasOperations.list_by_database` changed return type from `AsyncIterable[_models.DatabaseSchemaListResult]` to `AsyncItemPaged[_models.DatabaseSchema]`
  - Method `DatabaseSecurityAlertPoliciesOperations.create_or_update` changed return type from `_models.DatabaseSecurityAlertPolicy` to `DatabaseSecurityAlertPolicy`
  - Method `DatabaseSecurityAlertPoliciesOperations.get` changed return type from `_models.DatabaseSecurityAlertPolicy` to `DatabaseSecurityAlertPolicy`
  - Method `DatabaseSecurityAlertPoliciesOperations.list_by_database` changed return type from `AsyncIterable[_models.DatabaseSecurityAlertListResult]` to `AsyncItemPaged[_models.DatabaseSecurityAlertPolicy]`
  - Method `DatabaseTablesOperations.get` changed return type from `_models.DatabaseTable` to `DatabaseTable`
  - Method `DatabaseTablesOperations.list_by_schema` changed return type from `AsyncIterable[_models.DatabaseTableListResult]` to `AsyncItemPaged[_models.DatabaseTable]`
  - Method `DatabaseUsagesOperations.list_by_database` changed return type from `AsyncIterable[_models.DatabaseUsageListResult]` to `AsyncItemPaged[_models.DatabaseUsage]`
  - Method `DatabaseVulnerabilityAssessmentRuleBaselinesOperations.create_or_update` changed return type from `_models.DatabaseVulnerabilityAssessmentRuleBaseline` to `DatabaseVulnerabilityAssessmentRuleBaseline`
  - Method `DatabaseVulnerabilityAssessmentRuleBaselinesOperations.get` changed return type from `_models.DatabaseVulnerabilityAssessmentRuleBaseline` to `DatabaseVulnerabilityAssessmentRuleBaseline`
  - Method `DatabaseVulnerabilityAssessmentScansOperations.export` changed return type from `_models.DatabaseVulnerabilityAssessmentScansExport` to `DatabaseVulnerabilityAssessmentScansExport`
  - Method `DatabaseVulnerabilityAssessmentScansOperations.get` changed return type from `_models.VulnerabilityAssessmentScanRecord` to `VulnerabilityAssessmentScanRecord`
  - Method `DatabaseVulnerabilityAssessmentScansOperations.list_by_database` changed return type from `AsyncIterable[_models.VulnerabilityAssessmentScanRecordListResult]` to `AsyncItemPaged[_models.VulnerabilityAssessmentScanRecord]`
  - Method `DatabaseVulnerabilityAssessmentsOperations.create_or_update` changed return type from `_models.DatabaseVulnerabilityAssessment` to `DatabaseVulnerabilityAssessment`
  - Method `DatabaseVulnerabilityAssessmentsOperations.get` changed return type from `_models.DatabaseVulnerabilityAssessment` to `DatabaseVulnerabilityAssessment`
  - Method `DatabaseVulnerabilityAssessmentsOperations.list_by_database` changed return type from `AsyncIterable[_models.DatabaseVulnerabilityAssessmentListResult]` to `AsyncItemPaged[_models.DatabaseVulnerabilityAssessment]`
  - Method `DatabasesOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.Database]` to `AsyncLROPoller[Database]`
  - Method `DatabasesOperations.begin_export` changed return type from `AsyncLROPoller[_models.ImportExportOperationResult]` to `AsyncLROPoller[ImportExportOperationResult]`
  - Method `DatabasesOperations.begin_import_method` changed return type from `AsyncLROPoller[_models.ImportExportOperationResult]` to `AsyncLROPoller[ImportExportOperationResult]`
  - Method `DatabasesOperations.begin_pause` changed return type from `AsyncLROPoller[_models.Database]` to `AsyncLROPoller[Database]`
  - Method `DatabasesOperations.begin_resume` changed return type from `AsyncLROPoller[_models.Database]` to `AsyncLROPoller[Database]`
  - Method `DatabasesOperations.begin_update` changed return type from `AsyncLROPoller[_models.Database]` to `AsyncLROPoller[Database]`
  - Method `DatabasesOperations.get` changed return type from `_models.Database` to `Database`
  - Method `DatabasesOperations.list_by_elastic_pool` changed return type from `AsyncIterable[_models.DatabaseListResult]` to `AsyncItemPaged[_models.Database]`
  - Method `DatabasesOperations.list_by_server` changed return type from `AsyncIterable[_models.DatabaseListResult]` to `AsyncItemPaged[_models.Database]`
  - Method `DatabasesOperations.list_inaccessible_by_server` changed return type from `AsyncIterable[_models.DatabaseListResult]` to `AsyncItemPaged[_models.Database]`
  - Method `DeletedServersOperations.begin_recover` changed return type from `AsyncLROPoller[_models.DeletedServer]` to `AsyncLROPoller[DeletedServer]`
  - Method `DeletedServersOperations.get` changed return type from `_models.DeletedServer` to `DeletedServer`
  - Method `DeletedServersOperations.list` changed return type from `AsyncIterable[_models.DeletedServerListResult]` to `AsyncItemPaged[_models.DeletedServer]`
  - Method `DeletedServersOperations.list_by_location` changed return type from `AsyncIterable[_models.DeletedServerListResult]` to `AsyncItemPaged[_models.DeletedServer]`
  - Method `ElasticPoolOperationsOperations.list_by_elastic_pool` changed return type from `AsyncIterable[_models.ElasticPoolOperationListResult]` to `AsyncItemPaged[_models.ElasticPoolOperation]`
  - Method `ElasticPoolsOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.ElasticPool]` to `AsyncLROPoller[ElasticPool]`
  - Method `ElasticPoolsOperations.begin_update` changed return type from `AsyncLROPoller[_models.ElasticPool]` to `AsyncLROPoller[ElasticPool]`
  - Method `ElasticPoolsOperations.get` changed return type from `_models.ElasticPool` to `ElasticPool`
  - Method `ElasticPoolsOperations.list_by_server` changed return type from `AsyncIterable[_models.ElasticPoolListResult]` to `AsyncItemPaged[_models.ElasticPool]`
  - Method `EncryptionProtectorsOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.EncryptionProtector]` to `AsyncLROPoller[EncryptionProtector]`
  - Method `EncryptionProtectorsOperations.get` changed return type from `_models.EncryptionProtector` to `EncryptionProtector`
  - Method `EncryptionProtectorsOperations.list_by_server` changed return type from `AsyncIterable[_models.EncryptionProtectorListResult]` to `AsyncItemPaged[_models.EncryptionProtector]`
  - Method `ExtendedDatabaseBlobAuditingPoliciesOperations.create_or_update` changed return type from `_models.ExtendedDatabaseBlobAuditingPolicy` to `ExtendedDatabaseBlobAuditingPolicy`
  - Method `ExtendedDatabaseBlobAuditingPoliciesOperations.get` changed return type from `_models.ExtendedDatabaseBlobAuditingPolicy` to `ExtendedDatabaseBlobAuditingPolicy`
  - Method `ExtendedDatabaseBlobAuditingPoliciesOperations.list_by_database` changed return type from `AsyncIterable[_models.ExtendedDatabaseBlobAuditingPolicyListResult]` to `AsyncItemPaged[_models.ExtendedDatabaseBlobAuditingPolicy]`
  - Method `ExtendedServerBlobAuditingPoliciesOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.ExtendedServerBlobAuditingPolicy]` to `AsyncLROPoller[ExtendedServerBlobAuditingPolicy]`
  - Method `ExtendedServerBlobAuditingPoliciesOperations.get` changed return type from `_models.ExtendedServerBlobAuditingPolicy` to `ExtendedServerBlobAuditingPolicy`
  - Method `ExtendedServerBlobAuditingPoliciesOperations.list_by_server` changed return type from `AsyncIterable[_models.ExtendedServerBlobAuditingPolicyListResult]` to `AsyncItemPaged[_models.ExtendedServerBlobAuditingPolicy]`
  - Method `FailoverGroupsOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.FailoverGroup]` to `AsyncLROPoller[FailoverGroup]`
  - Method `FailoverGroupsOperations.begin_failover` changed return type from `AsyncLROPoller[_models.FailoverGroup]` to `AsyncLROPoller[FailoverGroup]`
  - Method `FailoverGroupsOperations.begin_force_failover_allow_data_loss` changed return type from `AsyncLROPoller[_models.FailoverGroup]` to `AsyncLROPoller[FailoverGroup]`
  - Method `FailoverGroupsOperations.begin_update` changed return type from `AsyncLROPoller[_models.FailoverGroup]` to `AsyncLROPoller[FailoverGroup]`
  - Method `FailoverGroupsOperations.get` changed return type from `_models.FailoverGroup` to `FailoverGroup`
  - Method `FailoverGroupsOperations.list_by_server` changed return type from `AsyncIterable[_models.FailoverGroupListResult]` to `AsyncItemPaged[_models.FailoverGroup]`
  - Method `FirewallRulesOperations.create_or_update` changed return type from `_models.FirewallRule` to `FirewallRule`
  - Method `FirewallRulesOperations.get` changed return type from `_models.FirewallRule` to `FirewallRule`
  - Method `FirewallRulesOperations.list_by_server` changed return type from `AsyncIterable[_models.FirewallRuleListResult]` to `AsyncItemPaged[_models.FirewallRule]`
  - Method `FirewallRulesOperations.replace` changed return type from `Optional[_models.FirewallRule]` to `Optional[FirewallRule]`
  - Method `GeoBackupPoliciesOperations.create_or_update` changed return type from `_models.GeoBackupPolicy` to `GeoBackupPolicy`
  - Method `GeoBackupPoliciesOperations.get` changed return type from `_models.GeoBackupPolicy` to `GeoBackupPolicy`
  - Method `InstanceFailoverGroupsOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.InstanceFailoverGroup]` to `AsyncLROPoller[InstanceFailoverGroup]`
  - Method `InstanceFailoverGroupsOperations.begin_failover` changed return type from `AsyncLROPoller[_models.InstanceFailoverGroup]` to `AsyncLROPoller[InstanceFailoverGroup]`
  - Method `InstanceFailoverGroupsOperations.begin_force_failover_allow_data_loss` changed return type from `AsyncLROPoller[_models.InstanceFailoverGroup]` to `AsyncLROPoller[InstanceFailoverGroup]`
  - Method `InstanceFailoverGroupsOperations.get` changed return type from `_models.InstanceFailoverGroup` to `InstanceFailoverGroup`
  - Method `InstanceFailoverGroupsOperations.list_by_location` changed return type from `AsyncIterable[_models.InstanceFailoverGroupListResult]` to `AsyncItemPaged[_models.InstanceFailoverGroup]`
  - Method `InstancePoolsOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.InstancePool]` to `AsyncLROPoller[InstancePool]`
  - Method `InstancePoolsOperations.begin_update` changed return type from `AsyncLROPoller[_models.InstancePool]` to `AsyncLROPoller[InstancePool]`
  - Method `InstancePoolsOperations.get` changed return type from `_models.InstancePool` to `InstancePool`
  - Method `InstancePoolsOperations.list` changed return type from `AsyncIterable[_models.InstancePoolListResult]` to `AsyncItemPaged[_models.InstancePool]`
  - Method `InstancePoolsOperations.list_by_resource_group` changed return type from `AsyncIterable[_models.InstancePoolListResult]` to `AsyncItemPaged[_models.InstancePool]`
  - Method `JobAgentsOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.JobAgent]` to `AsyncLROPoller[JobAgent]`
  - Method `JobAgentsOperations.begin_update` changed return type from `AsyncLROPoller[_models.JobAgent]` to `AsyncLROPoller[JobAgent]`
  - Method `JobAgentsOperations.get` changed return type from `_models.JobAgent` to `JobAgent`
  - Method `JobAgentsOperations.list_by_server` changed return type from `AsyncIterable[_models.JobAgentListResult]` to `AsyncItemPaged[_models.JobAgent]`
  - Method `JobCredentialsOperations.create_or_update` changed return type from `_models.JobCredential` to `JobCredential`
  - Method `JobCredentialsOperations.get` changed return type from `_models.JobCredential` to `JobCredential`
  - Method `JobCredentialsOperations.list_by_agent` changed return type from `AsyncIterable[_models.JobCredentialListResult]` to `AsyncItemPaged[_models.JobCredential]`
  - Method `JobExecutionsOperations.begin_create` changed return type from `AsyncLROPoller[_models.JobExecution]` to `AsyncLROPoller[JobExecution]`
  - Method `JobExecutionsOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.JobExecution]` to `AsyncLROPoller[JobExecution]`
  - Method `JobExecutionsOperations.get` changed return type from `_models.JobExecution` to `JobExecution`
  - Method `JobExecutionsOperations.list_by_agent` changed return type from `AsyncIterable[_models.JobExecutionListResult]` to `AsyncItemPaged[_models.JobExecution]`
  - Method `JobExecutionsOperations.list_by_job` changed return type from `AsyncIterable[_models.JobExecutionListResult]` to `AsyncItemPaged[_models.JobExecution]`
  - Method `JobStepExecutionsOperations.get` changed return type from `_models.JobExecution` to `JobExecution`
  - Method `JobStepExecutionsOperations.list_by_job_execution` changed return type from `AsyncIterable[_models.JobExecutionListResult]` to `AsyncItemPaged[_models.JobExecution]`
  - Method `JobStepsOperations.create_or_update` changed return type from `_models.JobStep` to `JobStep`
  - Method `JobStepsOperations.get` changed return type from `_models.JobStep` to `JobStep`
  - Method `JobStepsOperations.get_by_version` changed return type from `_models.JobStep` to `JobStep`
  - Method `JobStepsOperations.list_by_job` changed return type from `AsyncIterable[_models.JobStepListResult]` to `AsyncItemPaged[_models.JobStep]`
  - Method `JobStepsOperations.list_by_version` changed return type from `AsyncIterable[_models.JobStepListResult]` to `AsyncItemPaged[_models.JobStep]`
  - Method `JobTargetExecutionsOperations.get` changed return type from `_models.JobExecution` to `JobExecution`
  - Method `JobTargetExecutionsOperations.list_by_job_execution` changed return type from `AsyncIterable[_models.JobExecutionListResult]` to `AsyncItemPaged[_models.JobExecution]`
  - Method `JobTargetExecutionsOperations.list_by_step` changed return type from `AsyncIterable[_models.JobExecutionListResult]` to `AsyncItemPaged[_models.JobExecution]`
  - Method `JobTargetGroupsOperations.create_or_update` changed return type from `_models.JobTargetGroup` to `JobTargetGroup`
  - Method `JobTargetGroupsOperations.get` changed return type from `_models.JobTargetGroup` to `JobTargetGroup`
  - Method `JobTargetGroupsOperations.list_by_agent` changed return type from `AsyncIterable[_models.JobTargetGroupListResult]` to `AsyncItemPaged[_models.JobTargetGroup]`
  - Method `JobVersionsOperations.get` changed return type from `_models.JobVersion` to `JobVersion`
  - Method `JobVersionsOperations.list_by_job` changed return type from `AsyncIterable[_models.JobVersionListResult]` to `AsyncItemPaged[_models.JobVersion]`
  - Method `JobsOperations.create_or_update` changed return type from `_models.Job` to `Job`
  - Method `JobsOperations.get` changed return type from `_models.Job` to `Job`
  - Method `JobsOperations.list_by_agent` changed return type from `AsyncIterable[_models.JobListResult]` to `AsyncItemPaged[_models.Job]`
  - Method `LedgerDigestUploadsOperations.get` changed return type from `_models.LedgerDigestUploads` to `LedgerDigestUploads`
  - Method `LedgerDigestUploadsOperations.list_by_database` changed return type from `AsyncIterable[_models.LedgerDigestUploadsListResult]` to `AsyncItemPaged[_models.LedgerDigestUploads]`
  - Method `LongTermRetentionBackupsOperations.begin_copy` changed return type from `AsyncLROPoller[_models.LongTermRetentionBackupOperationResult]` to `AsyncLROPoller[LongTermRetentionBackupOperationResult]`
  - Method `LongTermRetentionBackupsOperations.begin_copy_by_resource_group` changed return type from `AsyncLROPoller[_models.LongTermRetentionBackupOperationResult]` to `AsyncLROPoller[LongTermRetentionBackupOperationResult]`
  - Method `LongTermRetentionBackupsOperations.begin_update` changed return type from `AsyncLROPoller[_models.LongTermRetentionBackupOperationResult]` to `AsyncLROPoller[LongTermRetentionBackupOperationResult]`
  - Method `LongTermRetentionBackupsOperations.begin_update_by_resource_group` changed return type from `AsyncLROPoller[_models.LongTermRetentionBackupOperationResult]` to `AsyncLROPoller[LongTermRetentionBackupOperationResult]`
  - Method `LongTermRetentionBackupsOperations.get` changed return type from `_models.LongTermRetentionBackup` to `LongTermRetentionBackup`
  - Method `LongTermRetentionBackupsOperations.get_by_resource_group` changed return type from `_models.LongTermRetentionBackup` to `LongTermRetentionBackup`
  - Method `LongTermRetentionBackupsOperations.list_by_database` changed return type from `AsyncIterable[_models.LongTermRetentionBackupListResult]` to `AsyncItemPaged[_models.LongTermRetentionBackup]`
  - Method `LongTermRetentionBackupsOperations.list_by_location` changed return type from `AsyncIterable[_models.LongTermRetentionBackupListResult]` to `AsyncItemPaged[_models.LongTermRetentionBackup]`
  - Method `LongTermRetentionBackupsOperations.list_by_resource_group_database` changed return type from `AsyncIterable[_models.LongTermRetentionBackupListResult]` to `AsyncItemPaged[_models.LongTermRetentionBackup]`
  - Method `LongTermRetentionBackupsOperations.list_by_resource_group_location` changed return type from `AsyncIterable[_models.LongTermRetentionBackupListResult]` to `AsyncItemPaged[_models.LongTermRetentionBackup]`
  - Method `LongTermRetentionBackupsOperations.list_by_resource_group_server` changed return type from `AsyncIterable[_models.LongTermRetentionBackupListResult]` to `AsyncItemPaged[_models.LongTermRetentionBackup]`
  - Method `LongTermRetentionBackupsOperations.list_by_server` changed return type from `AsyncIterable[_models.LongTermRetentionBackupListResult]` to `AsyncItemPaged[_models.LongTermRetentionBackup]`
  - Method `LongTermRetentionManagedInstanceBackupsOperations.get` changed return type from `_models.ManagedInstanceLongTermRetentionBackup` to `ManagedInstanceLongTermRetentionBackup`
  - Method `LongTermRetentionManagedInstanceBackupsOperations.get_by_resource_group` changed return type from `_models.ManagedInstanceLongTermRetentionBackup` to `ManagedInstanceLongTermRetentionBackup`
  - Method `LongTermRetentionManagedInstanceBackupsOperations.list_by_database` changed return type from `AsyncIterable[_models.ManagedInstanceLongTermRetentionBackupListResult]` to `AsyncItemPaged[_models.ManagedInstanceLongTermRetentionBackup]`
  - Method `LongTermRetentionManagedInstanceBackupsOperations.list_by_instance` changed return type from `AsyncIterable[_models.ManagedInstanceLongTermRetentionBackupListResult]` to `AsyncItemPaged[_models.ManagedInstanceLongTermRetentionBackup]`
  - Method `LongTermRetentionManagedInstanceBackupsOperations.list_by_location` changed return type from `AsyncIterable[_models.ManagedInstanceLongTermRetentionBackupListResult]` to `AsyncItemPaged[_models.ManagedInstanceLongTermRetentionBackup]`
  - Method `LongTermRetentionManagedInstanceBackupsOperations.list_by_resource_group_database` changed return type from `AsyncIterable[_models.ManagedInstanceLongTermRetentionBackupListResult]` to `AsyncItemPaged[_models.ManagedInstanceLongTermRetentionBackup]`
  - Method `LongTermRetentionManagedInstanceBackupsOperations.list_by_resource_group_instance` changed return type from `AsyncIterable[_models.ManagedInstanceLongTermRetentionBackupListResult]` to `AsyncItemPaged[_models.ManagedInstanceLongTermRetentionBackup]`
  - Method `LongTermRetentionManagedInstanceBackupsOperations.list_by_resource_group_location` changed return type from `AsyncIterable[_models.ManagedInstanceLongTermRetentionBackupListResult]` to `AsyncItemPaged[_models.ManagedInstanceLongTermRetentionBackup]`
  - Method `LongTermRetentionPoliciesOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.LongTermRetentionPolicy]` to `AsyncLROPoller[LongTermRetentionPolicy]`
  - Method `LongTermRetentionPoliciesOperations.get` changed return type from `_models.LongTermRetentionPolicy` to `LongTermRetentionPolicy`
  - Method `LongTermRetentionPoliciesOperations.list_by_database` changed return type from `AsyncIterable[_models.LongTermRetentionPolicyListResult]` to `AsyncItemPaged[_models.LongTermRetentionPolicy]`
  - Method `MaintenanceWindowOptionsOperations.get` changed return type from `_models.MaintenanceWindowOptions` to `MaintenanceWindowOptions`
  - Method `MaintenanceWindowsOperations.get` changed return type from `_models.MaintenanceWindows` to `MaintenanceWindows`
  - Method `ManagedBackupShortTermRetentionPoliciesOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.ManagedBackupShortTermRetentionPolicy]` to `AsyncLROPoller[ManagedBackupShortTermRetentionPolicy]`
  - Method `ManagedBackupShortTermRetentionPoliciesOperations.begin_update` changed return type from `AsyncLROPoller[_models.ManagedBackupShortTermRetentionPolicy]` to `AsyncLROPoller[ManagedBackupShortTermRetentionPolicy]`
  - Method `ManagedBackupShortTermRetentionPoliciesOperations.get` changed return type from `_models.ManagedBackupShortTermRetentionPolicy` to `ManagedBackupShortTermRetentionPolicy`
  - Method `ManagedBackupShortTermRetentionPoliciesOperations.list_by_database` changed return type from `AsyncIterable[_models.ManagedBackupShortTermRetentionPolicyListResult]` to `AsyncItemPaged[_models.ManagedBackupShortTermRetentionPolicy]`
  - Method `ManagedDatabaseColumnsOperations.get` changed return type from `_models.DatabaseColumn` to `DatabaseColumn`
  - Method `ManagedDatabaseColumnsOperations.list_by_database` changed return type from `AsyncIterable[_models.DatabaseColumnListResult]` to `AsyncItemPaged[_models.DatabaseColumn]`
  - Method `ManagedDatabaseColumnsOperations.list_by_table` changed return type from `AsyncIterable[_models.DatabaseColumnListResult]` to `AsyncItemPaged[_models.DatabaseColumn]`
  - Method `ManagedDatabaseQueriesOperations.get` changed return type from `_models.ManagedInstanceQuery` to `ManagedInstanceQuery`
  - Method `ManagedDatabaseQueriesOperations.list_by_query` changed return type from `AsyncIterable[_models.ManagedInstanceQueryStatistics]` to `AsyncItemPaged[_models.QueryStatistics]`
  - Method `ManagedDatabaseRestoreDetailsOperations.get` changed return type from `_models.ManagedDatabaseRestoreDetailsResult` to `ManagedDatabaseRestoreDetailsResult`
  - Method `ManagedDatabaseSchemasOperations.get` changed return type from `_models.DatabaseSchema` to `DatabaseSchema`
  - Method `ManagedDatabaseSchemasOperations.list_by_database` changed return type from `AsyncIterable[_models.DatabaseSchemaListResult]` to `AsyncItemPaged[_models.DatabaseSchema]`
  - Method `ManagedDatabaseSecurityAlertPoliciesOperations.create_or_update` changed return type from `_models.ManagedDatabaseSecurityAlertPolicy` to `ManagedDatabaseSecurityAlertPolicy`
  - Method `ManagedDatabaseSecurityAlertPoliciesOperations.get` changed return type from `_models.ManagedDatabaseSecurityAlertPolicy` to `ManagedDatabaseSecurityAlertPolicy`
  - Method `ManagedDatabaseSecurityAlertPoliciesOperations.list_by_database` changed return type from `AsyncIterable[_models.ManagedDatabaseSecurityAlertPolicyListResult]` to `AsyncItemPaged[_models.ManagedDatabaseSecurityAlertPolicy]`
  - Method `ManagedDatabaseSecurityEventsOperations.list_by_database` changed return type from `AsyncIterable[_models.SecurityEventCollection]` to `AsyncItemPaged[_models.SecurityEvent]`
  - Method `ManagedDatabaseSensitivityLabelsOperations.create_or_update` changed return type from `_models.SensitivityLabel` to `SensitivityLabel`
  - Method `ManagedDatabaseSensitivityLabelsOperations.get` changed return type from `_models.SensitivityLabel` to `SensitivityLabel`
  - Method `ManagedDatabaseSensitivityLabelsOperations.list_current_by_database` changed return type from `AsyncIterable[_models.SensitivityLabelListResult]` to `AsyncItemPaged[_models.SensitivityLabel]`
  - Method `ManagedDatabaseSensitivityLabelsOperations.list_recommended_by_database` changed return type from `AsyncIterable[_models.SensitivityLabelListResult]` to `AsyncItemPaged[_models.SensitivityLabel]`
  - Method `ManagedDatabaseTablesOperations.get` changed return type from `_models.DatabaseTable` to `DatabaseTable`
  - Method `ManagedDatabaseTablesOperations.list_by_schema` changed return type from `AsyncIterable[_models.DatabaseTableListResult]` to `AsyncItemPaged[_models.DatabaseTable]`
  - Method `ManagedDatabaseTransparentDataEncryptionOperations.create_or_update` changed return type from `_models.ManagedTransparentDataEncryption` to `ManagedTransparentDataEncryption`
  - Method `ManagedDatabaseTransparentDataEncryptionOperations.get` changed return type from `_models.ManagedTransparentDataEncryption` to `ManagedTransparentDataEncryption`
  - Method `ManagedDatabaseTransparentDataEncryptionOperations.list_by_database` changed return type from `AsyncIterable[_models.ManagedTransparentDataEncryptionListResult]` to `AsyncItemPaged[_models.ManagedTransparentDataEncryption]`
  - Method `ManagedDatabaseVulnerabilityAssessmentRuleBaselinesOperations.create_or_update` changed return type from `_models.DatabaseVulnerabilityAssessmentRuleBaseline` to `DatabaseVulnerabilityAssessmentRuleBaseline`
  - Method `ManagedDatabaseVulnerabilityAssessmentRuleBaselinesOperations.get` changed return type from `_models.DatabaseVulnerabilityAssessmentRuleBaseline` to `DatabaseVulnerabilityAssessmentRuleBaseline`
  - Method `ManagedDatabaseVulnerabilityAssessmentScansOperations.export` changed return type from `_models.DatabaseVulnerabilityAssessmentScansExport` to `DatabaseVulnerabilityAssessmentScansExport`
  - Method `ManagedDatabaseVulnerabilityAssessmentScansOperations.get` changed return type from `_models.VulnerabilityAssessmentScanRecord` to `VulnerabilityAssessmentScanRecord`
  - Method `ManagedDatabaseVulnerabilityAssessmentScansOperations.list_by_database` changed return type from `AsyncIterable[_models.VulnerabilityAssessmentScanRecordListResult]` to `AsyncItemPaged[_models.VulnerabilityAssessmentScanRecord]`
  - Method `ManagedDatabaseVulnerabilityAssessmentsOperations.create_or_update` changed return type from `_models.DatabaseVulnerabilityAssessment` to `DatabaseVulnerabilityAssessment`
  - Method `ManagedDatabaseVulnerabilityAssessmentsOperations.get` changed return type from `_models.DatabaseVulnerabilityAssessment` to `DatabaseVulnerabilityAssessment`
  - Method `ManagedDatabaseVulnerabilityAssessmentsOperations.list_by_database` changed return type from `AsyncIterable[_models.DatabaseVulnerabilityAssessmentListResult]` to `AsyncItemPaged[_models.DatabaseVulnerabilityAssessment]`
  - Method `ManagedDatabasesOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.ManagedDatabase]` to `AsyncLROPoller[ManagedDatabase]`
  - Method `ManagedDatabasesOperations.begin_update` changed return type from `AsyncLROPoller[_models.ManagedDatabase]` to `AsyncLROPoller[ManagedDatabase]`
  - Method `ManagedDatabasesOperations.get` changed return type from `_models.ManagedDatabase` to `ManagedDatabase`
  - Method `ManagedDatabasesOperations.list_by_instance` changed return type from `AsyncIterable[_models.ManagedDatabaseListResult]` to `AsyncItemPaged[_models.ManagedDatabase]`
  - Method `ManagedDatabasesOperations.list_inaccessible_by_instance` changed return type from `AsyncIterable[_models.ManagedDatabaseListResult]` to `AsyncItemPaged[_models.ManagedDatabase]`
  - Method `ManagedInstanceAdministratorsOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.ManagedInstanceAdministrator]` to `AsyncLROPoller[ManagedInstanceAdministrator]`
  - Method `ManagedInstanceAdministratorsOperations.get` changed return type from `_models.ManagedInstanceAdministrator` to `ManagedInstanceAdministrator`
  - Method `ManagedInstanceAdministratorsOperations.list_by_instance` changed return type from `AsyncIterable[_models.ManagedInstanceAdministratorListResult]` to `AsyncItemPaged[_models.ManagedInstanceAdministrator]`
  - Method `ManagedInstanceAzureADOnlyAuthenticationsOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.ManagedInstanceAzureADOnlyAuthentication]` to `AsyncLROPoller[ManagedInstanceAzureADOnlyAuthentication]`
  - Method `ManagedInstanceAzureADOnlyAuthenticationsOperations.get` changed return type from `_models.ManagedInstanceAzureADOnlyAuthentication` to `ManagedInstanceAzureADOnlyAuthentication`
  - Method `ManagedInstanceAzureADOnlyAuthenticationsOperations.list_by_instance` changed return type from `AsyncIterable[_models.ManagedInstanceAzureADOnlyAuthListResult]` to `AsyncItemPaged[_models.ManagedInstanceAzureADOnlyAuthentication]`
  - Method `ManagedInstanceEncryptionProtectorsOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.ManagedInstanceEncryptionProtector]` to `AsyncLROPoller[ManagedInstanceEncryptionProtector]`
  - Method `ManagedInstanceEncryptionProtectorsOperations.get` changed return type from `_models.ManagedInstanceEncryptionProtector` to `ManagedInstanceEncryptionProtector`
  - Method `ManagedInstanceEncryptionProtectorsOperations.list_by_instance` changed return type from `AsyncIterable[_models.ManagedInstanceEncryptionProtectorListResult]` to `AsyncItemPaged[_models.ManagedInstanceEncryptionProtector]`
  - Method `ManagedInstanceKeysOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.ManagedInstanceKey]` to `AsyncLROPoller[ManagedInstanceKey]`
  - Method `ManagedInstanceKeysOperations.get` changed return type from `_models.ManagedInstanceKey` to `ManagedInstanceKey`
  - Method `ManagedInstanceKeysOperations.list_by_instance` changed return type from `AsyncIterable[_models.ManagedInstanceKeyListResult]` to `AsyncItemPaged[_models.ManagedInstanceKey]`
  - Method `ManagedInstanceLongTermRetentionPoliciesOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.ManagedInstanceLongTermRetentionPolicy]` to `AsyncLROPoller[ManagedInstanceLongTermRetentionPolicy]`
  - Method `ManagedInstanceLongTermRetentionPoliciesOperations.get` changed return type from `_models.ManagedInstanceLongTermRetentionPolicy` to `ManagedInstanceLongTermRetentionPolicy`
  - Method `ManagedInstanceLongTermRetentionPoliciesOperations.list_by_database` changed return type from `AsyncIterable[_models.ManagedInstanceLongTermRetentionPolicyListResult]` to `AsyncItemPaged[_models.ManagedInstanceLongTermRetentionPolicy]`
  - Method `ManagedInstanceOperationsOperations.get` changed return type from `_models.ManagedInstanceOperation` to `ManagedInstanceOperation`
  - Method `ManagedInstanceOperationsOperations.list_by_managed_instance` changed return type from `AsyncIterable[_models.ManagedInstanceOperationListResult]` to `AsyncItemPaged[_models.ManagedInstanceOperation]`
  - Method `ManagedInstancePrivateEndpointConnectionsOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.ManagedInstancePrivateEndpointConnection]` to `AsyncLROPoller[ManagedInstancePrivateEndpointConnection]`
  - Method `ManagedInstancePrivateEndpointConnectionsOperations.get` changed return type from `_models.ManagedInstancePrivateEndpointConnection` to `ManagedInstancePrivateEndpointConnection`
  - Method `ManagedInstancePrivateEndpointConnectionsOperations.list_by_managed_instance` changed return type from `AsyncIterable[_models.ManagedInstancePrivateEndpointConnectionListResult]` to `AsyncItemPaged[_models.ManagedInstancePrivateEndpointConnection]`
  - Method `ManagedInstancePrivateLinkResourcesOperations.get` changed return type from `_models.ManagedInstancePrivateLink` to `ManagedInstancePrivateLink`
  - Method `ManagedInstancePrivateLinkResourcesOperations.list_by_managed_instance` changed return type from `AsyncIterable[_models.ManagedInstancePrivateLinkListResult]` to `AsyncItemPaged[_models.ManagedInstancePrivateLink]`
  - Method `ManagedInstanceVulnerabilityAssessmentsOperations.create_or_update` changed return type from `_models.ManagedInstanceVulnerabilityAssessment` to `ManagedInstanceVulnerabilityAssessment`
  - Method `ManagedInstanceVulnerabilityAssessmentsOperations.get` changed return type from `_models.ManagedInstanceVulnerabilityAssessment` to `ManagedInstanceVulnerabilityAssessment`
  - Method `ManagedInstanceVulnerabilityAssessmentsOperations.list_by_instance` changed return type from `AsyncIterable[_models.ManagedInstanceVulnerabilityAssessmentListResult]` to `AsyncItemPaged[_models.ManagedInstanceVulnerabilityAssessment]`
  - Method `ManagedInstancesOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.ManagedInstance]` to `AsyncLROPoller[ManagedInstance]`
  - Method `ManagedInstancesOperations.begin_update` changed return type from `AsyncLROPoller[_models.ManagedInstance]` to `AsyncLROPoller[ManagedInstance]`
  - Method `ManagedInstancesOperations.get` changed return type from `_models.ManagedInstance` to `ManagedInstance`
  - Method `ManagedInstancesOperations.list` changed return type from `AsyncIterable[_models.ManagedInstanceListResult]` to `AsyncItemPaged[_models.ManagedInstance]`
  - Method `ManagedInstancesOperations.list_by_instance_pool` changed return type from `AsyncIterable[_models.ManagedInstanceListResult]` to `AsyncItemPaged[_models.ManagedInstance]`
  - Method `ManagedInstancesOperations.list_by_managed_instance` changed return type from `AsyncIterable[_models.TopQueriesListResult]` to `AsyncItemPaged[_models.TopQueries]`
  - Method `ManagedInstancesOperations.list_by_resource_group` changed return type from `AsyncIterable[_models.ManagedInstanceListResult]` to `AsyncItemPaged[_models.ManagedInstance]`
  - Method `ManagedRestorableDroppedDatabaseBackupShortTermRetentionPoliciesOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.ManagedBackupShortTermRetentionPolicy]` to `AsyncLROPoller[ManagedBackupShortTermRetentionPolicy]`
  - Method `ManagedRestorableDroppedDatabaseBackupShortTermRetentionPoliciesOperations.begin_update` changed return type from `AsyncLROPoller[_models.ManagedBackupShortTermRetentionPolicy]` to `AsyncLROPoller[ManagedBackupShortTermRetentionPolicy]`
  - Method `ManagedRestorableDroppedDatabaseBackupShortTermRetentionPoliciesOperations.get` changed return type from `_models.ManagedBackupShortTermRetentionPolicy` to `ManagedBackupShortTermRetentionPolicy`
  - Method `ManagedRestorableDroppedDatabaseBackupShortTermRetentionPoliciesOperations.list_by_restorable_dropped_database` changed return type from `AsyncIterable[_models.ManagedBackupShortTermRetentionPolicyListResult]` to `AsyncItemPaged[_models.ManagedBackupShortTermRetentionPolicy]`
  - Method `ManagedServerSecurityAlertPoliciesOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.ManagedServerSecurityAlertPolicy]` to `AsyncLROPoller[ManagedServerSecurityAlertPolicy]`
  - Method `ManagedServerSecurityAlertPoliciesOperations.get` changed return type from `_models.ManagedServerSecurityAlertPolicy` to `ManagedServerSecurityAlertPolicy`
  - Method `ManagedServerSecurityAlertPoliciesOperations.list_by_instance` changed return type from `AsyncIterable[_models.ManagedServerSecurityAlertPolicyListResult]` to `AsyncItemPaged[_models.ManagedServerSecurityAlertPolicy]`
  - Method `Operations.list` changed return type from `AsyncIterable[_models.OperationListResult]` to `AsyncItemPaged[_models.Operation]`
  - Method `OutboundFirewallRulesOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.OutboundFirewallRule]` to `AsyncLROPoller[OutboundFirewallRule]`
  - Method `OutboundFirewallRulesOperations.get` changed return type from `_models.OutboundFirewallRule` to `OutboundFirewallRule`
  - Method `OutboundFirewallRulesOperations.list_by_server` changed return type from `AsyncIterable[_models.OutboundFirewallRuleListResult]` to `AsyncItemPaged[_models.OutboundFirewallRule]`
  - Method `PrivateEndpointConnectionsOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.PrivateEndpointConnection]` to `AsyncLROPoller[PrivateEndpointConnection]`
  - Method `PrivateEndpointConnectionsOperations.get` changed return type from `_models.PrivateEndpointConnection` to `PrivateEndpointConnection`
  - Method `PrivateEndpointConnectionsOperations.list_by_server` changed return type from `AsyncIterable[_models.PrivateEndpointConnectionListResult]` to `AsyncItemPaged[_models.PrivateEndpointConnection]`
  - Method `PrivateLinkResourcesOperations.get` changed return type from `_models.PrivateLinkResource` to `PrivateLinkResource`
  - Method `PrivateLinkResourcesOperations.list_by_server` changed return type from `AsyncIterable[_models.PrivateLinkResourceListResult]` to `AsyncItemPaged[_models.PrivateLinkResource]`
  - Method `RecoverableDatabasesOperations.get` changed return type from `_models.RecoverableDatabase` to `RecoverableDatabase`
  - Method `RecoverableDatabasesOperations.list_by_server` changed return type from `AsyncIterable[_models.RecoverableDatabaseListResult]` to `AsyncItemPaged[_models.RecoverableDatabase]`
  - Method `RecoverableManagedDatabasesOperations.get` changed return type from `_models.RecoverableManagedDatabase` to `RecoverableManagedDatabase`
  - Method `RecoverableManagedDatabasesOperations.list_by_instance` changed return type from `AsyncIterable[_models.RecoverableManagedDatabaseListResult]` to `AsyncItemPaged[_models.RecoverableManagedDatabase]`
  - Method `ReplicationLinksOperations.begin_failover` changed return type from `AsyncLROPoller[None]` to `AsyncLROPoller[ReplicationLink]`
  - Method `ReplicationLinksOperations.begin_failover_allow_data_loss` changed return type from `AsyncLROPoller[None]` to `AsyncLROPoller[ReplicationLink]`
  - Method `ReplicationLinksOperations.get` changed return type from `_models.ReplicationLink` to `ReplicationLink`
  - Method `ReplicationLinksOperations.list_by_database` changed return type from `AsyncIterable[_models.ReplicationLinkListResult]` to `AsyncItemPaged[_models.ReplicationLink]`
  - Method `ReplicationLinksOperations.list_by_server` changed return type from `AsyncIterable[_models.ReplicationLinkListResult]` to `AsyncItemPaged[_models.ReplicationLink]`
  - Method `RestorableDroppedDatabasesOperations.get` changed return type from `_models.RestorableDroppedDatabase` to `RestorableDroppedDatabase`
  - Method `RestorableDroppedDatabasesOperations.list_by_server` changed return type from `AsyncIterable[_models.RestorableDroppedDatabaseListResult]` to `AsyncItemPaged[_models.RestorableDroppedDatabase]`
  - Method `RestorableDroppedManagedDatabasesOperations.get` changed return type from `_models.RestorableDroppedManagedDatabase` to `RestorableDroppedManagedDatabase`
  - Method `RestorableDroppedManagedDatabasesOperations.list_by_instance` changed return type from `AsyncIterable[_models.RestorableDroppedManagedDatabaseListResult]` to `AsyncItemPaged[_models.RestorableDroppedManagedDatabase]`
  - Method `RestorePointsOperations.begin_create` changed return type from `AsyncLROPoller[_models.RestorePoint]` to `AsyncLROPoller[RestorePoint]`
  - Method `RestorePointsOperations.get` changed return type from `_models.RestorePoint` to `RestorePoint`
  - Method `RestorePointsOperations.list_by_database` changed return type from `AsyncIterable[_models.RestorePointListResult]` to `AsyncItemPaged[_models.RestorePoint]`
  - Method `SensitivityLabelsOperations.create_or_update` changed return type from `_models.SensitivityLabel` to `SensitivityLabel`
  - Method `SensitivityLabelsOperations.get` changed return type from `_models.SensitivityLabel` to `SensitivityLabel`
  - Method `SensitivityLabelsOperations.list_current_by_database` changed return type from `AsyncIterable[_models.SensitivityLabelListResult]` to `AsyncItemPaged[_models.SensitivityLabel]`
  - Method `SensitivityLabelsOperations.list_recommended_by_database` changed return type from `AsyncIterable[_models.SensitivityLabelListResult]` to `AsyncItemPaged[_models.SensitivityLabel]`
  - Method `ServerAdvisorsOperations.get` changed return type from `_models.Advisor` to `Advisor`
  - Method `ServerAdvisorsOperations.list_by_server` changed return type from `List[_models.Advisor]` to `List[Advisor]`
  - Method `ServerAdvisorsOperations.update` changed return type from `_models.Advisor` to `Advisor`
  - Method `ServerAutomaticTuningOperations.get` changed return type from `_models.ServerAutomaticTuning` to `ServerAutomaticTuning`
  - Method `ServerAutomaticTuningOperations.update` changed return type from `_models.ServerAutomaticTuning` to `ServerAutomaticTuning`
  - Method `ServerAzureADAdministratorsOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.ServerAzureADAdministrator]` to `AsyncLROPoller[ServerAzureADAdministrator]`
  - Method `ServerAzureADAdministratorsOperations.get` changed return type from `_models.ServerAzureADAdministrator` to `ServerAzureADAdministrator`
  - Method `ServerAzureADAdministratorsOperations.list_by_server` changed return type from `AsyncIterable[_models.AdministratorListResult]` to `AsyncItemPaged[_models.ServerAzureADAdministrator]`
  - Method `ServerAzureADOnlyAuthenticationsOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.ServerAzureADOnlyAuthentication]` to `AsyncLROPoller[ServerAzureADOnlyAuthentication]`
  - Method `ServerAzureADOnlyAuthenticationsOperations.get` changed return type from `_models.ServerAzureADOnlyAuthentication` to `ServerAzureADOnlyAuthentication`
  - Method `ServerAzureADOnlyAuthenticationsOperations.list_by_server` changed return type from `AsyncIterable[_models.AzureADOnlyAuthListResult]` to `AsyncItemPaged[_models.ServerAzureADOnlyAuthentication]`
  - Method `ServerBlobAuditingPoliciesOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.ServerBlobAuditingPolicy]` to `AsyncLROPoller[ServerBlobAuditingPolicy]`
  - Method `ServerBlobAuditingPoliciesOperations.get` changed return type from `_models.ServerBlobAuditingPolicy` to `ServerBlobAuditingPolicy`
  - Method `ServerBlobAuditingPoliciesOperations.list_by_server` changed return type from `AsyncIterable[_models.ServerBlobAuditingPolicyListResult]` to `AsyncItemPaged[_models.ServerBlobAuditingPolicy]`
  - Method `ServerConnectionPoliciesOperations.get` changed return type from `_models.ServerConnectionPolicy` to `ServerConnectionPolicy`
  - Method `ServerDevOpsAuditSettingsOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.ServerDevOpsAuditingSettings]` to `AsyncLROPoller[ServerDevOpsAuditingSettings]`
  - Method `ServerDevOpsAuditSettingsOperations.get` changed return type from `_models.ServerDevOpsAuditingSettings` to `ServerDevOpsAuditingSettings`
  - Method `ServerDevOpsAuditSettingsOperations.list_by_server` changed return type from `AsyncIterable[_models.ServerDevOpsAuditSettingsListResult]` to `AsyncItemPaged[_models.ServerDevOpsAuditingSettings]`
  - Method `ServerDnsAliasesOperations.begin_acquire` changed return type from `AsyncLROPoller[_models.ServerDnsAlias]` to `AsyncLROPoller[ServerDnsAlias]`
  - Method `ServerDnsAliasesOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.ServerDnsAlias]` to `AsyncLROPoller[ServerDnsAlias]`
  - Method `ServerDnsAliasesOperations.get` changed return type from `_models.ServerDnsAlias` to `ServerDnsAlias`
  - Method `ServerDnsAliasesOperations.list_by_server` changed return type from `AsyncIterable[_models.ServerDnsAliasListResult]` to `AsyncItemPaged[_models.ServerDnsAlias]`
  - Method `ServerKeysOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.ServerKey]` to `AsyncLROPoller[ServerKey]`
  - Method `ServerKeysOperations.get` changed return type from `_models.ServerKey` to `ServerKey`
  - Method `ServerKeysOperations.list_by_server` changed return type from `AsyncIterable[_models.ServerKeyListResult]` to `AsyncItemPaged[_models.ServerKey]`
  - Method `ServerOperationsOperations.list_by_server` changed return type from `AsyncIterable[_models.ServerOperationListResult]` to `AsyncItemPaged[_models.ServerOperation]`
  - Method `ServerSecurityAlertPoliciesOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.ServerSecurityAlertPolicy]` to `AsyncLROPoller[ServerSecurityAlertPolicy]`
  - Method `ServerSecurityAlertPoliciesOperations.get` changed return type from `_models.ServerSecurityAlertPolicy` to `ServerSecurityAlertPolicy`
  - Method `ServerSecurityAlertPoliciesOperations.list_by_server` changed return type from `AsyncIterable[_models.LogicalServerSecurityAlertPolicyListResult]` to `AsyncItemPaged[_models.ServerSecurityAlertPolicy]`
  - Method `ServerTrustGroupsOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.ServerTrustGroup]` to `AsyncLROPoller[ServerTrustGroup]`
  - Method `ServerTrustGroupsOperations.get` changed return type from `_models.ServerTrustGroup` to `ServerTrustGroup`
  - Method `ServerTrustGroupsOperations.list_by_instance` changed return type from `AsyncIterable[_models.ServerTrustGroupListResult]` to `AsyncItemPaged[_models.ServerTrustGroup]`
  - Method `ServerTrustGroupsOperations.list_by_location` changed return type from `AsyncIterable[_models.ServerTrustGroupListResult]` to `AsyncItemPaged[_models.ServerTrustGroup]`
  - Method `ServerUsagesOperations.list_by_server` changed return type from `AsyncIterable[_models.ServerUsageListResult]` to `AsyncItemPaged[_models.ServerUsage]`
  - Method `ServerVulnerabilityAssessmentsOperations.create_or_update` changed return type from `_models.ServerVulnerabilityAssessment` to `ServerVulnerabilityAssessment`
  - Method `ServerVulnerabilityAssessmentsOperations.get` changed return type from `_models.ServerVulnerabilityAssessment` to `ServerVulnerabilityAssessment`
  - Method `ServerVulnerabilityAssessmentsOperations.list_by_server` changed return type from `AsyncIterable[_models.ServerVulnerabilityAssessmentListResult]` to `AsyncItemPaged[_models.ServerVulnerabilityAssessment]`
  - Method `ServersOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.Server]` to `AsyncLROPoller[Server]`
  - Method `ServersOperations.begin_import_database` changed return type from `AsyncLROPoller[_models.ImportExportOperationResult]` to `AsyncLROPoller[ImportExportOperationResult]`
  - Method `ServersOperations.begin_update` changed return type from `AsyncLROPoller[_models.Server]` to `AsyncLROPoller[Server]`
  - Method `ServersOperations.check_name_availability` changed return type from `_models.CheckNameAvailabilityResponse` to `CheckNameAvailabilityResponse`
  - Method `ServersOperations.get` changed return type from `_models.Server` to `Server`
  - Method `ServersOperations.list` changed return type from `AsyncIterable[_models.ServerListResult]` to `AsyncItemPaged[_models.Server]`
  - Method `ServersOperations.list_by_resource_group` changed return type from `AsyncIterable[_models.ServerListResult]` to `AsyncItemPaged[_models.Server]`
  - Method `SqlAgentOperations.create_or_update` changed return type from `_models.SqlAgentConfiguration` to `SqlAgentConfiguration`
  - Method `SqlAgentOperations.get` changed return type from `_models.SqlAgentConfiguration` to `SqlAgentConfiguration`
  - Method `SubscriptionUsagesOperations.get` changed return type from `_models.SubscriptionUsage` to `SubscriptionUsage`
  - Method `SubscriptionUsagesOperations.list_by_location` changed return type from `AsyncIterable[_models.SubscriptionUsageListResult]` to `AsyncItemPaged[_models.SubscriptionUsage]`
  - Method `SyncAgentsOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.SyncAgent]` to `AsyncLROPoller[SyncAgent]`
  - Method `SyncAgentsOperations.generate_key` changed return type from `_models.SyncAgentKeyProperties` to `SyncAgentKeyProperties`
  - Method `SyncAgentsOperations.get` changed return type from `_models.SyncAgent` to `SyncAgent`
  - Method `SyncAgentsOperations.list_by_server` changed return type from `AsyncIterable[_models.SyncAgentListResult]` to `AsyncItemPaged[_models.SyncAgent]`
  - Method `SyncAgentsOperations.list_linked_databases` changed return type from `AsyncIterable[_models.SyncAgentLinkedDatabaseListResult]` to `AsyncItemPaged[_models.SyncAgentLinkedDatabase]`
  - Method `SyncGroupsOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.SyncGroup]` to `AsyncLROPoller[SyncGroup]`
  - Method `SyncGroupsOperations.begin_update` changed return type from `AsyncLROPoller[_models.SyncGroup]` to `AsyncLROPoller[SyncGroup]`
  - Method `SyncGroupsOperations.get` changed return type from `_models.SyncGroup` to `SyncGroup`
  - Method `SyncGroupsOperations.list_by_database` changed return type from `AsyncIterable[_models.SyncGroupListResult]` to `AsyncItemPaged[_models.SyncGroup]`
  - Method `SyncGroupsOperations.list_hub_schemas` changed return type from `AsyncIterable[_models.SyncFullSchemaPropertiesListResult]` to `AsyncItemPaged[_models.SyncFullSchemaProperties]`
  - Method `SyncGroupsOperations.list_logs` changed return type from `AsyncIterable[_models.SyncGroupLogListResult]` to `AsyncItemPaged[_models.SyncGroupLogProperties]`
  - Method `SyncGroupsOperations.list_sync_database_ids` changed return type from `AsyncIterable[_models.SyncDatabaseIdListResult]` to `AsyncItemPaged[_models.SyncDatabaseIdProperties]`
  - Method `SyncMembersOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.SyncMember]` to `AsyncLROPoller[SyncMember]`
  - Method `SyncMembersOperations.begin_update` changed return type from `AsyncLROPoller[_models.SyncMember]` to `AsyncLROPoller[SyncMember]`
  - Method `SyncMembersOperations.get` changed return type from `_models.SyncMember` to `SyncMember`
  - Method `SyncMembersOperations.list_by_sync_group` changed return type from `AsyncIterable[_models.SyncMemberListResult]` to `AsyncItemPaged[_models.SyncMember]`
  - Method `SyncMembersOperations.list_member_schemas` changed return type from `AsyncIterable[_models.SyncFullSchemaPropertiesListResult]` to `AsyncItemPaged[_models.SyncFullSchemaProperties]`
  - Method `TimeZonesOperations.get` changed return type from `_models.TimeZone` to `TimeZone`
  - Method `TimeZonesOperations.list_by_location` changed return type from `AsyncIterable[_models.TimeZoneListResult]` to `AsyncItemPaged[_models.TimeZone]`
  - Method `TransparentDataEncryptionsOperations.get` changed return type from `_models.TransparentDataEncryption` to `LogicalDatabaseTransparentDataEncryption`
  - Method `UsagesOperations.list_by_instance_pool` changed return type from `AsyncIterable[_models.UsageListResult]` to `AsyncItemPaged[_models.Usage]`
  - Method `VirtualClustersOperations.begin_update` changed return type from `AsyncLROPoller[_models.VirtualCluster]` to `AsyncLROPoller[VirtualCluster]`
  - Method `VirtualClustersOperations.get` changed return type from `_models.VirtualCluster` to `VirtualCluster`
  - Method `VirtualClustersOperations.list` changed return type from `AsyncIterable[_models.VirtualClusterListResult]` to `AsyncItemPaged[_models.VirtualCluster]`
  - Method `VirtualClustersOperations.list_by_resource_group` changed return type from `AsyncIterable[_models.VirtualClusterListResult]` to `AsyncItemPaged[_models.VirtualCluster]`
  - Method `VirtualNetworkRulesOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.VirtualNetworkRule]` to `AsyncLROPoller[VirtualNetworkRule]`
  - Method `VirtualNetworkRulesOperations.get` changed return type from `_models.VirtualNetworkRule` to `VirtualNetworkRule`
  - Method `VirtualNetworkRulesOperations.list_by_server` changed return type from `AsyncIterable[_models.VirtualNetworkRuleListResult]` to `AsyncItemPaged[_models.VirtualNetworkRule]`
  - Method `WorkloadClassifiersOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.WorkloadClassifier]` to `AsyncLROPoller[WorkloadClassifier]`
  - Method `WorkloadClassifiersOperations.get` changed return type from `_models.WorkloadClassifier` to `WorkloadClassifier`
  - Method `WorkloadClassifiersOperations.list_by_workload_group` changed return type from `AsyncIterable[_models.WorkloadClassifierListResult]` to `AsyncItemPaged[_models.WorkloadClassifier]`
  - Method `WorkloadGroupsOperations.begin_create_or_update` changed return type from `AsyncLROPoller[_models.WorkloadGroup]` to `AsyncLROPoller[WorkloadGroup]`
  - Method `WorkloadGroupsOperations.get` changed return type from `_models.WorkloadGroup` to `WorkloadGroup`
  - Method `WorkloadGroupsOperations.list_by_database` changed return type from `AsyncIterable[_models.WorkloadGroupListResult]` to `AsyncItemPaged[_models.WorkloadGroup]`
  - Method `TransparentDataEncryptionsOperations.get` re-ordered its parameters from `['self', 'resource_group_name', 'server_name', 'database_name', 'transparent_data_encryption_name', 'kwargs']` to `['self', 'resource_group_name', 'server_name', 'database_name', 'tde_name', 'kwargs']`
  - Method `MaintenanceWindowsOperations.create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'server_name', 'database_name', 'maintenance_window_name', 'parameters', 'kwargs']` to `['self', 'resource_group_name', 'server_name', 'database_name', 'parameters', 'maintenance_window_name', 'kwargs']`

### Other Changes

  - Deleted model `AdministratorListResult`/`AzureADOnlyAuthListResult`/`BackupShortTermRetentionPolicyListResult`/`DataMaskingRuleListResult`/`DataWarehouseUserActivitiesListResult`/`DatabaseBlobAuditingPolicyListResult`/`DatabaseColumnListResult`/`DatabaseListResult`/`DatabaseOperationListResult`/`DatabaseSchemaListResult`/`DatabaseSecurityAlertListResult`/`DatabaseTableListResult`/`DatabaseUsageListResult`/`DatabaseVulnerabilityAssessmentListResult`/`DeletedServerListResult`/`ElasticPoolActivityListResult`/`ElasticPoolDatabaseActivityListResult`/`ElasticPoolListResult`/`ElasticPoolOperationListResult`/`EncryptionProtectorListResult`/`ExtendedDatabaseBlobAuditingPolicyListResult`/`ExtendedServerBlobAuditingPolicyListResult`/`FailoverGroupListResult`/`FirewallRuleListResult`/`GeoBackupPolicyListResult`/`ImportExportExtensionsOperationListResult`/`InstanceFailoverGroupListResult`/`InstancePoolListResult`/`JobAgentListResult`/`JobCredentialListResult`/`JobExecutionListResult`/`JobListResult`/`JobStepListResult`/`JobTargetGroupListResult`/`JobVersionListResult`/`LedgerDigestUploadsListResult`/`LogicalServerSecurityAlertPolicyListResult`/`LongTermRetentionBackupListResult`/`LongTermRetentionPolicyListResult`/`ManagedBackupShortTermRetentionPolicyListResult`/`ManagedDatabaseListResult`/`ManagedDatabaseSecurityAlertPolicyListResult`/`ManagedInstanceAdministratorListResult`/`ManagedInstanceAzureADOnlyAuthListResult`/`ManagedInstanceEncryptionProtectorListResult`/`ManagedInstanceKeyListResult`/`ManagedInstanceListResult`/`ManagedInstanceLongTermRetentionBackupListResult`/`ManagedInstanceLongTermRetentionPolicyListResult`/`ManagedInstanceOperationListResult`/`ManagedInstancePrivateEndpointConnectionListResult`/`ManagedInstancePrivateLinkListResult`/`ManagedInstanceVulnerabilityAssessmentListResult`/`ManagedServerSecurityAlertPolicyListResult`/`ManagedTransparentDataEncryptionListResult`/`MetricDefinitionListResult`/`MetricListResult`/`OperationListResult`/`OperationsHealthListResult`/`OutboundFirewallRuleListResult`/`PrivateEndpointConnectionListResult`/`PrivateLinkResourceListResult`/`RecoverableDatabaseListResult`/`RecoverableManagedDatabaseListResult`/`ReplicationLinkListResult`/`RestorableDroppedDatabaseListResult`/`RestorableDroppedManagedDatabaseListResult`/`RestorePointListResult`/`SecurityEventCollection`/`SensitivityLabelListResult`/`ServerBlobAuditingPolicyListResult`/`ServerCommunicationLinkListResult`/`ServerDevOpsAuditSettingsListResult`/`ServerDnsAliasListResult`/`ServerKeyListResult`/`ServerListResult`/`ServerOperationListResult`/`ServerTrustGroupListResult`/`ServerUsageListResult`/`ServerVulnerabilityAssessmentListResult`/`ServiceObjectiveListResult`/`SubscriptionUsageListResult`/`SyncAgentLinkedDatabaseListResult`/`SyncAgentListResult`/`SyncDatabaseIdListResult`/`SyncFullSchemaPropertiesListResult`/`SyncGroupListResult`/`SyncGroupLogListResult`/`SyncMemberListResult`/`TimeZoneListResult`/`TopQueriesListResult`/`TransparentDataEncryptionActivityListResult`/`UsageListResult`/`VirtualClusterListResult`/`VirtualNetworkRuleListResult`/`VulnerabilityAssessmentScanRecordListResult`/`WorkloadClassifierListResult`/`WorkloadGroupListResult` which actually were not used by SDK users

## 4.0.0b25 (2026-06-02)

### Features Added

  - Client `SqlManagementClient` added method `send_request`
  - Client `SqlManagementClient` added operation group `instance_pool_operations`
  - Client `SqlManagementClient` added operation group `network_security_perimeter_configurations`
  - Model `Advisor` added property `system_data`
  - Model `BackupShortTermRetentionPolicy` added property `system_data`
  - Enum `CapabilityGroup` added member `SUPPORTED_JOB_AGENT_VERSIONS`
  - Model `CheckNameAvailabilityRequest` added property `type`
  - Model `DataMaskingPolicy` added property `system_data`
  - Model `DataMaskingRule` added property `system_data`
  - Model `DataWarehouseUserActivities` added property `system_data`
  - Model `Database` added property `system_data`
  - Model `DatabaseAutomaticTuning` added property `system_data`
  - Model `DatabaseBlobAuditingPolicy` added property `system_data`
  - Model `DatabaseColumn` added property `system_data`
  - Model `DatabaseExtensions` added property `system_data`
  - Model `DatabaseKey` added property `key_version`
  - Model `DatabaseOperation` added property `system_data`
  - Model `DatabaseSchema` added property `system_data`
  - Model `DatabaseTable` added property `system_data`
  - Model `DatabaseUsage` added property `system_data`
  - Model `DatabaseVulnerabilityAssessment` added property `system_data`
  - Model `DatabaseVulnerabilityAssessmentRuleBaseline` added property `system_data`
  - Model `DatabaseVulnerabilityAssessmentScansExport` added property `system_data`
  - Model `DeletedServer` added property `system_data`
  - Model `DistributedAvailabilityGroup` added property `system_data`
  - Model `EditionCapability` added property `zone_pinning`
  - Model `ElasticPool` added property `system_data`
  - Model `ElasticPoolEditionCapability` added property `zone_pinning`
  - Model `ElasticPoolOperation` added property `system_data`
  - Model `ElasticPoolPerDatabaseSettings` added property `auto_pause_delay`
  - Model `ElasticPoolPerformanceLevelCapability` added property `supported_min_capacities`
  - Model `ElasticPoolPerformanceLevelCapability` added property `supported_auto_pause_delay`
  - Model `ElasticPoolPerformanceLevelCapability` added property `supported_per_database_auto_pause_delay`
  - Model `ElasticPoolPerformanceLevelCapability` added property `supported_zones`
  - Model `EncryptionProtector` added property `system_data`
  - Model `EndpointCertificate` added property `system_data`
  - Model `ExtendedDatabaseBlobAuditingPolicy` added property `system_data`
  - Model `ExtendedServerBlobAuditingPolicy` added property `system_data`
  - Model `FailoverGroup` added property `system_data`
  - Model `GeoBackupPolicy` added property `system_data`
  - Model `ImportExportExtensionsOperationResult` added property `system_data`
  - Model `ImportExportOperationResult` added property `system_data`
  - Model `InstanceFailoverGroup` added property `system_data`
  - Model `InstancePool` added property `system_data`
  - Model `Job` added property `system_data`
  - Model `JobAgent` added property `identity`
  - Model `JobAgent` added property `system_data`
  - Model `JobAgentUpdate` added property `identity`
  - Model `JobAgentUpdate` added property `sku`
  - Model `JobCredential` added property `system_data`
  - Model `JobExecution` added property `system_data`
  - Model `JobPrivateEndpoint` added property `system_data`
  - Model `JobStep` added property `system_data`
  - Model `JobTargetGroup` added property `system_data`
  - Model `JobVersion` added property `system_data`
  - Model `LedgerDigestUploads` added property `system_data`
  - Model `LocationCapabilities` added property `supported_job_agent_versions`
  - Model `LocationCapabilities` added property `is_zone_resilient_provisioning_allowed`
  - Model `LogicalDatabaseTransparentDataEncryption` added property `system_data`
  - Model `LongTermRetentionBackup` added property `system_data`
  - Model `LongTermRetentionBackupOperationResult` added property `system_data`
  - Model `LongTermRetentionPolicy` added property `system_data`
  - Model `MaintenanceWindowOptions` added property `system_data`
  - Model `MaintenanceWindows` added property `system_data`
  - Model `ManagedBackupShortTermRetentionPolicy` added property `system_data`
  - Model `ManagedDatabase` added property `system_data`
  - Model `ManagedDatabaseMoveOperationResult` added property `system_data`
  - Model `ManagedDatabaseRestoreDetailsResult` added property `system_data`
  - Model `ManagedDatabaseSecurityAlertPolicy` added property `system_data`
  - Model `ManagedInstance` added property `system_data`
  - Model `ManagedInstanceAdministrator` added property `system_data`
  - Model `ManagedInstanceAzureADOnlyAuthentication` added property `system_data`
  - Enum `ManagedInstanceDatabaseFormat` added member `SQL_SERVER2025`
  - Model `ManagedInstanceDtc` added property `system_data`
  - Model `ManagedInstanceEditionCapability` added property `is_general_purpose_v2`
  - Model `ManagedInstanceEncryptionProtector` added property `system_data`
  - Model `ManagedInstanceFamilyCapability` added property `zone_redundant`
  - Model `ManagedInstanceKey` added property `system_data`
  - Model `ManagedInstanceLongTermRetentionBackup` added property `system_data`
  - Model `ManagedInstanceLongTermRetentionPolicy` added property `system_data`
  - Model `ManagedInstanceOperation` added property `system_data`
  - Model `ManagedInstancePrivateEndpointConnection` added property `system_data`
  - Model `ManagedInstancePrivateLink` added property `system_data`
  - Model `ManagedInstancePrivateLinkProperties` added property `required_zone_names`
  - Model `ManagedInstanceQuery` added property `system_data`
  - Model `ManagedInstanceVcoresCapability` added property `supported_memory_sizes_in_gb`
  - Model `ManagedInstanceVcoresCapability` added property `supported_memory_limits_mb`
  - Model `ManagedInstanceVcoresCapability` added property `included_storage_i_ops`
  - Model `ManagedInstanceVcoresCapability` added property `supported_storage_i_ops`
  - Model `ManagedInstanceVcoresCapability` added property `iops_min_value_override_factor_per_selected_storage_gb`
  - Model `ManagedInstanceVcoresCapability` added property `iops_included_value_override_factor_per_selected_storage_gb`
  - Model `ManagedInstanceVcoresCapability` added property `included_storage_throughput_m_bps`
  - Model `ManagedInstanceVcoresCapability` added property `supported_storage_throughput_m_bps`
  - Model `ManagedInstanceVcoresCapability` added property `throughput_m_bps_min_value_override_factor_per_selected_storage_gb`
  - Model `ManagedInstanceVcoresCapability` added property `throughput_m_bps_included_value_override_factor_per_selected_storage_gb`
  - Model `ManagedInstanceVulnerabilityAssessment` added property `system_data`
  - Model `ManagedLedgerDigestUploads` added property `system_data`
  - Model `ManagedServerDnsAlias` added property `system_data`
  - Model `ManagedTransparentDataEncryption` added property `system_data`
  - Enum `OperationMode` added member `EXPORT`
  - Enum `OperationMode` added member `IMPORT`
  - Model `OutboundFirewallRule` added property `system_data`
  - Model `PrivateEndpointConnection` added property `system_data`
  - Model `PrivateLinkResource` added property `system_data`
  - Model `ProxyResource` added property `system_data`
  - Model `QueryStatistics` added property `system_data`
  - Model `RecommendedAction` added property `system_data`
  - Model `RecommendedSensitivityLabelUpdate` added property `system_data`
  - Model `RecoverableDatabase` added property `system_data`
  - Model `RecoverableManagedDatabase` added property `system_data`
  - Model `RefreshExternalGovernanceStatusOperationResult` added property `system_data`
  - Model `RefreshExternalGovernanceStatusOperationResultMI` added property `system_data`
  - Model `ReplicationLink` added property `system_data`
  - Model `ReplicationLinkUpdate` added property `system_data`
  - Model `Resource` added property `system_data`
  - Model `RestorableDroppedDatabase` added property `system_data`
  - Model `RestorableDroppedManagedDatabase` added property `system_data`
  - Model `RestorePoint` added property `system_data`
  - Model `SecurityEvent` added property `system_data`
  - Model `SensitivityLabel` added property `system_data`
  - Model `SensitivityLabelUpdate` added property `system_data`
  - Model `Server` added property `system_data`
  - Model `ServerAutomaticTuning` added property `system_data`
  - Model `ServerAzureADAdministrator` added property `system_data`
  - Model `ServerAzureADOnlyAuthentication` added property `system_data`
  - Model `ServerBlobAuditingPolicy` added property `system_data`
  - Model `ServerConfigurationOption` added property `system_data`
  - Model `ServerConnectionPolicy` added property `system_data`
  - Model `ServerDnsAlias` added property `system_data`
  - Model `ServerKey` added property `system_data`
  - Model `ServerOperation` added property `system_data`
  - Model `ServerTrustCertificate` added property `system_data`
  - Model `ServerTrustGroup` added property `system_data`
  - Model `ServerUsage` added property `id`
  - Model `ServerUsage` added property `type`
  - Model `ServerUsage` added property `system_data`
  - Model `ServerVulnerabilityAssessment` added property `system_data`
  - Model `ServiceObjectiveCapability` added property `zone_pinning`
  - Model `ServiceObjectiveCapability` added property `supported_zones`
  - Model `ServiceObjectiveCapability` added property `supported_free_limit_exhaustion_behaviors`
  - Model `SqlAgentConfiguration` added property `system_data`
  - Enum `StorageCapabilityStorageAccountType` added member `GZRS`
  - Model `SubscriptionUsage` added property `system_data`
  - Model `SynapseLinkWorkspace` added property `system_data`
  - Model `SyncAgent` added property `system_data`
  - Model `SyncAgentLinkedDatabase` added property `system_data`
  - Model `SyncGroup` added property `system_data`
  - Model `SyncMember` added property `system_data`
  - Model `TdeCertificate` added property `system_data`
  - Model `TimeZone` added property `system_data`
  - Model `TrackedResource` added property `system_data`
  - Model `UpdateVirtualClusterDnsServersOperation` added property `system_data`
  - Model `VirtualCluster` added property `system_data`
  - Model `VirtualNetworkRule` added property `system_data`
  - Model `VulnerabilityAssessmentScanRecord` added property `system_data`
  - Model `WorkloadClassifier` added property `system_data`
  - Model `WorkloadGroup` added property `system_data`
  - Added enum `CheckNameAvailabilityResourceType`
  - Added enum `ClientClassificationSource`
  - Added enum `ErrorType`
  - Added model `FreeLimitExhaustionBehaviorCapability`
  - Added enum `InaccessibilityReason`
  - Added model `InstancePoolOperation`
  - Added model `InstancePoolOperationProperties`
  - Added model `JobAgentEditionCapability`
  - Added model `JobAgentIdentity`
  - Added enum `JobAgentIdentityType`
  - Added model `JobAgentServiceLevelObjectiveCapability`
  - Added model `JobAgentUserAssignedIdentity`
  - Added model `JobAgentVersionCapability`
  - Added model `ManagedDatabaseExtendedAccessibilityInfo`
  - Added model `ManagedInstanceValidateAzureKeyVaultEncryptionKeyRequest`
  - Added model `MaxLimitRangeCapability`
  - Added model `NSPConfigAccessRule`
  - Added model `NSPConfigAccessRuleProperties`
  - Added model `NSPConfigAssociation`
  - Added model `NSPConfigNetworkSecurityPerimeterRule`
  - Added model `NSPConfigPerimeter`
  - Added model `NSPConfigProfile`
  - Added model `NSPProvisioningIssue`
  - Added model `NSPProvisioningIssueProperties`
  - Added model `NetworkSecurityPerimeterConfiguration`
  - Added model `NetworkSecurityPerimeterConfigurationProperties`
  - Added model `PerDatabaseAutoPauseDelayTimeRange`
  - Added enum `PricingModel`
  - Added enum `TransparentDataEncryptionScanState`
  - Added model `UpsertManagedServerOperationStepWithEstimatesAndDuration`
  - Added enum `UpsertManagedServerOperationStepWithEstimatesAndDurationStatus`
  - Added model `ZonePinningCapability`
  - Operation group `GeoBackupPoliciesOperations` added method `list`
  - Operation group `LongTermRetentionManagedInstanceBackupsOperations` added parameter `skip` in method `list_by_location`
  - Operation group `LongTermRetentionManagedInstanceBackupsOperations` added parameter `top` in method `list_by_location`
  - Operation group `LongTermRetentionManagedInstanceBackupsOperations` added parameter `filter` in method `list_by_location`
  - Operation group `LongTermRetentionManagedInstanceBackupsOperations` added parameter `skip` in method `list_by_resource_group_location`
  - Operation group `LongTermRetentionManagedInstanceBackupsOperations` added parameter `top` in method `list_by_resource_group_location`
  - Operation group `LongTermRetentionManagedInstanceBackupsOperations` added parameter `filter` in method `list_by_resource_group_location`
  - Operation group `ManagedDatabaseSensitivityLabelsOperations` added method `list_by_database`
  - Operation group `ManagedDatabasesOperations` added method `begin_reevaluate_inaccessible_database_state`
  - Operation group `ManagedInstanceLongTermRetentionPoliciesOperations` added method `begin_delete`
  - Operation group `ManagedInstancesOperations` added method `begin_reevaluate_inaccessible_database_state`
  - Operation group `ManagedInstancesOperations` added method `begin_validate_azure_key_vault_encryption_key`
  - Operation group `SensitivityLabelsOperations` added method `list_by_database`
  - Operation group `TransparentDataEncryptionsOperations` added method `begin_resume`
  - Operation group `TransparentDataEncryptionsOperations` added method `begin_suspend`
  - Operation group `VirtualClustersOperations` added method `begin_create_or_update`
  - Added operation group `InstancePoolOperationsOperations`
  - Added operation group `NetworkSecurityPerimeterConfigurationsOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Deleted or renamed client operation group `SqlManagementClient.server_communication_links`
  - Deleted or renamed client operation group `SqlManagementClient.service_objectives`
  - Deleted or renamed client operation group `SqlManagementClient.elastic_pool_activities`
  - Deleted or renamed client operation group `SqlManagementClient.elastic_pool_database_activities`
  - Model `CopyLongTermRetentionBackupParameters` moved instance variable `target_subscription_id`, `target_resource_group`, `target_server_resource_id`, `target_server_fully_qualified_domain_name`, `target_database_name` and `target_backup_storage_redundancy` under property `properties` whose type is `CopyLongTermRetentionBackupParametersProperties`
  - Model `DatabaseAdvancedThreatProtection` moved instance variable `state` and `creation_time` under property `properties` whose type is `AdvancedThreatProtectionProperties`
  - Model `DatabaseSecurityAlertPolicy` moved instance variable `state`, `disabled_alerts`, `email_addresses`, `email_account_admins`, `storage_endpoint`, `storage_account_access_key`, `retention_days` and `creation_time` under property `properties` whose type is `SecurityAlertsPolicyProperties`
  - Model `DatabaseVulnerabilityAssessmentScansExport` moved instance variable `exported_report_location` under property `properties` whose type is `DatabaseVulnerabilityAssessmentScanExportProperties`
  - Model `FirewallRule` moved instance variable `start_ip_address` and `end_ip_address` under property `properties` whose type is `ServerFirewallRuleProperties`
  - Model `FirewallRuleList` renamed its instance variable `values` to `values_property`
  - Model `IPv6FirewallRule` moved instance variable `start_i_pv6_address` and `end_i_pv6_address` under property `properties` whose type is `IPv6ServerFirewallRuleProperties`
  - Model `InstancePoolUpdate` moved instance variable `subnet_id`, `v_cores`, `license_type`, `dns_zone` and `maintenance_configuration_id` under property `properties` whose type is `InstancePoolProperties`
  - Model `LogicalDatabaseTransparentDataEncryption` moved instance variable `state` under property `properties` whose type is `TransparentDataEncryptionProperties`
  - Model `LongTermRetentionBackupOperationResult` moved instance variable `request_id`, `operation_type`, `from_backup_resource_id`, `to_backup_resource_id`, `target_backup_storage_redundancy`, `status` and `message` under property `properties` whose type is `LongTermRetentionOperationResultProperties`
  - Model `ManagedDatabaseAdvancedThreatProtection` moved instance variable `state` and `creation_time` under property `properties` whose type is `AdvancedThreatProtectionProperties`
  - Model `ManagedDatabaseRestoreDetailsResult` moved instance variable `type_properties_type`, `status`, `block_reason`, `last_uploaded_file_name`, `last_uploaded_file_time`, `last_restored_file_name`, `last_restored_file_time`, `percent_completed`, `current_restored_size_mb`, `current_restore_plan_size_mb`, `current_backup_type`, `current_restoring_file_name`, `number_of_files_detected`, `number_of_files_queued`, `number_of_files_skipped`, `number_of_files_restoring`, `number_of_files_restored`, `number_of_files_unrestorable`, `full_backup_sets`, `diff_backup_sets`, `log_backup_sets` and `unrestorable_files` under property `properties` whose type is `ManagedDatabaseRestoreDetailsProperties`
  - Model `ManagedDatabaseSecurityAlertPolicy` moved instance variable `state`, `disabled_alerts`, `email_addresses`, `email_account_admins`, `storage_endpoint`, `storage_account_access_key`, `retention_days` and `creation_time` under property `properties` whose type is `SecurityAlertPolicyProperties`
  - Model `ManagedDatabaseUpdate` moved instance variable `collation`, `status`, `creation_date`, `earliest_restore_point`, `restore_point_in_time`, `default_secondary_location`, `catalog_collation`, `create_mode`, `storage_container_uri`, `source_database_id`, `cross_subscription_source_database_id`, `restorable_dropped_database_id`, `cross_subscription_restorable_dropped_database_id`, `storage_container_identity`, `storage_container_sas_token`, `failover_group_id`, `recoverable_database_id`, `long_term_retention_backup_resource_id`, `auto_complete_restore`, `last_backup_name`, `cross_subscription_target_managed_instance_id` and `is_ledger_on` under property `properties` whose type is `ManagedDatabaseProperties`
  - Model `ManagedInstanceAdvancedThreatProtection` moved instance variable `state` and `creation_time` under property `properties` whose type is `AdvancedThreatProtectionProperties`
  - Model `ManagedInstanceAzureADOnlyAuthentication` moved instance variable `azure_ad_only_authentication` under property `properties` whose type is `ManagedInstanceAzureADOnlyAuthProperties`
  - Model `ManagedInstanceEditionCapability` deleted or renamed its instance variable `zone_redundant`
  - Model `ManagedInstancePrivateEndpointConnection` moved instance variable `private_endpoint`, `private_link_service_connection_state` and `provisioning_state` under property `properties` whose type is `ManagedInstancePrivateEndpointConnectionProperties`
  - Model `ManagedInstanceQuery` moved instance variable `query_text` under property `properties` whose type is `QueryProperties`
  - Model `ManagedInstanceUpdate` moved instance variable `provisioning_state`, `managed_instance_create_mode`, `fully_qualified_domain_name`, `is_general_purpose_v2`, `administrator_login`, `administrator_login_password`, `subnet_id`, `state`, `license_type`, `hybrid_secondary_usage`, `hybrid_secondary_usage_detected`, `v_cores`, `storage_size_in_gb`, `storage_iops`, `storage_throughput_mbps`, `collation`, `dns_zone`, `dns_zone_partner`, `public_data_endpoint_enabled`, `source_managed_instance_id`, `restore_point_in_time`, `proxy_override`, `timezone_id`, `instance_pool_id`, `maintenance_configuration_id`, `private_endpoint_connections`, `minimal_tls_version`, `current_backup_storage_redundancy`, `requested_backup_storage_redundancy`, `zone_redundant`, `primary_user_assigned_identity_id`, `key_id`, `administrators`, `service_principal`, `virtual_cluster_id`, `external_governance_status`, `pricing_model`, `create_time`, `authentication_metadata` and `database_format` under property `properties` whose type is `ManagedInstanceProperties`
  - Model `ManagedServerSecurityAlertPolicy` moved instance variable `state`, `disabled_alerts`, `email_addresses`, `email_account_admins`, `storage_endpoint`, `storage_account_access_key`, `retention_days` and `creation_time` under property `properties` whose type is `SecurityAlertsPolicyProperties`
  - Model `PrivateEndpointConnection` moved instance variable `private_endpoint`, `group_ids`, `private_link_service_connection_state` and `provisioning_state` under property `properties` whose type is `PrivateEndpointConnectionProperties`
  - Model `QueryStatistics` moved instance variable `database_name`, `query_id`, `start_time`, `end_time` and `intervals` under property `properties` whose type is `QueryStatisticsProperties`
  - Model `RefreshExternalGovernanceStatusOperationResultMI` moved instance variable `request_id`, `request_type`, `queued_time`, `managed_instance_name`, `status` and `error_message` under property `properties` whose type is `RefreshExternalGovernanceStatusOperationResultPropertiesMI`
  - Model `ServerAdvancedThreatProtection` moved instance variable `state` and `creation_time` under property `properties` whose type is `AdvancedThreatProtectionProperties`
  - Model `ServerAutomaticTuning` moved instance variable `desired_state`, `actual_state` and `options` under property `properties` whose type is `AutomaticTuningServerProperties`
  - Model `ServerAzureADAdministrator` moved instance variable `administrator_type`, `login`, `sid`, `tenant_id` and `azure_ad_only_authentication` under property `properties` whose type is `AdministratorProperties`
  - Model `ServerAzureADOnlyAuthentication` moved instance variable `azure_ad_only_authentication` under property `properties` whose type is `AzureADOnlyAuthProperties`
  - Model `ServerDevOpsAuditingSettings` moved instance variable `is_azure_monitor_target_enabled`, `is_managed_identity_in_use`, `state`, `storage_endpoint`, `storage_account_access_key` and `storage_account_subscription_id` under property `properties` whose type is `ServerDevOpsAuditSettingsProperties`
  - Model `ServerSecurityAlertPolicy` moved instance variable `state`, `disabled_alerts`, `email_addresses`, `email_account_admins`, `storage_endpoint`, `storage_account_access_key`, `retention_days` and `creation_time` under property `properties` whose type is `SecurityAlertsPolicyProperties`
  - Model `ServerUpdate` moved instance variable `administrator_login`, `administrator_login_password`, `version`, `state`, `fully_qualified_domain_name`, `private_endpoint_connections`, `minimal_tls_version`, `public_network_access`, `workspace_feature`, `primary_user_assigned_identity_id`, `federated_client_id`, `key_id`, `administrators`, `restrict_outbound_network_access`, `is_i_pv6_enabled`, `external_governance_status`, `retention_days` and `create_mode` under property `properties` whose type is `ServerProperties`
  - Model `SqlVulnerabilityAssessment` moved instance variable `state` under property `properties` whose type is `SqlVulnerabilityAssessmentPolicyProperties`
  - Model `SqlVulnerabilityAssessmentScanResults` moved instance variable `rule_id`, `status`, `error_message`, `is_trimmed`, `query_results`, `remediation`, `baseline_adjusted_result` and `rule_metadata` under property `properties` whose type is `SqlVulnerabilityAssessmentScanResultProperties`
  - Model `UpdateLongTermRetentionBackupParameters` moved instance variable `requested_backup_storage_redundancy` under property `properties` whose type is `UpdateLongTermRetentionBackupParametersProperties`
  - Model `UpdateVirtualClusterDnsServersOperation` moved instance variable `status` under property `properties` whose type is `VirtualClusterDnsServersProperties`
  - Model `VirtualClusterUpdate` moved instance variable `subnet_id`, `version` and `child_resources` under property `properties` whose type is `VirtualClusterProperties`
  - Deleted or renamed model `ElasticPoolActivity`
  - Deleted or renamed model `ElasticPoolDatabaseActivity`
  - Deleted or renamed model `FreemiumType`
  - Deleted or renamed model `Metric`
  - Deleted or renamed model `MetricAvailability`
  - Deleted or renamed model `MetricDefinition`
  - Deleted or renamed model `MetricName`
  - Deleted or renamed model `MetricValue`
  - Deleted or renamed model `OperationImpact`
  - Deleted or renamed model `PrimaryAggregationType`
  - Deleted or renamed model `QueryMetricIntervalAutoGenerated`
  - Deleted or renamed model `ServerCommunicationLink`
  - Deleted or renamed model `ServiceObjective`
  - Deleted or renamed model `ServiceObjectiveName`
  - Deleted or renamed model `SloUsageMetric`
  - Deleted or renamed model `UnitDefinitionType`
  - Deleted or renamed model `UnitType`
  - Deleted or renamed model `UpsertManagedServerOperationStep`
  - Deleted or renamed model `UpsertManagedServerOperationStepStatus`
  - Method `CapabilitiesOperations.list_by_location` changed its parameter `include` from `positional_or_keyword` to `keyword_only`
  - Method `DatabaseAdvisorsOperations.list_by_database` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `DatabaseColumnsOperations.list_by_database` changed its parameter `schema`/`table`/`column`/`order_by`/`skiptoken` from `positional_or_keyword` to `keyword_only`
  - Method `DatabasesOperations.begin_failover` changed its parameter `replica_type` from `positional_or_keyword` to `keyword_only`
  - Method `DatabasesOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `DatabasesOperations.list_by_server` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Deleted or renamed method `DatabasesOperations.list_metric_definitions`
  - Deleted or renamed method `DatabasesOperations.list_metrics`
  - Deleted or renamed method `ElasticPoolsOperations.list_metric_definitions`
  - Deleted or renamed method `ElasticPoolsOperations.list_metrics`
  - Deleted or renamed method `GeoBackupPoliciesOperations.list_by_database`
  - Method `JobExecutionsOperations.list_by_agent` changed its parameter `create_time_min`/`create_time_max`/`end_time_min`/`end_time_max`/`is_active` from `positional_or_keyword` to `keyword_only`
  - Method `JobExecutionsOperations.list_by_job` changed its parameter `create_time_min`/`create_time_max`/`end_time_min`/`end_time_max`/`is_active` from `positional_or_keyword` to `keyword_only`
  - Method `JobStepExecutionsOperations.list_by_job_execution` changed its parameter `create_time_min`/`create_time_max`/`end_time_min`/`end_time_max`/`is_active` from `positional_or_keyword` to `keyword_only`
  - Method `JobTargetExecutionsOperations.list_by_job_execution` changed its parameter `create_time_min`/`create_time_max`/`end_time_min`/`end_time_max`/`is_active` from `positional_or_keyword` to `keyword_only`
  - Method `JobTargetExecutionsOperations.list_by_step` changed its parameter `create_time_min`/`create_time_max`/`end_time_min`/`end_time_max`/`is_active` from `positional_or_keyword` to `keyword_only`
  - Method `LongTermRetentionBackupsOperations.list_by_database` changed its parameter `only_latest_per_database`/`database_state` from `positional_or_keyword` to `keyword_only`
  - Method `LongTermRetentionBackupsOperations.list_by_location` changed its parameter `only_latest_per_database`/`database_state` from `positional_or_keyword` to `keyword_only`
  - Method `LongTermRetentionBackupsOperations.list_by_resource_group_database` changed its parameter `only_latest_per_database`/`database_state` from `positional_or_keyword` to `keyword_only`
  - Method `LongTermRetentionBackupsOperations.list_by_resource_group_location` changed its parameter `only_latest_per_database`/`database_state` from `positional_or_keyword` to `keyword_only`
  - Method `LongTermRetentionBackupsOperations.list_by_resource_group_server` changed its parameter `only_latest_per_database`/`database_state` from `positional_or_keyword` to `keyword_only`
  - Method `LongTermRetentionBackupsOperations.list_by_server` changed its parameter `only_latest_per_database`/`database_state` from `positional_or_keyword` to `keyword_only`
  - Method `LongTermRetentionManagedInstanceBackupsOperations.list_by_database` changed its parameter `only_latest_per_database`/`database_state` from `positional_or_keyword` to `keyword_only`
  - Method `LongTermRetentionManagedInstanceBackupsOperations.list_by_instance` changed its parameter `only_latest_per_database`/`database_state` from `positional_or_keyword` to `keyword_only`
  - Method `LongTermRetentionManagedInstanceBackupsOperations.list_by_location` changed its parameter `only_latest_per_database`/`database_state` from `positional_or_keyword` to `keyword_only`
  - Method `LongTermRetentionManagedInstanceBackupsOperations.list_by_resource_group_database` changed its parameter `only_latest_per_database`/`database_state` from `positional_or_keyword` to `keyword_only`
  - Method `LongTermRetentionManagedInstanceBackupsOperations.list_by_resource_group_instance` changed its parameter `only_latest_per_database`/`database_state` from `positional_or_keyword` to `keyword_only`
  - Method `LongTermRetentionManagedInstanceBackupsOperations.list_by_resource_group_location` changed its parameter `only_latest_per_database`/`database_state` from `positional_or_keyword` to `keyword_only`
  - Method `MaintenanceWindowOptionsOperations.get` changed its parameter `maintenance_window_options_name` from `positional_or_keyword` to `keyword_only`
  - Method `MaintenanceWindowsOperations.create_or_update` changed its parameter `maintenance_window_name` from `positional_or_keyword` to `keyword_only`
  - Method `MaintenanceWindowsOperations.get` changed its parameter `maintenance_window_name` from `positional_or_keyword` to `keyword_only`
  - Method `ManagedDatabaseColumnsOperations.list_by_database` changed its parameter `schema`/`table`/`column`/`order_by`/`skiptoken` from `positional_or_keyword` to `keyword_only`
  - Method `ManagedDatabaseMoveOperationsOperations.list_by_location` changed its parameter `only_latest_per_database` from `positional_or_keyword` to `keyword_only`
  - Method `ManagedDatabaseQueriesOperations.list_by_query` changed its parameter `start_time`/`end_time`/`interval` from `positional_or_keyword` to `keyword_only`
  - Method `ManagedDatabaseSecurityEventsOperations.list_by_database` changed its parameter `skiptoken` from `positional_or_keyword` to `keyword_only`
  - Method `ManagedDatabaseSensitivityLabelsOperations.list_current_by_database` changed its parameter `skip_token`/`count` from `positional_or_keyword` to `keyword_only`
  - Method `ManagedDatabaseSensitivityLabelsOperations.list_recommended_by_database` changed its parameter `skip_token`/`include_disabled_recommendations` from `positional_or_keyword` to `keyword_only`
  - Method `ManagedInstancesOperations.begin_failover` changed its parameter `replica_type` from `positional_or_keyword` to `keyword_only`
  - Method `ManagedInstancesOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `ManagedInstancesOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `ManagedInstancesOperations.list_by_instance_pool` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `ManagedInstancesOperations.list_by_managed_instance` changed its parameter `number_of_queries`/`databases`/`start_time`/`end_time`/`interval`/`aggregation_function`/`observation_metric` from `positional_or_keyword` to `keyword_only`
  - Method `ManagedInstancesOperations.list_by_resource_group` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `OutboundFirewallRulesOperations.begin_create_or_update` deleted or renamed its parameter `parameters` of kind `positional_or_keyword`
  - Method `RecoverableDatabasesOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `RestorableDroppedDatabasesOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `SensitivityLabelsOperations.list_current_by_database` changed its parameter `skip_token`/`count` from `positional_or_keyword` to `keyword_only`
  - Method `SensitivityLabelsOperations.list_recommended_by_database` changed its parameter `skip_token`/`include_disabled_recommendations` from `positional_or_keyword` to `keyword_only`
  - Method `ServerAdvisorsOperations.list_by_server` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `ServersOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `ServersOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `ServersOperations.list_by_resource_group` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `SyncGroupsOperations.list_logs` changed its parameter `start_time`/`end_time`/`type`/`continuation_token_parameter` from `positional_or_keyword` to `keyword_only`
  - Method `UsagesOperations.list_by_instance_pool` changed its parameter `expand_children` from `positional_or_keyword` to `keyword_only`
  - Deleted or renamed operation group `ElasticPoolActivitiesOperations`
  - Deleted or renamed operation group `ElasticPoolDatabaseActivitiesOperations`
  - Deleted or renamed operation group `ServerCommunicationLinksOperations`
  - Deleted or renamed operation group `ServiceObjectivesOperations`

### Other Changes

  - Deleted model `OutboundEnvironmentEndpointCollection`/ `SecurityEventCollection`/`ManagedInstanceQueryStatistics`/`SecurityEventsFilterParameters` which actually were not used by SDK users

## 4.0.0b24 (2025-10-09)

### Bugs Fixed

- Exclude `generated_samples` and `generated_tests` from wheel

## 4.0.0b23 (2025-09-10)

### Features Added

  - Added operation DatabasesOperations.list_metric_definitions
  - Added operation DatabasesOperations.list_metrics
  - Added operation ElasticPoolsOperations.list_metric_definitions
  - Added operation ElasticPoolsOperations.list_metrics
  - Added operation GeoBackupPoliciesOperations.list_by_database
  - Added operation group ElasticPoolActivitiesOperations
  - Added operation group ElasticPoolDatabaseActivitiesOperations
  - Added operation group ServerCommunicationLinksOperations
  - Added operation group ServiceObjectivesOperations
  - Model ManagedInstanceEditionCapability has a new parameter zone_redundant
  - Model ServerUsage has a new parameter next_reset_time
  - Model ServerUsage has a new parameter resource_name

### Breaking Changes

  - Model DataMaskingRuleListResult no longer has parameter next_link
  - Model DatabaseExtensions no longer has parameter administrator_login
  - Model DatabaseExtensions no longer has parameter administrator_login_password
  - Model DatabaseExtensions no longer has parameter authentication_type
  - Model DatabaseExtensions no longer has parameter database_edition
  - Model DatabaseExtensions no longer has parameter max_size_bytes
  - Model DatabaseExtensions no longer has parameter network_isolation
  - Model DatabaseExtensions no longer has parameter service_objective_name
  - Model DatabaseKey no longer has parameter key_version
  - Model EditionCapability no longer has parameter zone_pinning
  - Model ElasticPool no longer has parameter auto_pause_delay
  - Model ElasticPoolEditionCapability no longer has parameter zone_pinning
  - Model ElasticPoolPerDatabaseSettings no longer has parameter auto_pause_delay
  - Model ElasticPoolPerformanceLevelCapability no longer has parameter supported_auto_pause_delay
  - Model ElasticPoolPerformanceLevelCapability no longer has parameter supported_min_capacities
  - Model ElasticPoolPerformanceLevelCapability no longer has parameter supported_per_database_auto_pause_delay
  - Model ElasticPoolPerformanceLevelCapability no longer has parameter supported_zones
  - Model ElasticPoolUpdate no longer has parameter auto_pause_delay
  - Model EncryptionProtector no longer has parameter key_version
  - Model GeoBackupPolicyListResult no longer has parameter next_link
  - Model ImportExportExtensionsOperationResult no longer has parameter blob_uri
  - Model ImportExportExtensionsOperationResult no longer has parameter private_endpoint_connections
  - Model ImportExportExtensionsOperationResult no longer has parameter queued_time
  - Model JobAgent no longer has parameter identity
  - Model JobAgentUpdate no longer has parameter identity
  - Model JobAgentUpdate no longer has parameter sku
  - Model LocationCapabilities no longer has parameter is_zone_resilient_provisioning_allowed
  - Model LocationCapabilities no longer has parameter supported_job_agent_versions
  - Model LogicalDatabaseTransparentDataEncryption no longer has parameter scan_state
  - Model ManagedDatabase no longer has parameter extended_accessibility_info
  - Model ManagedDatabaseUpdate no longer has parameter extended_accessibility_info
  - Model ManagedInstance no longer has parameter memory_size_in_gb
  - Model ManagedInstance no longer has parameter requested_logical_availability_zone
  - Model ManagedInstanceEditionCapability no longer has parameter is_general_purpose_v2
  - Model ManagedInstanceFamilyCapability no longer has parameter zone_redundant
  - Model ManagedInstanceLongTermRetentionBackup no longer has parameter backup_storage_access_tier
  - Model ManagedInstanceLongTermRetentionPolicy no longer has parameter backup_storage_access_tier
  - Model ManagedInstancePrivateLinkProperties no longer has parameter required_zone_names
  - Model ManagedInstanceUpdate no longer has parameter memory_size_in_gb
  - Model ManagedInstanceUpdate no longer has parameter requested_logical_availability_zone
  - Model ManagedInstanceVcoresCapability no longer has parameter included_storage_i_ops
  - Model ManagedInstanceVcoresCapability no longer has parameter included_storage_throughput_m_bps
  - Model ManagedInstanceVcoresCapability no longer has parameter iops_included_value_override_factor_per_selected_storage_gb
  - Model ManagedInstanceVcoresCapability no longer has parameter iops_min_value_override_factor_per_selected_storage_gb
  - Model ManagedInstanceVcoresCapability no longer has parameter supported_memory_sizes_in_gb
  - Model ManagedInstanceVcoresCapability no longer has parameter supported_storage_i_ops
  - Model ManagedInstanceVcoresCapability no longer has parameter supported_storage_throughput_m_bps
  - Model ManagedInstanceVcoresCapability no longer has parameter throughput_m_bps_included_value_override_factor_per_selected_storage_gb
  - Model ManagedInstanceVcoresCapability no longer has parameter throughput_m_bps_min_value_override_factor_per_selected_storage_gb
  - Model SensitivityLabel no longer has parameter client_classification_source
  - Model ServerKey no longer has parameter key_version
  - Model ServerUsage no longer has parameter id
  - Model ServerUsage no longer has parameter type
  - Model ServerUsageListResult no longer has parameter next_link
  - Model ServiceObjectiveCapability no longer has parameter supported_free_limit_exhaustion_behaviors
  - Model ServiceObjectiveCapability no longer has parameter supported_zones
  - Model ServiceObjectiveCapability no longer has parameter zone_pinning
  - Operation DataMaskingPoliciesOperations.create_or_update no longer has parameter data_masking_policy_name
  - Operation DataMaskingPoliciesOperations.get no longer has parameter data_masking_policy_name
  - Operation DataMaskingRulesOperations.create_or_update no longer has parameter data_masking_policy_name
  - Operation DataMaskingRulesOperations.list_by_database no longer has parameter data_masking_policy_name
  - Operation LongTermRetentionManagedInstanceBackupsOperations.list_by_location no longer has parameter filter
  - Operation LongTermRetentionManagedInstanceBackupsOperations.list_by_location no longer has parameter skip
  - Operation LongTermRetentionManagedInstanceBackupsOperations.list_by_location no longer has parameter top
  - Operation LongTermRetentionManagedInstanceBackupsOperations.list_by_resource_group_location no longer has parameter filter
  - Operation LongTermRetentionManagedInstanceBackupsOperations.list_by_resource_group_location no longer has parameter skip
  - Operation LongTermRetentionManagedInstanceBackupsOperations.list_by_resource_group_location no longer has parameter top
  - Operation OutboundFirewallRulesOperations.begin_create_or_update has a new required parameter parameters
  - Parameter administrator_login_password of model ExportDatabaseDefinition is now required
  - Parameter administrator_login_password of model ImportExistingDatabaseDefinition is now required
  - Parameter credential of model JobStepOutput is now required
  - Parameter state of model GeoBackupPolicy is now required
  - Parameter value of model ServerUsageListResult is now required
  - Removed operation GeoBackupPoliciesOperations.list
  - Removed operation ManagedDatabaseSensitivityLabelsOperations.list_by_database
  - Removed operation ManagedDatabasesOperations.begin_reevaluate_inaccessible_database_state
  - Removed operation ManagedInstanceLongTermRetentionPoliciesOperations.begin_delete
  - Removed operation ManagedInstancesOperations.begin_reevaluate_inaccessible_database_state
  - Removed operation ManagedInstancesOperations.begin_validate_azure_key_vault_encryption_key
  - Removed operation SensitivityLabelsOperations.list_by_database
  - Removed operation TransparentDataEncryptionsOperations.begin_resume
  - Removed operation TransparentDataEncryptionsOperations.begin_suspend
  - Removed operation VirtualClustersOperations.begin_create_or_update
  - Removed operation group InstancePoolOperationsOperations
  - Removed operation group NetworkSecurityPerimeterConfigurationsOperations

## 4.0.0b22 (2025-07-30)

### Features Added

  - Added operation LongTermRetentionBackupsOperations.begin_lock_time_based_immutability
  - Added operation LongTermRetentionBackupsOperations.begin_lock_time_based_immutability_by_resource_group
  - Added operation LongTermRetentionBackupsOperations.begin_remove_legal_hold_immutability
  - Added operation LongTermRetentionBackupsOperations.begin_remove_legal_hold_immutability_by_resource_group
  - Added operation LongTermRetentionBackupsOperations.begin_remove_time_based_immutability
  - Added operation LongTermRetentionBackupsOperations.begin_remove_time_based_immutability_by_resource_group
  - Added operation LongTermRetentionBackupsOperations.begin_set_legal_hold_immutability
  - Added operation LongTermRetentionBackupsOperations.begin_set_legal_hold_immutability_by_resource_group
  - Added operation ManagedDatabasesOperations.begin_reevaluate_inaccessible_database_state
  - Added operation ManagedInstancesOperations.begin_reevaluate_inaccessible_database_state
  - Added operation ManagedInstancesOperations.begin_validate_azure_key_vault_encryption_key
  - Added operation TransparentDataEncryptionsOperations.begin_resume
  - Added operation TransparentDataEncryptionsOperations.begin_suspend
  - Added operation VirtualClustersOperations.begin_create_or_update
  - Model DatabaseKey has a new parameter key_version
  - Model EncryptionProtector has a new parameter key_version
  - Model LocationCapabilities has a new parameter is_zone_resilient_provisioning_allowed
  - Model LogicalDatabaseTransparentDataEncryption has a new parameter scan_state
  - Model LongTermRetentionBackup has a new parameter legal_hold_immutability
  - Model LongTermRetentionBackup has a new parameter time_based_immutability
  - Model LongTermRetentionBackup has a new parameter time_based_immutability_mode
  - Model LongTermRetentionPolicy has a new parameter time_based_immutability
  - Model LongTermRetentionPolicy has a new parameter time_based_immutability_mode
  - Model ManagedDatabase has a new parameter extended_accessibility_info
  - Model ManagedDatabaseUpdate has a new parameter extended_accessibility_info
  - Model ManagedInstance has a new parameter memory_size_in_gb
  - Model ManagedInstance has a new parameter requested_logical_availability_zone
  - Model ManagedInstanceUpdate has a new parameter memory_size_in_gb
  - Model ManagedInstanceUpdate has a new parameter requested_logical_availability_zone
  - Model ManagedInstanceVcoresCapability has a new parameter supported_memory_sizes_in_gb
  - Model Server has a new parameter create_mode
  - Model Server has a new parameter retention_days
  - Model ServerKey has a new parameter key_version
  - Model ServerUpdate has a new parameter create_mode
  - Model ServerUpdate has a new parameter retention_days

### Breaking Changes

  - Model ManagedInstance no longer has parameter total_memory_mb
  - Model ManagedInstanceUpdate no longer has parameter total_memory_mb
  - Model ManagedInstanceVcoresCapability no longer has parameter supported_memory_limits_mb

## 4.0.0b21 (2025-03-23)

### Features Added

  - Added operation GeoBackupPoliciesOperations.list
  - Added operation ManagedDatabaseSensitivityLabelsOperations.list_by_database
  - Added operation ManagedInstanceLongTermRetentionPoliciesOperations.begin_delete
  - Added operation SensitivityLabelsOperations.list_by_database
  - Added operation group InstancePoolOperationsOperations
  - Added operation group NetworkSecurityPerimeterConfigurationsOperations
  - Model DataMaskingRuleListResult has a new parameter next_link
  - Model DatabaseExtensions has a new parameter administrator_login
  - Model DatabaseExtensions has a new parameter administrator_login_password
  - Model DatabaseExtensions has a new parameter authentication_type
  - Model DatabaseExtensions has a new parameter database_edition
  - Model DatabaseExtensions has a new parameter max_size_bytes
  - Model DatabaseExtensions has a new parameter network_isolation
  - Model DatabaseExtensions has a new parameter service_objective_name
  - Model EditionCapability has a new parameter zone_pinning
  - Model ElasticPool has a new parameter auto_pause_delay
  - Model ElasticPoolEditionCapability has a new parameter zone_pinning
  - Model ElasticPoolPerDatabaseSettings has a new parameter auto_pause_delay
  - Model ElasticPoolPerformanceLevelCapability has a new parameter supported_auto_pause_delay
  - Model ElasticPoolPerformanceLevelCapability has a new parameter supported_min_capacities
  - Model ElasticPoolPerformanceLevelCapability has a new parameter supported_per_database_auto_pause_delay
  - Model ElasticPoolPerformanceLevelCapability has a new parameter supported_zones
  - Model ElasticPoolUpdate has a new parameter auto_pause_delay
  - Model GeoBackupPolicyListResult has a new parameter next_link
  - Model ImportExportExtensionsOperationResult has a new parameter blob_uri
  - Model ImportExportExtensionsOperationResult has a new parameter private_endpoint_connections
  - Model ImportExportExtensionsOperationResult has a new parameter queued_time
  - Model JobAgent has a new parameter identity
  - Model JobAgentUpdate has a new parameter identity
  - Model JobAgentUpdate has a new parameter sku
  - Model LocationCapabilities has a new parameter supported_job_agent_versions
  - Model ManagedInstance has a new parameter total_memory_mb
  - Model ManagedInstanceEditionCapability has a new parameter is_general_purpose_v2
  - Model ManagedInstanceFamilyCapability has a new parameter zone_redundant
  - Model ManagedInstanceLongTermRetentionBackup has a new parameter backup_storage_access_tier
  - Model ManagedInstanceLongTermRetentionPolicy has a new parameter backup_storage_access_tier
  - Model ManagedInstancePrivateLinkProperties has a new parameter required_zone_names
  - Model ManagedInstanceUpdate has a new parameter total_memory_mb
  - Model ManagedInstanceVcoresCapability has a new parameter included_storage_i_ops
  - Model ManagedInstanceVcoresCapability has a new parameter included_storage_throughput_m_bps
  - Model ManagedInstanceVcoresCapability has a new parameter iops_included_value_override_factor_per_selected_storage_gb
  - Model ManagedInstanceVcoresCapability has a new parameter iops_min_value_override_factor_per_selected_storage_gb
  - Model ManagedInstanceVcoresCapability has a new parameter supported_memory_limits_mb
  - Model ManagedInstanceVcoresCapability has a new parameter supported_storage_i_ops
  - Model ManagedInstanceVcoresCapability has a new parameter supported_storage_throughput_m_bps
  - Model ManagedInstanceVcoresCapability has a new parameter throughput_m_bps_included_value_override_factor_per_selected_storage_gb
  - Model ManagedInstanceVcoresCapability has a new parameter throughput_m_bps_min_value_override_factor_per_selected_storage_gb
  - Model SensitivityLabel has a new parameter client_classification_source
  - Model ServerUsage has a new parameter id
  - Model ServerUsage has a new parameter type
  - Model ServerUsageListResult has a new parameter next_link
  - Model ServiceObjectiveCapability has a new parameter supported_free_limit_exhaustion_behaviors
  - Model ServiceObjectiveCapability has a new parameter supported_zones
  - Model ServiceObjectiveCapability has a new parameter zone_pinning
  - Operation LongTermRetentionManagedInstanceBackupsOperations.list_by_location has a new optional parameter filter
  - Operation LongTermRetentionManagedInstanceBackupsOperations.list_by_location has a new optional parameter skip
  - Operation LongTermRetentionManagedInstanceBackupsOperations.list_by_location has a new optional parameter top
  - Operation LongTermRetentionManagedInstanceBackupsOperations.list_by_resource_group_location has a new optional parameter filter
  - Operation LongTermRetentionManagedInstanceBackupsOperations.list_by_resource_group_location has a new optional parameter skip
  - Operation LongTermRetentionManagedInstanceBackupsOperations.list_by_resource_group_location has a new optional parameter top

### Breaking Changes

  - Model LongTermRetentionPolicy no longer has parameter backup_storage_access_tier
  - Model LongTermRetentionPolicy no longer has parameter make_backups_immutable
  - Model ManagedInstanceEditionCapability no longer has parameter zone_redundant
  - Model ServerUsage no longer has parameter next_reset_time
  - Model ServerUsage no longer has parameter resource_name
  - Operation DataMaskingPoliciesOperations.create_or_update has a new required parameter data_masking_policy_name
  - Operation DataMaskingPoliciesOperations.get has a new required parameter data_masking_policy_name
  - Operation DataMaskingRulesOperations.create_or_update has a new required parameter data_masking_policy_name
  - Operation DataMaskingRulesOperations.list_by_database has a new required parameter data_masking_policy_name
  - Operation OutboundFirewallRulesOperations.begin_create_or_update no longer has parameter parameters
  - Removed operation DatabasesOperations.list_metric_definitions
  - Removed operation DatabasesOperations.list_metrics
  - Removed operation ElasticPoolsOperations.list_metric_definitions
  - Removed operation ElasticPoolsOperations.list_metrics
  - Removed operation GeoBackupPoliciesOperations.list_by_database
  - Removed operation group ElasticPoolActivitiesOperations
  - Removed operation group ElasticPoolDatabaseActivitiesOperations
  - Removed operation group ServerCommunicationLinksOperations
  - Removed operation group ServiceObjectivesOperations

## 4.0.0b20 (2024-11-04)

### Features Added

  - Model `DistributedAvailabilityGroup` added property `distributed_availability_group_name`
  - Model `DistributedAvailabilityGroup` added property `partner_link_role`
  - Model `DistributedAvailabilityGroup` added property `partner_availability_group_name`
  - Model `DistributedAvailabilityGroup` added property `partner_endpoint`
  - Model `DistributedAvailabilityGroup` added property `instance_link_role`
  - Model `DistributedAvailabilityGroup` added property `instance_availability_group_name`
  - Model `DistributedAvailabilityGroup` added property `failover_mode`
  - Model `DistributedAvailabilityGroup` added property `seeding_mode`
  - Model `DistributedAvailabilityGroup` added property `databases`
  - Added model `CertificateInfo`
  - Added model `DistributedAvailabilityGroupDatabase`
  - Added model `DistributedAvailabilityGroupSetRole`
  - Added model `DistributedAvailabilityGroupsFailoverRequest`
  - Added enum `FailoverModeType`
  - Added enum `FailoverType`
  - Added enum `InstanceRole`
  - Added enum `LinkRole`
  - Added enum `ReplicaConnectedState`
  - Added enum `ReplicaSynchronizationHealth`
  - Added enum `ReplicationModeType`
  - Added enum `RoleChangeType`
  - Added enum `SeedingModeType`
  - Operation group `DistributedAvailabilityGroupsOperations` added method `begin_failover`
  - Operation group `DistributedAvailabilityGroupsOperations` added method `begin_set_role`

### Breaking Changes

  - Model `DistributedAvailabilityGroup` deleted or renamed its instance variable `target_database`
  - Model `DistributedAvailabilityGroup` deleted or renamed its instance variable `source_endpoint`
  - Model `DistributedAvailabilityGroup` deleted or renamed its instance variable `primary_availability_group_name`
  - Model `DistributedAvailabilityGroup` deleted or renamed its instance variable `secondary_availability_group_name`
  - Model `DistributedAvailabilityGroup` deleted or renamed its instance variable `source_replica_id`
  - Model `DistributedAvailabilityGroup` deleted or renamed its instance variable `target_replica_id`
  - Model `DistributedAvailabilityGroup` deleted or renamed its instance variable `link_state`
  - Model `DistributedAvailabilityGroup` deleted or renamed its instance variable `last_hardened_lsn`
  - Deleted or renamed model `ReplicationMode`

## 4.0.0b19 (2024-09-09)

### Features Added

  - The 'ReplicationLinksOperations' method 'begin_create_or_update' was added in the current version
  - The 'ReplicationLinksOperations' method 'begin_update' was added in the current version
  - The model or publicly exposed class 'ColumnDataType' had property 'INT' added in the current version
  - The model or publicly exposed class 'DistributedAvailabilityGroup' had property 'target_database' added in the current version
  - The model or publicly exposed class 'DistributedAvailabilityGroup' had property 'source_endpoint' added in the current version
  - The model or publicly exposed class 'DistributedAvailabilityGroup' had property 'primary_availability_group_name' added in the current version
  - The model or publicly exposed class 'DistributedAvailabilityGroup' had property 'secondary_availability_group_name' added in the current version
  - The model or publicly exposed class 'DistributedAvailabilityGroup' had property 'source_replica_id' added in the current version
  - The model or publicly exposed class 'DistributedAvailabilityGroup' had property 'target_replica_id' added in the current version
  - The model or publicly exposed class 'DistributedAvailabilityGroup' had property 'link_state' added in the current version
  - The model or publicly exposed class 'DistributedAvailabilityGroup' had property 'last_hardened_lsn' added in the current version
  - The model or publicly exposed class 'FailoverGroup' had property 'secondary_type' added in the current version
  - The model or publicly exposed class 'FailoverGroupUpdate' had property 'secondary_type' added in the current version
  - The model or publicly exposed class 'ManagedInstance' had property 'storage_iops' added in the current version
  - The model or publicly exposed class 'ManagedInstance' had property 'storage_throughput_mbps' added in the current version
  - The model or publicly exposed class 'ManagedInstanceUpdate' had property 'storage_iops' added in the current version
  - The model or publicly exposed class 'ManagedInstanceUpdate' had property 'storage_throughput_mbps' added in the current version
  - The model or publicly exposed class 'ReplicationLink' had property 'partner_database_id' added in the current version
  - The model or publicly exposed class 'FailoverGroupDatabasesSecondaryType' was added in the current version
  - The model or publicly exposed class 'ReplicationLinkUpdate' was added in the current version
  - The model or publicly exposed class 'ReplicationMode' was added in the current version
  - The 'ReplicationLinksOperations' method 'begin_create_or_update' was added in the current version
  - The 'ReplicationLinksOperations' method 'begin_update' was added in the current version

### Breaking Changes

  - The 'DistributedAvailabilityGroupsOperations' method 'begin_failover' was deleted or renamed in the current version
  - The 'DistributedAvailabilityGroupsOperations' method 'begin_set_role' was deleted or renamed in the current version
  - The 'ColumnDataType' enum had its value 'INT_ENUM' deleted or renamed in the current version
  - The model or publicly exposed class 'DistributedAvailabilityGroup' had its instance variable 'distributed_availability_group_name' deleted or renamed in the current version
  - The model or publicly exposed class 'DistributedAvailabilityGroup' had its instance variable 'partner_link_role' deleted or renamed in the current version
  - The model or publicly exposed class 'DistributedAvailabilityGroup' had its instance variable 'partner_availability_group_name' deleted or renamed in the current version
  - The model or publicly exposed class 'DistributedAvailabilityGroup' had its instance variable 'partner_endpoint' deleted or renamed in the current version
  - The model or publicly exposed class 'DistributedAvailabilityGroup' had its instance variable 'instance_link_role' deleted or renamed in the current version
  - The model or publicly exposed class 'DistributedAvailabilityGroup' had its instance variable 'instance_availability_group_name' deleted or renamed in the current version
  - The model or publicly exposed class 'DistributedAvailabilityGroup' had its instance variable 'failover_mode' deleted or renamed in the current version
  - The model or publicly exposed class 'DistributedAvailabilityGroup' had its instance variable 'seeding_mode' deleted or renamed in the current version
  - The model or publicly exposed class 'DistributedAvailabilityGroup' had its instance variable 'databases' deleted or renamed in the current version
  - The model or publicly exposed class 'ManagedInstance' had its instance variable 'storage_i_ops' deleted or renamed in the current version
  - The model or publicly exposed class 'ManagedInstance' had its instance variable 'storage_throughput_m_bps' deleted or renamed in the current version
  - The model or publicly exposed class 'ManagedInstanceUpdate' had its instance variable 'storage_i_ops' deleted or renamed in the current version
  - The model or publicly exposed class 'ManagedInstanceUpdate' had its instance variable 'storage_throughput_m_bps' deleted or renamed in the current version
  - The model or publicly exposed class 'CertificateInfo' was deleted or renamed in the current version
  - The model or publicly exposed class 'DistributedAvailabilityGroupDatabase' was deleted or renamed in the current version
  - The model or publicly exposed class 'DistributedAvailabilityGroupSetRole' was deleted or renamed in the current version
  - The model or publicly exposed class 'DistributedAvailabilityGroupsFailoverRequest' was deleted or renamed in the current version
  - The model or publicly exposed class 'FailoverModeType' was deleted or renamed in the current version
  - The model or publicly exposed class 'FailoverType' was deleted or renamed in the current version
  - The model or publicly exposed class 'InstanceRole' was deleted or renamed in the current version
  - The model or publicly exposed class 'LinkRole' was deleted or renamed in the current version
  - The model or publicly exposed class 'ReplicaConnectedState' was deleted or renamed in the current version
  - The model or publicly exposed class 'ReplicaSynchronizationHealth' was deleted or renamed in the current version
  - The model or publicly exposed class 'ReplicationModeType' was deleted or renamed in the current version
  - The model or publicly exposed class 'RoleChangeType' was deleted or renamed in the current version
  - The model or publicly exposed class 'SeedingModeType' was deleted or renamed in the current version
  - The 'DistributedAvailabilityGroupsOperations' method 'begin_failover' was deleted or renamed in the current version
  - The 'DistributedAvailabilityGroupsOperations' method 'begin_set_role' was deleted or renamed in the current version

## 4.0.0b18 (2024-07-11)

### Bugs Fixed

  - Fix import error when import from azure.mgmt.sql.aio

## 4.0.0b17 (2024-05-20)

### Features Added

  - Model DatabaseOperation has a new parameter operation_phase_details

## 4.0.0b16 (2024-04-07)

### Features Added

  - Added operation DistributedAvailabilityGroupsOperations.begin_failover
  - Added operation DistributedAvailabilityGroupsOperations.begin_set_role
  - Model DistributedAvailabilityGroup has a new parameter databases
  - Model DistributedAvailabilityGroup has a new parameter distributed_availability_group_name
  - Model DistributedAvailabilityGroup has a new parameter failover_mode
  - Model DistributedAvailabilityGroup has a new parameter instance_availability_group_name
  - Model DistributedAvailabilityGroup has a new parameter instance_link_role
  - Model DistributedAvailabilityGroup has a new parameter partner_availability_group_name
  - Model DistributedAvailabilityGroup has a new parameter partner_endpoint
  - Model DistributedAvailabilityGroup has a new parameter partner_link_role
  - Model DistributedAvailabilityGroup has a new parameter seeding_mode

### Breaking Changes

  - Model DistributedAvailabilityGroup no longer has parameter last_hardened_lsn
  - Model DistributedAvailabilityGroup no longer has parameter link_state
  - Model DistributedAvailabilityGroup no longer has parameter primary_availability_group_name
  - Model DistributedAvailabilityGroup no longer has parameter secondary_availability_group_name
  - Model DistributedAvailabilityGroup no longer has parameter source_endpoint
  - Model DistributedAvailabilityGroup no longer has parameter source_replica_id
  - Model DistributedAvailabilityGroup no longer has parameter target_database
  - Model DistributedAvailabilityGroup no longer has parameter target_replica_id

## 4.0.0b15 (2024-01-11)

### Features Added

  - Added operation ManagedInstancesOperations.begin_refresh_status
  - Model ManagedInstance has a new parameter authentication_metadata
  - Model ManagedInstance has a new parameter create_time
  - Model ManagedInstance has a new parameter database_format
  - Model ManagedInstance has a new parameter external_governance_status
  - Model ManagedInstance has a new parameter hybrid_secondary_usage
  - Model ManagedInstance has a new parameter hybrid_secondary_usage_detected
  - Model ManagedInstance has a new parameter is_general_purpose_v2
  - Model ManagedInstance has a new parameter pricing_model
  - Model ManagedInstance has a new parameter storage_i_ops
  - Model ManagedInstance has a new parameter storage_throughput_m_bps
  - Model ManagedInstance has a new parameter virtual_cluster_id
  - Model ManagedInstanceUpdate has a new parameter authentication_metadata
  - Model ManagedInstanceUpdate has a new parameter create_time
  - Model ManagedInstanceUpdate has a new parameter database_format
  - Model ManagedInstanceUpdate has a new parameter external_governance_status
  - Model ManagedInstanceUpdate has a new parameter hybrid_secondary_usage
  - Model ManagedInstanceUpdate has a new parameter hybrid_secondary_usage_detected
  - Model ManagedInstanceUpdate has a new parameter is_general_purpose_v2
  - Model ManagedInstanceUpdate has a new parameter pricing_model
  - Model ManagedInstanceUpdate has a new parameter storage_i_ops
  - Model ManagedInstanceUpdate has a new parameter storage_throughput_m_bps
  - Model ManagedInstanceUpdate has a new parameter virtual_cluster_id

## 4.0.0b14 (2023-12-18)

### Features Added

  - Added operation LongTermRetentionBackupsOperations.begin_change_access_tier
  - Added operation LongTermRetentionBackupsOperations.begin_change_access_tier_by_resource_group
  - Model LongTermRetentionBackup has a new parameter backup_storage_access_tier
  - Model LongTermRetentionBackup has a new parameter is_backup_immutable
  - Model LongTermRetentionPolicy has a new parameter backup_storage_access_tier
  - Model LongTermRetentionPolicy has a new parameter make_backups_immutable

## 4.0.0b13 (2023-11-17)

### Features Added

  - Added operation group JobPrivateEndpointsOperations
  - Model FailoverGroupReadOnlyEndpoint has a new parameter target_server
  - Model FailoverGroupUpdate has a new parameter partner_servers
  - Model InstancePool has a new parameter dns_zone
  - Model InstancePool has a new parameter maintenance_configuration_id
  - Model InstancePoolUpdate has a new parameter dns_zone
  - Model InstancePoolUpdate has a new parameter license_type
  - Model InstancePoolUpdate has a new parameter maintenance_configuration_id
  - Model InstancePoolUpdate has a new parameter sku
  - Model InstancePoolUpdate has a new parameter subnet_id
  - Model InstancePoolUpdate has a new parameter v_cores
  - Model Server has a new parameter is_i_pv6_enabled
  - Model ServerUpdate has a new parameter is_i_pv6_enabled

## 4.0.0b12 (2023-08-30)

### Features Added

  - Model Database has a new parameter encryption_protector_auto_rotation
  - Model Database has a new parameter free_limit_exhaustion_behavior
  - Model Database has a new parameter use_free_limit
  - Model DatabaseUpdate has a new parameter encryption_protector_auto_rotation
  - Model DatabaseUpdate has a new parameter free_limit_exhaustion_behavior
  - Model DatabaseUpdate has a new parameter use_free_limit

## 4.0.0b11 (2023-07-28)

### Features Added

  - Added operation FailoverGroupsOperations.begin_try_planned_before_forced_failover
  - Model PrivateEndpointConnection has a new parameter group_ids
  - Model SqlVulnerabilityAssessmentScanRecord has a new parameter last_scan_time

## 4.0.0b10 (2023-04-11)

### Features Added

  - Model ManagedDatabase has a new parameter is_ledger_on
  - Model ManagedDatabaseUpdate has a new parameter is_ledger_on

## 4.0.0b9 (2023-03-24)

### Features Added

  - Model ElasticPool has a new parameter availability_zone
  - Model ElasticPool has a new parameter min_capacity
  - Model ElasticPool has a new parameter preferred_enclave_type
  - Model ElasticPoolUpdate has a new parameter availability_zone
  - Model ElasticPoolUpdate has a new parameter min_capacity
  - Model ElasticPoolUpdate has a new parameter preferred_enclave_type

## 4.0.0b8 (2023-02-17)

### Features Added

  - Added operation ManagedInstancesOperations.begin_start
  - Added operation ManagedInstancesOperations.begin_stop
  - Added operation ManagedInstancesOperations.list_outbound_network_dependencies_by_managed_instance
  - Added operation ServersOperations.begin_refresh_status
  - Added operation group DatabaseEncryptionProtectorsOperations
  - Added operation group ManagedLedgerDigestUploadsOperations
  - Added operation group ServerConfigurationOptionsOperations
  - Added operation group StartStopManagedInstanceSchedulesOperations
  - Model Database has a new parameter availability_zone
  - Model Database has a new parameter encryption_protector
  - Model Database has a new parameter keys
  - Model Database has a new parameter manual_cutover
  - Model Database has a new parameter perform_cutover
  - Model DatabaseUpdate has a new parameter encryption_protector
  - Model DatabaseUpdate has a new parameter keys
  - Model DatabaseUpdate has a new parameter manual_cutover
  - Model DatabaseUpdate has a new parameter perform_cutover
  - Model PrivateEndpointConnectionProperties has a new parameter group_ids
  - Model RecoverableDatabase has a new parameter keys
  - Model RecoverableDatabaseListResult has a new parameter next_link
  - Model RestorableDroppedDatabase has a new parameter keys
  - Model Server has a new parameter external_governance_status
  - Model ServerUpdate has a new parameter external_governance_status
  - Operation DatabasesOperations.get has a new optional parameter expand
  - Operation DatabasesOperations.get has a new optional parameter filter
  - Operation RecoverableDatabasesOperations.get has a new optional parameter expand
  - Operation RecoverableDatabasesOperations.get has a new optional parameter filter
  - Operation RestorableDroppedDatabasesOperations.get has a new optional parameter expand
  - Operation RestorableDroppedDatabasesOperations.get has a new optional parameter filter

### Breaking Changes

  - Renamed operation TransparentDataEncryptionsOperations.create_or_update to TransparentDataEncryptionsOperations.begin_create_or_update

## 4.0.0b7 (2023-01-29)

### Features Added

  - Model InstanceFailoverGroup has a new parameter secondary_type
  - Model ManagedDatabase has a new parameter cross_subscription_restorable_dropped_database_id
  - Model ManagedDatabase has a new parameter cross_subscription_source_database_id
  - Model ManagedDatabase has a new parameter cross_subscription_target_managed_instance_id
  - Model ManagedDatabaseUpdate has a new parameter cross_subscription_restorable_dropped_database_id
  - Model ManagedDatabaseUpdate has a new parameter cross_subscription_source_database_id
  - Model ManagedDatabaseUpdate has a new parameter cross_subscription_target_managed_instance_id

## 4.0.0b6 (2022-12-30)

### Features Added

  - Model Database has a new parameter preferred_enclave_type
  - Model DatabaseUpdate has a new parameter preferred_enclave_type

## 4.0.0b5 (2022-11-10)

### Features Added

  - Model ServerDevOpsAuditingSettings has a new parameter is_managed_identity_in_use

## 4.0.0b4 (2022-09-29)

### Features Added

  - Added operation ManagedDatabasesOperations.begin_cancel_move
  - Added operation ManagedDatabasesOperations.begin_complete_move
  - Added operation ManagedDatabasesOperations.begin_start_move
  - Added operation group DatabaseSqlVulnerabilityAssessmentBaselinesOperations
  - Added operation group DatabaseSqlVulnerabilityAssessmentExecuteScanOperations
  - Added operation group DatabaseSqlVulnerabilityAssessmentRuleBaselinesOperations
  - Added operation group DatabaseSqlVulnerabilityAssessmentScanResultOperations
  - Added operation group DatabaseSqlVulnerabilityAssessmentScansOperations
  - Added operation group DatabaseSqlVulnerabilityAssessmentsSettingsOperations
  - Added operation group ManagedDatabaseAdvancedThreatProtectionSettingsOperations
  - Added operation group ManagedDatabaseMoveOperationsOperations
  - Added operation group ManagedInstanceAdvancedThreatProtectionSettingsOperations
  - Added operation group ManagedInstanceDtcsOperations
  - Added operation group SqlVulnerabilityAssessmentBaselineOperations
  - Added operation group SqlVulnerabilityAssessmentBaselinesOperations
  - Added operation group SqlVulnerabilityAssessmentExecuteScanOperations
  - Added operation group SqlVulnerabilityAssessmentRuleBaselineOperations
  - Added operation group SqlVulnerabilityAssessmentRuleBaselinesOperations
  - Added operation group SqlVulnerabilityAssessmentScanResultOperations
  - Added operation group SqlVulnerabilityAssessmentScansOperations
  - Added operation group SqlVulnerabilityAssessmentsOperations
  - Added operation group SqlVulnerabilityAssessmentsSettingsOperations
  - Added operation group SynapseLinkWorkspacesOperations
  - Model ManagedDatabase has a new parameter storage_container_identity
  - Model ManagedDatabaseRestoreDetailsResult has a new parameter current_backup_type
  - Model ManagedDatabaseRestoreDetailsResult has a new parameter current_restore_plan_size_mb
  - Model ManagedDatabaseRestoreDetailsResult has a new parameter current_restored_size_mb
  - Model ManagedDatabaseRestoreDetailsResult has a new parameter diff_backup_sets
  - Model ManagedDatabaseRestoreDetailsResult has a new parameter full_backup_sets
  - Model ManagedDatabaseRestoreDetailsResult has a new parameter log_backup_sets
  - Model ManagedDatabaseRestoreDetailsResult has a new parameter number_of_files_queued
  - Model ManagedDatabaseRestoreDetailsResult has a new parameter number_of_files_restored
  - Model ManagedDatabaseRestoreDetailsResult has a new parameter number_of_files_restoring
  - Model ManagedDatabaseRestoreDetailsResult has a new parameter number_of_files_skipped
  - Model ManagedDatabaseRestoreDetailsResult has a new parameter number_of_files_unrestorable
  - Model ManagedDatabaseRestoreDetailsResult has a new parameter type_properties_type
  - Model ManagedDatabaseUpdate has a new parameter storage_container_identity
  - Model VirtualCluster has a new parameter version
  - Model VirtualClusterUpdate has a new parameter version

### Breaking Changes

  - Model VirtualCluster no longer has parameter family
  - Model VirtualCluster no longer has parameter maintenance_configuration_id
  - Model VirtualClusterUpdate no longer has parameter family
  - Model VirtualClusterUpdate no longer has parameter maintenance_configuration_id
  - Renamed operation ReplicationLinksOperations.delete to ReplicationLinksOperations.begin_delete
  - Renamed operation VirtualClustersOperations.update_dns_servers to VirtualClustersOperations.begin_update_dns_servers

## 4.0.0b3 (2022-07-06)

**Features**

  - Added operation group DatabaseAdvancedThreatProtectionSettingsOperations
  - Added operation group EndpointCertificatesOperations
  - Added operation group ManagedServerDnsAliasesOperations
  - Added operation group ServerAdvancedThreatProtectionSettingsOperations
  - Model Database has a new parameter source_resource_id
  - Model DatabaseBlobAuditingPolicy has a new parameter is_managed_identity_in_use
  - Model ExtendedDatabaseBlobAuditingPolicy has a new parameter is_managed_identity_in_use
  - Model ExtendedServerBlobAuditingPolicy has a new parameter is_managed_identity_in_use
  - Model ServerBlobAuditingPolicy has a new parameter is_managed_identity_in_use

**Breaking changes**

  - Model Database no longer has parameter primary_delegated_identity_client_id
  - Model DatabaseIdentity no longer has parameter delegated_resources
  - Model DatabaseUpdate no longer has parameter primary_delegated_identity_client_id
  - Removed operation ReplicationLinksOperations.begin_unlink

## 4.0.0b2 (2022-03-08)

**Features**

  - Added operation group DistributedAvailabilityGroupsOperations
  - Added operation group IPv6FirewallRulesOperations
  - Added operation group ServerTrustCertificatesOperations
  - Model ElasticPool has a new parameter high_availability_replica_count
  - Model ElasticPoolUpdate has a new parameter high_availability_replica_count

**Breaking changes**

  - Removed operation group OperationsHealthOperations

## 4.0.0b1 (2021-12-21)

**Features**

  - Model ManagedInstanceUpdate has a new parameter current_backup_storage_redundancy
  - Model ManagedInstanceUpdate has a new parameter requested_backup_storage_redundancy
  - Model ManagedInstanceUpdate has a new parameter service_principal
  - Model Database has a new parameter identity
  - Model Database has a new parameter primary_delegated_identity_client_id
  - Model Database has a new parameter federated_client_id
  - Model ManagedInstance has a new parameter current_backup_storage_redundancy
  - Model ManagedInstance has a new parameter requested_backup_storage_redundancy
  - Model ManagedInstance has a new parameter service_principal
  - Model DatabaseUpdate has a new parameter identity
  - Model DatabaseUpdate has a new parameter primary_delegated_identity_client_id
  - Model DatabaseUpdate has a new parameter federated_client_id
  - Added operation TransparentDataEncryptionsOperations.list_by_database
  - Added operation LedgerDigestUploadsOperations.begin_create_or_update
  - Added operation LedgerDigestUploadsOperations.begin_disable
  - Added operation ServerConnectionPoliciesOperations.list_by_server
  - Added operation ServerConnectionPoliciesOperations.begin_create_or_update

**Breaking changes**

  - Operation TransparentDataEncryptionsOperations.create_or_update has a new signature
  - Operation TransparentDataEncryptionsOperations.get has a new signature
  - Model ManagedInstanceUpdate no longer has parameter storage_account_type
  - Model ManagedInstance no longer has parameter storage_account_type
  - Model RestorableDroppedDatabase no longer has parameter elastic_pool_id
  - Removed operation LedgerDigestUploadsOperations.create_or_update
  - Removed operation LedgerDigestUploadsOperations.disable
  - Removed operation ServerConnectionPoliciesOperations.create_or_update
  - Removed operation group TransparentDataEncryptionActivitiesOperations

## 3.0.1 (2021-07-15)

**Bugfixes**

  - Fix default setting for blob_auditing_policy_name

## 3.0.0 (2021-06-18)

**Features**

  - Model Server has a new parameter federated_client_id
  - Model Server has a new parameter restrict_outbound_network_access
  - Model ServerUpdate has a new parameter federated_client_id
  - Model ServerUpdate has a new parameter restrict_outbound_network_access
  - Model BackupShortTermRetentionPolicy has a new parameter diff_backup_interval_in_hours

**Breaking changes**

  - Operation ReplicationLinksOperations.get has a new signature

## 2.1.0 (2021-05-24)

 - Add resource identity

## 2.0.0 (2021-05-13)

**Features**

  - Model LongTermRetentionBackup has a new parameter requested_backup_storage_redundancy
  - Model LongTermRetentionBackup has a new parameter backup_storage_redundancy
  - Model ManagedInstanceKey has a new parameter auto_rotation_enabled
  - Model ManagedInstanceEncryptionProtector has a new parameter auto_rotation_enabled
  - Model Database has a new parameter is_infra_encryption_enabled
  - Model Database has a new parameter is_ledger_on
  - Model Database has a new parameter secondary_type
  - Model Database has a new parameter current_backup_storage_redundancy
  - Model Database has a new parameter high_availability_replica_count
  - Model Database has a new parameter maintenance_configuration_id
  - Model Database has a new parameter requested_backup_storage_redundancy
  - Model ReplicationLink has a new parameter link_type
  - Model ServerUpdate has a new parameter primary_user_assigned_identity_id
  - Model ServerUpdate has a new parameter administrators
  - Model ServerUpdate has a new parameter identity
  - Model ServerUpdate has a new parameter key_id
  - Model ServerUpdate has a new parameter workspace_feature
  - Model DatabaseUpdate has a new parameter is_infra_encryption_enabled
  - Model DatabaseUpdate has a new parameter is_ledger_on
  - Model DatabaseUpdate has a new parameter secondary_type
  - Model DatabaseUpdate has a new parameter current_backup_storage_redundancy
  - Model DatabaseUpdate has a new parameter high_availability_replica_count
  - Model DatabaseUpdate has a new parameter maintenance_configuration_id
  - Model DatabaseUpdate has a new parameter requested_backup_storage_redundancy
  - Model ManagedInstance has a new parameter primary_user_assigned_identity_id
  - Model ManagedInstance has a new parameter administrators
  - Model ManagedInstance has a new parameter key_id
  - Model ManagedInstance has a new parameter zone_redundant
  - Model ManagedInstance has a new parameter private_endpoint_connections
  - Model ServerKey has a new parameter auto_rotation_enabled
  - Model ExtendedServerBlobAuditingPolicy has a new parameter is_devops_audit_enabled
  - Model ServiceObjectiveCapability has a new parameter supported_maintenance_configurations
  - Model EncryptionProtector has a new parameter auto_rotation_enabled
  - Model FirewallRuleListResult has a new parameter next_link
  - Model ManagedInstanceUpdate has a new parameter primary_user_assigned_identity_id
  - Model ManagedInstanceUpdate has a new parameter administrators
  - Model ManagedInstanceUpdate has a new parameter identity
  - Model ManagedInstanceUpdate has a new parameter key_id
  - Model ManagedInstanceUpdate has a new parameter private_endpoint_connections
  - Model ManagedInstanceUpdate has a new parameter zone_redundant
  - Model ElasticPoolUpdate has a new parameter maintenance_configuration_id
  - Model SyncMember has a new parameter private_endpoint_name
  - Model ElasticPool has a new parameter maintenance_configuration_id
  - Model ManagedInstanceVcoresCapability has a new parameter supported_maintenance_configurations
  - Model ManagedInstanceLongTermRetentionBackup has a new parameter backup_storage_redundancy
  - Model ServerSecurityAlertPolicy has a new parameter system_data
  - Model ManagedInstanceEditionCapability has a new parameter supported_storage_capabilities
  - Model ManagedInstanceEditionCapability has a new parameter zone_redundant
  - Model ServerBlobAuditingPolicy has a new parameter is_devops_audit_enabled
  - Model ElasticPoolPerformanceLevelCapability has a new parameter supported_maintenance_configurations
  - Model RestorableDroppedDatabase has a new parameter backup_storage_redundancy
  - Model RestorableDroppedDatabase has a new parameter tags
  - Model RestorableDroppedDatabase has a new parameter sku
  - Model RestorableDroppedDatabase has a new parameter elastic_pool_id
  - Model DatabaseSecurityAlertPolicy has a new parameter creation_time
  - Model DatabaseSecurityAlertPolicy has a new parameter system_data
  - Model SyncGroup has a new parameter conflict_logging_retention_in_days
  - Model SyncGroup has a new parameter private_endpoint_name
  - Model SyncGroup has a new parameter sku
  - Model SyncGroup has a new parameter enable_conflict_logging
  - Model VirtualClusterUpdate has a new parameter maintenance_configuration_id
  - Model PrivateLinkResourceProperties has a new parameter required_zone_names
  - Model VirtualCluster has a new parameter maintenance_configuration_id
  - Model ManagedServerSecurityAlertPolicy has a new parameter system_data
  - Model DatabaseUsage has a new parameter type
  - Model DatabaseUsage has a new parameter id
  - Model Server has a new parameter primary_user_assigned_identity_id
  - Model Server has a new parameter key_id
  - Model Server has a new parameter administrators
  - Model Server has a new parameter workspace_feature
  - Model SensitivityLabel has a new parameter column_name
  - Model SensitivityLabel has a new parameter schema_name
  - Model SensitivityLabel has a new parameter managed_by
  - Model SensitivityLabel has a new parameter table_name
  - Added operation VirtualClustersOperations.update_dns_servers
  - Added operation ServersOperations.begin_import_database
  - Added operation DatabasesOperations.list_inaccessible_by_server
  - Added operation FirewallRulesOperations.replace
  - Added operation ReplicationLinksOperations.list_by_server
  - Added operation SensitivityLabelsOperations.update
  - Added operation ManagedInstancesOperations.list_by_managed_instance
  - Added operation ManagedDatabaseSensitivityLabelsOperations.update
  - Added operation LongTermRetentionBackupsOperations.begin_update
  - Added operation LongTermRetentionBackupsOperations.begin_copy
  - Added operation LongTermRetentionBackupsOperations.begin_copy_by_resource_group
  - Added operation LongTermRetentionBackupsOperations.begin_update_by_resource_group
  - Added operation group DatabaseSchemasOperations
  - Added operation group DatabaseExtensionsOperations
  - Added operation group ManagedInstancePrivateEndpointConnectionsOperations
  - Added operation group DeletedServersOperations
  - Added operation group ManagedDatabaseTablesOperations
  - Added operation group MaintenanceWindowOptionsOperations
  - Added operation group DatabaseSecurityAlertPoliciesOperations
  - Added operation group ServerTrustGroupsOperations
  - Added operation group ManagedInstanceAzureADOnlyAuthenticationsOperations
  - Added operation group SqlAgentOperations
  - Added operation group TimeZonesOperations
  - Added operation group ManagedInstancePrivateLinkResourcesOperations
  - Added operation group RecommendedSensitivityLabelsOperations
  - Added operation group DatabaseTablesOperations
  - Added operation group ServerAdvisorsOperations
  - Added operation group ManagedDatabaseSecurityEventsOperations
  - Added operation group ServerOperationsOperations
  - Added operation group DatabaseAdvisorsOperations
  - Added operation group DatabaseColumnsOperations
  - Added operation group DataWarehouseUserActivitiesOperations
  - Added operation group OutboundFirewallRulesOperations
  - Added operation group ManagedDatabaseSchemasOperations
  - Added operation group DatabaseRecommendedActionsOperations
  - Added operation group LongTermRetentionPoliciesOperations
  - Added operation group ManagedDatabaseQueriesOperations
  - Added operation group ManagedDatabaseRecommendedSensitivityLabelsOperations
  - Added operation group ManagedDatabaseTransparentDataEncryptionOperations
  - Added operation group ServerDevOpsAuditSettingsOperations
  - Added operation group OperationsHealthOperations
  - Added operation group LedgerDigestUploadsOperations
  - Added operation group MaintenanceWindowsOperations
  - Added operation group ManagedDatabaseColumnsOperations

**Breaking changes**

  - Operation RestorableDroppedDatabasesOperations.get has a new signature
  - Operation ReplicationLinksOperations.get has a new signature
  - Parameter old_server_dns_alias_id of model ServerDnsAliasAcquisition is now required
  - Operation SensitivityLabelsOperations.list_recommended_by_database has a new signature
  - Operation ManagedDatabaseSensitivityLabelsOperations.list_recommended_by_database has a new signature
  - Operation DatabasesOperations.begin_import_method has a new signature
  - Operation DatabasesOperations.list_by_server has a new signature
  - Operation ManagedDatabaseSensitivityLabelsOperations.list_current_by_database has a new signature
  - Operation ManagedDatabaseSensitivityLabelsOperations.list_current_by_database has a new signature
  - Operation ManagedDatabaseSensitivityLabelsOperations.list_recommended_by_database has a new signature
  - Operation ManagedInstanceAdministratorsOperations.begin_create_or_update has a new signature
  - Operation ManagedInstanceAdministratorsOperations.begin_delete has a new signature
  - Operation ManagedInstanceAdministratorsOperations.get has a new signature
  - Operation ManagedInstancesOperations.get has a new signature
  - Operation ManagedInstancesOperations.list has a new signature
  - Operation ManagedInstancesOperations.list_by_instance_pool has a new signature
  - Operation ManagedInstancesOperations.list_by_resource_group has a new signature
  - Operation SensitivityLabelsOperations.list_current_by_database has a new signature
  - Operation SensitivityLabelsOperations.list_current_by_database has a new signature
  - Operation SensitivityLabelsOperations.list_recommended_by_database has a new signature
  - Operation ServersOperations.get has a new signature
  - Operation ServersOperations.list has a new signature
  - Operation ServersOperations.list_by_resource_group has a new signature
  - Model BackupShortTermRetentionPolicy no longer has parameter diff_backup_interval_in_hours
  - Model Database no longer has parameter read_replica_count
  - Model ReplicationLink no longer has parameter location
  - Model DatabaseUpdate no longer has parameter read_replica_count
  - Model FirewallRule no longer has parameter kind
  - Model FirewallRule no longer has parameter location
  - Model RestorableDroppedDatabase no longer has parameter service_level_objective
  - Model RestorableDroppedDatabase no longer has parameter edition
  - Model RestorableDroppedDatabase no longer has parameter elastic_pool_name
  - Model DatabaseSecurityAlertPolicy no longer has parameter use_server_default
  - Model DatabaseSecurityAlertPolicy no longer has parameter kind
  - Model DatabaseSecurityAlertPolicy no longer has parameter location
  - Model DatabaseUsage no longer has parameter resource_name
  - Model DatabaseUsage no longer has parameter next_reset_time
  - Removed operation DatabasesOperations.begin_create_import_operation
  - Model DatabaseUsageListResult has a new signature
  - Model RestorableDroppedDatabaseListResult has a new signature
  - Removed operation group RecommendedElasticPoolsOperations
  - Removed operation group BackupLongTermRetentionPoliciesOperations
  - Removed operation group DatabaseThreatDetectionPoliciesOperations
  - Removed operation group ServiceTierAdvisorsOperations

## 1.0.0 (2020-11-24)

- GA release

## 1.0.0b1 (2020-10-13)

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

## 0.21.0 (2020-09-03)

**Features**

  - Model DatabaseUpdate has a new parameter storage_account_type
  - Model Database has a new parameter storage_account_type
  - Model BackupShortTermRetentionPolicy has a new parameter diff_backup_interval_in_hours
  - Model ManagedInstance has a new parameter storage_account_type
  - Model ManagedInstance has a new parameter provisioning_state
  - Model ManagedInstanceUpdate has a new parameter storage_account_type
  - Model ManagedInstanceUpdate has a new parameter provisioning_state
  - Added operation DatabasesOperations.list_inaccessible_by_server
  - Added operation ServersOperations.import_database
  - Added operation group ImportExportOperations
  - Added operation group ServerAzureADOnlyAuthenticationsOperations
  - Added operation group ManagedInstanceAzureADOnlyAuthenticationsOperations

**Breaking changes**

  - Operation BackupShortTermRetentionPoliciesOperations.create_or_update has a new signature
  - Operation BackupShortTermRetentionPoliciesOperations.update has a new signature
  - Removed operation DatabasesOperations.import_method
  - Removed operation DatabasesOperations.create_import_operation
  - Removed operation ServerAzureADAdministratorsOperations.disable_azure_ad_only_authentication

## 0.20.0 (2020-06-22)

**Features**

  - Model ManagedDatabase has a new parameter last_backup_name
  - Model ManagedDatabase has a new parameter auto_complete_restore
  - Model ManagedDatabaseUpdate has a new parameter last_backup_name
  - Model ManagedDatabaseUpdate has a new parameter auto_complete_restore
  - Model ManagedInstanceOperation has a new parameter operation_parameters
  - Model ManagedInstanceOperation has a new parameter operation_steps

## 0.19.0 (2020-06-22)

**Features**

  - Model SyncGroup has a new parameter use_private_link_connection
  - Model ManagedInstanceUpdate has a new parameter maintenance_configuration_id
  - Model SyncMember has a new parameter use_private_link_connection
  - Model SyncMember has a new parameter sync_member_azure_database_resource_id
  - Model ManagedInstance has a new parameter maintenance_configuration_id
  - Added operation ExtendedDatabaseBlobAuditingPoliciesOperations.list_by_database
  - Added operation ManagedInstancesOperations.failover
  - Added operation ReplicationLinksOperations.unlink
  - Added operation ExtendedServerBlobAuditingPoliciesOperations.list_by_server

# 0.18.0 (2020-03-23)

**Features**

  - Added operation group ManagedInstanceOperations

# 0.17.0 (2020-03-02)

**Features**

  - Model ManagedInstanceUpdate has a new parameter minimal_tls_version
  - Model ServerAzureADAdministrator has a new parameter azure_ad_only_authentication
  - Model ManagedDatabase has a new parameter long_term_retention_backup_resource_id
  - Model ManagedDatabaseUpdate has a new parameter long_term_retention_backup_resource_id
  - Model SensitivityLabel has a new parameter rank
  - Model ServerUpdate has a new parameter private_endpoint_connections
  - Model ServerUpdate has a new parameter minimal_tls_version
  - Model ServerUpdate has a new parameter public_network_access
  - Model Server has a new parameter private_endpoint_connections
  - Model Server has a new parameter minimal_tls_version
  - Model Server has a new parameter public_network_access
  - Model ManagedInstance has a new parameter minimal_tls_version
  - Added operation ServerAzureADAdministratorsOperations.disable_azure_ad_only_authentication
  - Added operation ManagedDatabasesOperations.list_inaccessible_by_instance
  - Added operation group ManagedInstanceLongTermRetentionPoliciesOperations
  - Added operation group LongTermRetentionManagedInstanceBackupsOperations

## 0.16.0 (2019-12-17)

**Features**

  - Model ExtendedServerBlobAuditingPolicy has a new parameter
    queue_delay_ms
  - Model EditionCapability has a new parameter read_scale
  - Model EditionCapability has a new parameter
    supported_storage_capabilities
  - Model ServiceObjectiveCapability has a new parameter compute_model
  - Model ServiceObjectiveCapability has a new parameter
    supported_auto_pause_delay
  - Model ServiceObjectiveCapability has a new parameter zone_redundant
  - Model ServiceObjectiveCapability has a new parameter
    supported_min_capacities
  - Model ManagedInstanceVersionCapability has a new parameter
    supported_instance_pool_editions
  - Model DatabaseBlobAuditingPolicy has a new parameter
    queue_delay_ms
  - Model ExtendedDatabaseBlobAuditingPolicy has a new parameter
    queue_delay_ms
  - Model ManagedInstanceVcoresCapability has a new parameter
    supported_storage_sizes
  - Model ManagedInstanceVcoresCapability has a new parameter
    instance_pool_supported
  - Model ManagedInstanceVcoresCapability has a new parameter
    standalone_supported
  - Model ManagedInstanceVcoresCapability has a new parameter
    included_max_size
  - Model ServerBlobAuditingPolicy has a new parameter queue_delay_ms
  - Model ElasticPoolPerformanceLevelCapability has a new parameter
    zone_redundant
  - Added operation group WorkloadGroupsOperations
  - Added operation group WorkloadClassifiersOperations

**Breaking changes**

  - Operation ServerAzureADAdministratorsOperations.create_or_update
    has a new signature
  - Model ManagedInstanceFamilyCapability no longer has parameter
    supported_storage_sizes
  - Model ManagedInstanceFamilyCapability no longer has parameter
    included_max_size

## 0.15.0 (2019-11-12)

**Breaking changes**

  - Operation DatabasesOperations.failover has a new signature
  - Operation ManagedInstanceAdministratorsOperations.get has a new
    signature
  - Operation ManagedInstanceAdministratorsOperations.delete has a new
    signature
  - Operation ManagedInstanceAdministratorsOperations.create_or_update
    has a new signature

## 0.14.0 (2019-10-04)

**Features**

  - Added operation
    ServerBlobAuditingPoliciesOperations.list_by_server
  - Added operation ManagedDatabasesOperations.complete_restore
  - Added operation
    DatabaseBlobAuditingPoliciesOperations.list_by_database
  - Added operation group ManagedDatabaseRestoreDetailsOperations

## 0.13.0 (2019-09-03)

**Features**

  - Model ManagedInstanceUpdate has a new parameter
    source_managed_instance_id
  - Model ManagedInstanceUpdate has a new parameter instance_pool_id
  - Model ManagedInstanceUpdate has a new parameter
    restore_point_in_time
  - Model ManagedInstanceUpdate has a new parameter
    managed_instance_create_mode
  - Model SensitivityLabel has a new parameter is_disabled
  - Model Database has a new parameter paused_date
  - Model Database has a new parameter read_replica_count
  - Model Database has a new parameter resumed_date
  - Model Database has a new parameter auto_pause_delay
  - Model Database has a new parameter min_capacity
  - Model ManagedInstance has a new parameter
    source_managed_instance_id
  - Model ManagedInstance has a new parameter instance_pool_id
  - Model ManagedInstance has a new parameter restore_point_in_time
  - Model ManagedInstance has a new parameter
    managed_instance_create_mode
  - Model DatabaseUpdate has a new parameter paused_date
  - Model DatabaseUpdate has a new parameter read_replica_count
  - Model DatabaseUpdate has a new parameter resumed_date
  - Model DatabaseUpdate has a new parameter auto_pause_delay
  - Model DatabaseUpdate has a new parameter min_capacity
  - Added operation
    ManagedInstanceEncryptionProtectorsOperations.revalidate
  - Added operation
    ManagedDatabaseSensitivityLabelsOperations.enable_recommendation
  - Added operation
    ManagedDatabaseSensitivityLabelsOperations.disable_recommendation
  - Added operation ElasticPoolsOperations.failover
  - Added operation ManagedInstancesOperations.list_by_instance_pool
  - Added operation DatabasesOperations.failover
  - Added operation
    LongTermRetentionBackupsOperations.get_by_resource_group
  - Added operation
    LongTermRetentionBackupsOperations.list_by_resource_group_server
  - Added operation
    LongTermRetentionBackupsOperations.delete_by_resource_group
  - Added operation
    LongTermRetentionBackupsOperations.list_by_resource_group_location
  - Added operation
    LongTermRetentionBackupsOperations.list_by_resource_group_database
  - Added operation SensitivityLabelsOperations.enable_recommendation
  - Added operation SensitivityLabelsOperations.disable_recommendation
  - Added operation EncryptionProtectorsOperations.revalidate
  - Added operation group InstancePoolsOperations
  - Added operation group ManagedInstanceAdministratorsOperations
  - Added operation group UsagesOperations
  - Added operation group PrivateLinkResourcesOperations
  - Added operation group PrivateEndpointConnectionsOperations

**Breaking changes**

  - Operation
    ManagedDatabaseSensitivityLabelsOperations.list_recommended_by_database
    has a new signature
  - Operation
    SensitivityLabelsOperations.list_recommended_by_database has a
    new signature
  - Operation EncryptionProtectorsOperations.create_or_update has a
    new signature

**General breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if from some import. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - SqlManagementClient cannot be imported from
    `azure.mgmt.sql.sql_management_client` anymore (import from
    `azure.mgmt.sqlmanagement` works like before)
  - SqlManagementClientConfiguration import has been moved from
    `azure.mgmt.sqlmanagement.sql_management_client` to
    `azure.mgmt.sqlmanagement`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.sqlmanagement.models.my_class` (import
    from `azure.mgmt.sqlmanagement.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.sqlmanagement.operations.my_class_operations`
    (import from `azure.mgmt.sqlmanagement.operations` works like
    before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.12.0 (2019-03-28)

**Features**

  - Model ManagedDatabase has a new parameter recoverable_database_id
  - Model ManagedDatabase has a new parameter
    restorable_dropped_database_id
  - Model ServerSecurityAlertPolicy has a new parameter creation_time
  - Model ManagedInstanceUpdate has a new parameter
    public_data_endpoint_enabled
  - Model ManagedInstanceUpdate has a new parameter proxy_override
  - Model ManagedInstanceUpdate has a new parameter timezone_id
  - Model ManagedDatabaseUpdate has a new parameter
    recoverable_database_id
  - Model ManagedDatabaseUpdate has a new parameter
    restorable_dropped_database_id
  - Model ManagedInstance has a new parameter
    public_data_endpoint_enabled
  - Model ManagedInstance has a new parameter proxy_override
  - Model ManagedInstance has a new parameter timezone_id
  - Added operation group ManagedServerSecurityAlertPoliciesOperations
  - Added operation group VirtualClustersOperations
  - Added operation group
    ManagedRestorableDroppedDatabaseBackupShortTermRetentionPoliciesOperations
  - Added operation group RestorableDroppedManagedDatabasesOperations
  - Added operation group ManagedDatabaseSensitivityLabelsOperations
  - Added operation group RecoverableManagedDatabasesOperations
  - Added operation group ServerVulnerabilityAssessmentsOperations
  - Added operation group
    ManagedInstanceVulnerabilityAssessmentsOperations
  - Added operation group ManagedDatabaseSecurityAlertPoliciesOperations
  - Added operation group SensitivityLabelsOperations

## 0.11.0 (2018-11-08)

**Features**

  - Model ServerBlobAuditingPolicy has a new parameter
    is_azure_monitor_target_enabled
  - Model ExtendedServerBlobAuditingPolicy has a new parameter
    is_azure_monitor_target_enabled
  - Model DatabaseBlobAuditingPolicy has a new parameter
    is_azure_monitor_target_enabled
  - Model ExtendedDatabaseBlobAuditingPolicy has a new parameter
    is_azure_monitor_target_enabled
  - Added operation
    DatabaseVulnerabilityAssessmentsOperations.list_by_database
  - Added operation
    ManagedDatabaseVulnerabilityAssessmentsOperations.list_by_database
  - Added operation group
    ManagedBackupShortTermRetentionPoliciesOperations

## 0.10.0 (2018-10-18)

**Features**

  - Model DatabaseVulnerabilityAssessment has a new parameter
    storage_account_access_key
  - Model ManagedInstanceUpdate has a new parameter dns_zone_partner
  - Model ManagedInstanceUpdate has a new parameter collation
  - Model ManagedInstanceUpdate has a new parameter dns_zone
  - Model ManagedInstance has a new parameter dns_zone_partner
  - Model ManagedInstance has a new parameter collation
  - Model ManagedInstance has a new parameter dns_zone
  - Added operation
    BackupShortTermRetentionPoliciesOperations.list_by_database
  - Added operation group
    ManagedDatabaseVulnerabilityAssessmentsOperations
  - Added operation group ExtendedDatabaseBlobAuditingPoliciesOperations
  - Added operation group TdeCertificatesOperations
  - Added operation group ManagedInstanceKeysOperations
  - Added operation group ServerBlobAuditingPoliciesOperations
  - Added operation group ManagedInstanceEncryptionProtectorsOperations
  - Added operation group ExtendedServerBlobAuditingPoliciesOperations
  - Added operation group ServerSecurityAlertPoliciesOperations
  - Added operation group
    ManagedDatabaseVulnerabilityAssessmentScansOperations
  - Added operation group ManagedInstanceTdeCertificatesOperations
  - Added operation group
    ManagedDatabaseVulnerabilityAssessmentRuleBaselinesOperations

**Breaking changes**

  - Operation
    DatabaseVulnerabilityAssessmentRuleBaselinesOperations.delete has a
    new signature
  - Operation DatabaseVulnerabilityAssessmentRuleBaselinesOperations.get
    has a new signature
  - Operation
    DatabaseVulnerabilityAssessmentRuleBaselinesOperations.create_or_update
    has a new signature

**Note**

  - azure-mgmt-nspkg is not installed anymore on Python 3 (PEP420-based
    namespace package)

## 0.9.1 (2018-05-24)

**Features**

  - Managed instances, databases, and failover groups
  - Vulnerability assessments
  - Backup short term retention policies
  - Elastic Jobs

## 0.9.0 (2018-04-25)

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

**SQL Breaking changes**

  -   - Database and ElasticPool now use Sku property for scale and
        tier-related properties. We have made this change in order to
        allow future support of autoscale, and to allow for new
        vCore-based editions.

          - Database.sku has replaced
            Database.requested_service_objective_name and
            Database.edition. Database scale can be set by setting
            Sku.name to the requested service objective name (e.g. S0,
            P1, or GP_Gen4_1), or by setting Sku.name to the sku name
            (e.g. Standard, Premium, or GP_Gen4) and set Sku.capacity
            to the scale measured in DTU or vCores.
          - Database.current_sku has replaced
            Database.service_level_objetive.
          - Database.current_service_objective_id and
            Database.requested_service_objective_id have been
            removed.
          - ElasticPool.sku has replaced ElasticPool.dtu. Elastic pool
            scale can be set by setting Sku.name to the requested sku
            name (e.g. StandardPool, PremiumPool, or GP_Gen4) and
            setting Sku.capacity to the scale measured in DTU or vCores.
          - ElasticPool.per_database_settings has replaced
            ElasticPool.database_dtu_min and
            ElasticPool.database_dtu_max.

  - Database.max_size_bytes is now an integer instead of string.

  - LocationCapabilities tree has been changed in order to support
    capabilities of new vCore-based database and elastic pool editions.

**Features**

  - Added support for List and Cancel operation on Azure database and
    elastic pool REST API
  - Added Long Term Retention V2 commands, including getting backups,
    deleting backups, setting the V2 policies, and getting the V2
    policies
      - Removed support for managing Vaults used for Long Term Retention
        V1
      - Changed BackupLongTermRetentionPolicy class, removing the Long
        Term Retention V1 properties and adding the Long Term Retention
        V2 properties
      - Removed BackupLongTermRetentionPolicyState

## 0.8.6 (2018-03-22)

**Features**

  - Added support for List and Cancel operation on Azure database and
    elastic pool REST API
  - Added support for Auto-tuning REST API

## 0.8.5 (2018-01-18)

**Features**

  - Added support for renaming databases
  - Added missing database editions and service objectives
  - Added ability to list long term retention vaults & policies

## 0.8.4 (2017-11-14)

**Features**

  - Added support for subscription usages

## 0.8.3 (2017-10-24)

**Features**

  - Added support for database zone redundant property
  - Added support for server dns aliases

## 0.8.2 (2017-10-18)

**Features**

  - Added support for state and migration flag properties for SQL Vnet
    rules

## 0.8.1 (2017-10-04)

**Features**

  - Add database.cancel operation
  - Add database.list_by_database

## 0.8.0 (2017-09-07)

**Disclaimer**

We were using a slightly unorthodox convention for some operation ids.
Some resource operations were "nested" inside others, e.g. blob auditing
policies was nested inside databases as in
client.databases.get_blob_auditing_policies(..) instead of the
flattened ARM standard
client.database_blob_auditing_policies.get(...).

This convention has lead to some inconsistencies, makes some APIs
difficult to find, and is at odds with future APIs. For example if we
wanted to implement listing db audit policies by server, continuing the
current convention would be
client.databases.list_blob_auditing_policies_by_server(..) which
makes much less sense than the ARM standard which would
beclient.database_blob_auditing_policies.list_by_server(...)`.

In order to resolve this and provide a good path moving forward, we have
renamed the inconsistent operations to follow the ARM standard. This is
an unfortunate breaking change, but it's best to do now while the SDK is
still in preview and since most of these operations were only recently
added.

**Breaking changes**

  - client.database.get_backup_long_term_retention_policy ->
    client.backup_long_term_retention_policies.get
  - client.database.create_or_update_backup_long_term_retention_policy
    ->
    client.backup_long_term_retention_policies.create_or_update
  - client.servers.create_backup_long_term_retention_vault ->
    client.backup_long_term_retention_vaults.create_or_update
  - client.servers.get_backup_long_term_retention_vault ->
    client.backup_long_term_retention_vaults.get
  - client.database.list_restore_points ->
    client.restore_points.list_by_database
  - client.servers.create_or_update_connection_policy ->
    client.server_connection_policies.create_or_update
  - client.servers.get_connection_policy ->
    client.server_connection_policies.get
  - client.databases.create_or_update_data_masking_policy ->
    client.data_masking_policies.create_or_update
  - client.databases.get_data_masking_policy ->
    client.data_masking_policies.get
  - client.databases.create_or_update_data_masking_rule ->
    client.data_masking_rules.create_or_update
  - client.databases.get_data_masking_rule ->
    client.data_masking_rules.get
  - client.databases.list_data_masking_rules ->
    client.data_masking_rules.list_by_database
  - client.databases.get_threat_detection_policy ->
    client.database_threat_detection_policies.get
  - client.databases.create_or_update_threat_detection_policy ->
    client.database_threat_detection_policies.create_or_update
  - client.databases.create_or_update_geo_backup_policy ->
    client.geo_backup_policies.create_or_update
  - client.databases.get_geo_backup_policy ->
    client.geo_backup_policies.get
  - client.databases.list_geo_backup_policies ->
    client.geo_backup_policies.list_by_database
  - client.databases.delete_replication_link ->
    client.replication_links.delete
  - client.databases.get_replication_link ->
    client.replication_links.get
  - client.databases.failover_replication_link ->
    client.replication_links.failover
  - client.databases.failover_replication_link_allow_data_loss ->
    client.replication_links.failover_allow_data_loss
  - client.databases.list_replication_links ->
    client.replication_links.list_by_database
  - client.server_azure_ad_administrators.list ->
    client.server_azure_ad_administrators.list_by_server
  - client.servers.get_service_objective ->
    client.service_objectives.get
  - client.servers.list_service_objectives ->
    client.service_objectives.list_by_server
  - client.elastic_pools.list_activity ->
    client.elastic_pool_activities.list_by_elastic_pool
  - client.elastic_pools.list_database_activity ->
    client.elastic_pool_database_activities.list_by_elastic_pool
  - client.elastic_pools.get_database ->
    client.databases.get_by_elastic_pool
  - client.elastic_pools.list_databases ->
    client.databases.list_by_elastic_pool
  - client.recommended_elastic_pools.get_databases ->
    client.databases.get_by_recommended_elastic_pool
  - client.recommended_elastic_pools.list_databases ->
    client.databases.list_by_recommended_elastic_pool
  - client.databases.get_service_tier_advisor ->
    client.service_tier_advisors.get
  - client.databases.list_service_tier_advisors ->
    client.service_tier_advisors.list_by_database
  - client.databases.create_or_update_transparent_data_encryption_configuration
    -> client.transparent_data_encryptions.create_or_update
  - client.databases.get_transparent_data_encryption_configuration
    -> client.transparent_data_encryptions.get
  - client.databases.list_transparent_data_encryption_activity ->
    client.transparent_data_encryption_activities.list_by_configuration
  - client.servers.list_usages ->
    client.server_usages.list_by_server
  - client.databases.list_usages ->
    client.database_usages.list_by_database
  - client.databases.get_blob_auditing_policy ->
    client.database_blob_auditing_policies.get
  - client.databases.create_or_update_blob_auditing_policy ->
    client.database_blob_auditing_policies.create_or_update
  - client.servers.list_encryption_protectors, ->
    client.encryption_protectors.list_by_server
  - client.servers.get_encryption_protector ->
    client.encryption_protectors.get
  - client.servers.create_or_update_encryption_protector ->
    client.encryption_protectors.create_or_update
  - Database blob auditing policy state is required
  - Failover group resource now has required properties defined

**Features**

  - Add SQL DB, server, and pool PATCH operations
  - client.operations.list now returnes a full list of operations and
    not a limited subset (2014-04-01 to 2015-05-01-preview)

**Fixed bugs**

  - Fixed KeyError in server_azure_ad_administrators_operations.get

## 0.7.1 (2017-06-30)

  - Added support for server connection policies
  - Fixed error in
    databases_operations.create_or_update_threat_detection_policy

## 0.7.0 (2017-06-28)

**Features**

  - Backup/Restore related: RecoverableDatabase,
    RestorableDroppedDatabase, BackupLongTermRetentionVault,
    BackupLongTermRetentionPolicy, and GeoBackupPolicy
  - Data Masking rules and policies
  - Server communication links

**Breaking changes**

  - Renamed enum RestorePointTypes to RestorePointType
  - Renamed VnetFirewallRule and related operations to
    VirtualNetworkRule

## 0.6.0 (2017-06-13)

  - Updated Servers api version from 2014-04-01 to 2015-05-01-preview,
    which is SDK compatible and includes support for server managed
    identity
  - Added support for server keys and encryption protectors
  - Added support for check server name availability
  - Added support for virtual network firewall rules
  - Updated server azure ad admin from swagger
  - Minor nonfunctional updates to database blob auditing
  - Breaking changes DatabaseMetrics and ServerMetrics renamed to
    DatabaseUsage and ServerUsage. These were misleadingly named because
    metrics is a different API.
  - Added database metrics and elastic pool metrics

## 0.5.3 (2017-06-01)

  - Update minimal dependency to msrestazure 0.4.8

## 0.5.2 (2017-05-31)

**Features**

  - Added support for server active directory administrator, failover
    groups, and virtual network rules
  - Minor changes to database auditing support

## 0.5.1 (2017-04-28)

**Bugfixes**

  - Fix return exception in import/export

## 0.5.0 (2017-04-19)

**Breaking changes**

  - `SqlManagementClient.list_operations` is now
    `SqlManagementClient.operations.list`

**New features**

  - Added elastic pool capabilities to capabilities API.

**Notes**

  - This wheel package is now built with the azure wheel extension

## 0.4.0 (2017-03-22)

Capabilities and security policy features.

Also renamed several types and operations for improved clarify and
consistency.

Additions:

  - BlobAuditingPolicy APIs (e.g.
    databases.create_or_update_blob_auditing_policy)
  - ThreatDetectionPolicy APIs (e.g.
    databases.create_or_update_threat_detection_policy)
  - databases.list_by_server now supports $expand parameter
  - Capabilities APIs (e.g. capabilities.list_by_location)

Classes and enums renamed:

  - ServerFirewallRule -> FirewallRule
  - DatabaseEditions -> DatabaseEdition
  - ElasticPoolEditions -> ElasticPoolEdition
  - ImportRequestParameters -> ImportRequest
  - ExportRequestParameters -> ExportRequest
  - ImportExportOperationResponse -> ImportExportResponse
  - OperationMode -> ImportOperationMode
  - TransparentDataEncryptionStates -> TransparentDataEncryptionStatus

Classes removed:

  - Unused types: UpgradeHint, Schema, Table, Column

Operations renamed:

  - servers.get_by_resource_group -> servers.get
  - servers.create_or_update_firewall_rule ->
    firewall_rules.create_or_update, and similar for get, list, and
    delete
  - databases.import -> databases.create_import_operation
  - servers.import -> databases.import
  - databases.pause_data_warehouse -> databases.pause
  - databases.resume_data_warehouse -> databases.resume
  - recommended_elastic_pools.list ->
    recommended_elastic_pools.list_by_server

Operations removed:

  - Removed ImportExport operation results APIs since these are handled
    automatically by Azure async pattern.

## 0.3.3 (2017-03-14)

  - Add database blob auditing and threat detection operations

## 0.3.2 (2017-03-08)

  - Add import/export operations
  - Expanded documentation of create modes

## 0.3.1 (2017-03-01)

  - Added ‘filter’ param to list databases

## 0.3.0 (2017-02-27)

**Breaking changes**

  - Enums:
      - createMode renamed to CreateMode
      - Added ReadScale, SampleName, ServerState
  - Added missing Database properties (failover_group_id,
    restore_point_in_time, read_scale, sample_name)
  - Added missing ElasticPoolActivity properties ([requested](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/sql/azure-mgmt-sql)*)
  - Added missing ReplicationLink properties (is_termination_allowed,
    replication_mode)
  - Added missing Server properties ([external_administrator](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/sql/azure-mgmt-sql)*,
    state)
  - Added operations APIs
  - Removed unused Database.upgrade_hint property
  - Removed unused RecommendedDatabaseProperties class
  - Renamed incorrect RecommendedElasticPool.databases_property to
    databases
  - Made firewall rule start/end ip address required
  - Added missing kind property to many resources
  - Many doc clarifications

## 0.2.0 (2016-12-12)

**Breaking changes**

  - Parameters re-ordering (list_database_activity)
  - Flatten create_or_update_firewall_rule from "parameters" to
    "start_ip_address" and "end_ip_address"

## 0.1.0 (2016-11-02)

  - Initial Release
