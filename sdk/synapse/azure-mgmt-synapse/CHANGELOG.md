# Release History

## 2.1.0b5 (2022-04-15)

**Features**

  - Added operation group WorkspaceManagedSqlServerDedicatedSQLMinimalTlsSettingsOperations

## 2.1.0b4 (2022-01-11)

**Features**

  - Model DynamicExecutorAllocation has a new parameter max_executors
  - Model DynamicExecutorAllocation has a new parameter min_executors
  - Model ExtendedServerBlobAuditingPolicy has a new parameter is_devops_audit_enabled
  - Model ManagedIntegrationRuntime has a new parameter id
  - Model ManagedIntegrationRuntime has a new parameter reference_name
  - Model ManagedIntegrationRuntime has a new parameter type_managed_virtual_network_type
  - Model SelfHostedIntegrationRuntimeStatus has a new parameter newer_versions
  - Model SelfHostedIntegrationRuntimeStatus has a new parameter service_region
  - Model ServerBlobAuditingPolicy has a new parameter is_devops_audit_enabled
  - Model Workspace has a new parameter trusted_service_bypass_enabled

## 2.1.0b3 (2021-11-08)

**Features**

  - Model EventHubDataConnection has a new parameter managed_identity_resource_id
  - Added operation KustoPoolsOperations.list_skus

**Breaking changes**

  - Removed operation group KustoPoolOperations

## 2.1.0b2 (2021-10-09)

**Features**

  - Added operation group KustoPoolOperations
  - Added operation group KustoPoolChildResourceOperations
  - Added operation group KustoPoolsOperations
  - Added operation group KustoPoolAttachedDatabaseConfigurationsOperations
  - Added operation group KustoOperationsOperations
  - Added operation group KustoPoolDatabasesOperations
  - Added operation group KustoPoolDataConnectionsOperations
  - Added operation group KustoPoolPrincipalAssignmentsOperations
  - Added operation group KustoPoolDatabasePrincipalAssignmentsOperations

## 2.1.0b1 (2021-09-06)

**Features**

  - Model IntegrationRuntimeVNetProperties has a new parameter subnet_id
  - Model Workspace has a new parameter csp_workspace_admin_properties
  - Model Workspace has a new parameter settings
  - Model Workspace has a new parameter azure_ad_only_authentication
  - Model SqlPoolPatchInfo has a new parameter source_database_deletion_date
  - Model CustomerManagedKeyDetails has a new parameter kek_identity
  - Model DataLakeStorageAccountDetails has a new parameter resource_id
  - Model DataLakeStorageAccountDetails has a new parameter create_managed_private_endpoint
  - Model SqlPool has a new parameter source_database_deletion_date
  - Model ManagedIdentity has a new parameter user_assigned_identities
  - Model IntegrationRuntimeDataFlowProperties has a new parameter cleanup
  - Added operation IntegrationRuntimesOperations.list_outbound_network_dependencies_endpoints
  - Added operation PrivateEndpointConnectionsPrivateLinkHubOperations.get
  - Added operation group AzureADOnlyAuthenticationsOperations
  - Added operation group SparkConfigurationsOperations
  - Added operation group SparkConfigurationOperations

## 2.0.0 (2021-04-07)

**Features**

  - Model WorkspacePatchInfo has a new parameter public_network_access
  - Model Workspace has a new parameter public_network_access

**Breaking changes**

  - Model WorkspacePatchInfo no longer has parameter network_settings
  - Model Workspace no longer has parameter network_settings

## 1.0.0 (2021-03-10)

**Features**

  - Model WorkspacePatchInfo has a new parameter network_settings
  - Model WorkspacePatchInfo has a new parameter encryption
  - Model SqlPoolPatchInfo has a new parameter storage_account_type
  - Model BigDataPoolResourceInfo has a new parameter dynamic_executor_allocation
  - Model BigDataPoolResourceInfo has a new parameter last_succeeded_timestamp
  - Model BigDataPoolResourceInfo has a new parameter cache_size
  - Model BigDataPoolResourceInfo has a new parameter custom_libraries
  - Model Workspace has a new parameter network_settings
  - Model Workspace has a new parameter adla_resource_id
  - Model SqlPoolColumn has a new parameter is_computed
  - Model WorkspaceRepositoryConfiguration has a new parameter tenant_id
  - Model WorkspaceRepositoryConfiguration has a new parameter last_commit_id
  - Model SqlPool has a new parameter storage_account_type
  - Model SensitivityLabel has a new parameter rank
  - Model SensitivityLabel has a new parameter schema_name
  - Model SensitivityLabel has a new parameter table_name
  - Model SensitivityLabel has a new parameter managed_by
  - Model SensitivityLabel has a new parameter column_name
  - Added operation DataMaskingRulesOperations.get
  - Added operation WorkspaceManagedIdentitySqlControlSettingsOperations.begin_create_or_update
  - Added operation SqlPoolSensitivityLabelsOperations.update
  - Added operation SqlPoolGeoBackupPoliciesOperations.create_or_update
  - Added operation SqlPoolsOperations.rename
  - Added operation group PrivateLinkHubPrivateLinkResourcesOperations
  - Added operation group SqlPoolRecommendedSensitivityLabelsOperations
  - Added operation group LibraryOperations
  - Added operation group LibrariesOperations
  - Added operation group SqlPoolMaintenanceWindowOptionsOperations
  - Added operation group SqlPoolMaintenanceWindowsOperations
  - Added operation group WorkspaceManagedSqlServerRecoverableSqlPoolsOperations
  - Added operation group WorkspaceManagedSqlServerEncryptionProtectorOperations

**Breaking changes**

  - Model BigDataPoolResourceInfo no longer has parameter have_library_requirements_changed
  - Model ErrorResponse has a new signature
  - Model ErrorDetail has a new signature
  - Removed operation WorkspaceManagedIdentitySqlControlSettingsOperations.create_or_update
  - Removed operation group WorkspaceManagedSqlServerRecoverableSqlpoolsOperations

## 1.0.0b1 (2020-12-10)

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
