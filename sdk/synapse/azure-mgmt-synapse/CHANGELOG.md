# Release History

## 0.6.0 (2020-12-17)

**Features**

  - Model DataMaskingPolicy has a new parameter managed_by
  - Model WorkspacePatchInfo has a new parameter encryption

## 0.5.0 (2020-11-23)

**Features**

  - Model SelfHostedIntegrationRuntimeStatus has a new parameter node_communication_channel_encryption_mode
  - Model MetadataSyncConfig has a new parameter sync_interval_in_minutes
  - Model BigDataPoolResourceInfo has a new parameter spark_config_properties
  - Model BigDataPoolResourceInfo has a new parameter session_level_packages_enabled
  - Model BigDataPoolResourceInfo has a new parameter have_library_requirements_changed
  - Model Workspace has a new parameter workspace_uid
  - Model Workspace has a new parameter managed_virtual_network_settings
  - Model Workspace has a new parameter purview_configuration
  - Model Workspace has a new parameter workspace_repository_configuration
  - Model Workspace has a new parameter encryption
  - Model PrivateLinkHub has a new parameter private_endpoint_connections
  - Model WorkspacePatchInfo has a new parameter managed_virtual_network_settings
  - Model WorkspacePatchInfo has a new parameter purview_configuration
  - Model WorkspacePatchInfo has a new parameter workspace_repository_configuration
  - Added operation SqlPoolSecurityAlertPoliciesOperations.list
  - Added operation SqlPoolTransparentDataEncryptionsOperations.list
  - Added operation IntegrationRuntimesOperations.disable_interactive_query
  - Added operation IntegrationRuntimesOperations.enable_interactive_query
  - Added operation SqlPoolRestorePointsOperations.get
  - Added operation SqlPoolRestorePointsOperations.delete
  - Added operation SqlPoolReplicationLinksOperations.get_by_name
  - Added operation SqlPoolTablesOperations.get
  - Added operation SqlPoolBlobAuditingPoliciesOperations.list_by_sql_pool
  - Added operation SqlPoolVulnerabilityAssessmentScansOperations.get
  - Added operation IntegrationRuntimeObjectMetadataOperations.list
  - Added operation SqlPoolVulnerabilityAssessmentRuleBaselinesOperations.get
  - Added operation SqlPoolSchemasOperations.get
  - Added operation SqlPoolSensitivityLabelsOperations.get
  - Added operation SqlPoolGeoBackupPoliciesOperations.list
  - Added operation IntegrationRuntimeMonitoringDataOperations.list
  - Added operation group DataMaskingRulesOperations
  - Added operation group WorkspaceManagedSqlServerUsagesOperations
  - Added operation group WorkspaceManagedSqlServerBlobAuditingPoliciesOperations
  - Added operation group ExtendedSqlPoolBlobAuditingPoliciesOperations
  - Added operation group SqlPoolWorkloadGroupOperations
  - Added operation group DataMaskingPoliciesOperations
  - Added operation group KeysOperations
  - Added operation group WorkspaceManagedSqlServerExtendedBlobAuditingPoliciesOperations
  - Added operation group SqlPoolWorkloadClassifierOperations
  - Added operation group WorkspaceManagedSqlServerRecoverableSqlpoolsOperations
  - Added operation group WorkspaceSqlAadAdminsOperations
  - Added operation group RestorableDroppedSqlPoolsOperations
  - Added operation group WorkspaceManagedSqlServerVulnerabilityAssessmentsOperations
  - Added operation group PrivateEndpointConnectionsPrivateLinkHubOperations
  - Added operation group SqlPoolColumnsOperations
  - Added operation group WorkspaceManagedSqlServerSecurityAlertPolicyOperations

**Breaking changes**

  - Operation PrivateEndpointConnectionsOperations.create has a new signature
  - Operation PrivateEndpointConnectionsOperations.create has a new signature
  - Operation SqlPoolMetadataSyncConfigsOperations.create has a new signature
  - Operation PrivateLinkHubsOperations.create_or_update has a new signature
  - Removed operation SqlPoolsOperations.rename
  - Removed operation IntegrationRuntimeObjectMetadataOperations.get
  - Removed operation IntegrationRuntimeMonitoringDataOperations.get

## 0.4.0 (2020-09-25)

**Features**

  - Model BigDataPoolResourceInfo has a new parameter is_compute_isolation_enabled
  - Model Workspace has a new parameter extra_properties
  - Model Sku has a new parameter capacity

## 0.3.0 (2020-06-17)

**Features**

  - Added operation group PrivateLinkHubsOperations

## 0.2.0 (2020-04-09)

**Features**

  - Model Workspace has a new parameter private_endpoint_connections
  - Model Workspace has a new parameter managed_virtual_network
  - Added operation IpFirewallRulesOperations.get
  - Added operation group IntegrationRuntimeCredentialsOperations
  - Added operation group IntegrationRuntimeAuthKeysOperations
  - Added operation group IntegrationRuntimeNodesOperations
  - Added operation group PrivateLinkResourcesOperations
  - Added operation group IntegrationRuntimeObjectMetadataOperations
  - Added operation group IntegrationRuntimeStatusOperations
  - Added operation group IntegrationRuntimeConnectionInfosOperations
  - Added operation group IntegrationRuntimeMonitoringDataOperations
  - Added operation group PrivateEndpointConnectionsOperations
  - Added operation group IntegrationRuntimeNodeIpAddressOperations
  - Added operation group IntegrationRuntimesOperations

## 0.1.0 (2020-02-27)

* Initial Release
