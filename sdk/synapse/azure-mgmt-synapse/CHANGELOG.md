# Release History

## 1.0.0b1 (2020-12-10)

This is beta preview version.

This version uses a next-generation code generator that introduces important breaking changes, but also important new features (like unified authentication and async programming).

**General breaking changes**

- Credential system has been completly revamped:

  - `azure.common.credentials` or `msrestazure.azure_active_directory` instances are no longer supported, use the `azure-identity` classes instead: https://pypi.org/project/azure-identity/
  - `credentials` parameter has been renamed `credential`

- The `config` attribute no longer exists on a client, configuration should be passed as kwarg. Example: `MyClient(credential, subscription_id, enable_logging=True)`. For a complete set of
  supported options, see the [parameters accept in init documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)
- You can't import a `version` module anymore, use `__version__` instead
- Operations that used to return a `msrest.polling.LROPoller` now returns a `azure.core.polling.LROPoller` and are prefixed with `begin_`.
- Exceptions tree have been simplified and most exceptions are now `azure.core.exceptions.HttpResponseError` (`CloudError` has been removed).
- Most of the operation kwarg have changed. Some of the most noticeable:

  - `raw` has been removed. Equivalent feature can be found using `cls`, a callback that will give access to internal HTTP response for advanced user
  - For a complete set of
  supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/core/azure-core-tracing-opentelemetry) for an overview.

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
