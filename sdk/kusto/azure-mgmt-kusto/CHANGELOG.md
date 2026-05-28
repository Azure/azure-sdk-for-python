# Release History

## 3.5.0 (2026-05-28)

### Features Added

  - Client `KustoManagementClient` added method `send_request`
  - Model `AttachedDatabaseConfiguration` added property `system_data`
  - Model `AttachedDatabaseConfigurationsCheckNameRequest` added property `type`
  - Model `ClusterCheckNameRequest` added property `type`
  - Model `ClusterPrincipalAssignment` added property `properties`
  - Model `ClusterPrincipalAssignment` added property `system_data`
  - Model `ClusterPrincipalAssignmentCheckNameRequest` added property `type`
  - Model `ClusterUpdate` added property `properties`
  - Model `ClusterUpdate` added property `system_data`
  - Model `CosmosDbDataConnection` added property `system_data`
  - Model `DataConnection` added property `system_data`
  - Model `DataConnectionCheckNameRequest` added property `type`
  - Model `Database` added property `system_data`
  - Model `DatabasePrincipalAssignment` added property `properties`
  - Model `DatabasePrincipalAssignment` added property `system_data`
  - Model `DatabasePrincipalAssignmentCheckNameRequest` added property `type`
  - Model `DatabasePrincipalListResult` added property `next_link`
  - Model `EventGridDataConnection` added property `properties`
  - Model `EventGridDataConnection` added property `system_data`
  - Model `EventGridDataConnectionWithManagedIdentity` added property `properties`
  - Model `EventGridDataConnectionWithManagedIdentity` added property `system_data`
  - Model `EventHubDataConnection` added property `properties`
  - Model `EventHubDataConnection` added property `system_data`
  - Model `EventHubDataConnectionWithManagedIdentity` added property `properties`
  - Model `EventHubDataConnectionWithManagedIdentity` added property `system_data`
  - Model `IotHubDataConnection` added property `properties`
  - Model `IotHubDataConnection` added property `system_data`
  - Model `LanguageExtensionsList` added property `next_link`
  - Model `ManagedPrivateEndpointsCheckNameRequest` added property `type`
  - Model `OperationResult` added property `error`
  - Model `OutboundNetworkDependenciesEndpoint` added property `system_data`
  - Model `ProxyResource` added property `system_data`
  - Model `ReadOnlyFollowingDatabase` added property `system_data`
  - Model `ReadWriteDatabase` added property `system_data`
  - Model `Resource` added property `system_data`
  - Model `SandboxCustomImage` added property `system_data`
  - Model `SandboxCustomImagesCheckNameRequest` added property `type`
  - Model `ScriptCheckNameRequest` added property `type`
  - Model `TrackedResource` added property `system_data`
  - Added model `ClusterPrincipalProperties`
  - Added model `DatabasePrincipalProperties`
  - Added model `EventGridConnectionProperties`
  - Added model `EventGridConnectionWithManagedIdentityProperties`
  - Added model `EventHubConnectionProperties`
  - Added model `EventHubConnectionWithManagedIdentityProperties`
  - Added model `FollowerDatabaseProperties`
  - Added model `IotHubConnectionProperties`
  - Added model `OperationResultErrorProperties`
  - Model `ClustersOperations` added parameter `etag` in method `begin_create_or_update`
  - Model `ClustersOperations` added parameter `match_condition` in method `begin_create_or_update`
  - Model `ClustersOperations` added parameter `etag` in method `begin_update`
  - Model `ClustersOperations` added parameter `match_condition` in method `begin_update`

### Breaking Changes

  - Model `ClusterPrincipalAssignment` deleted or renamed its instance variable `principal_id`
  - Model `ClusterPrincipalAssignment` deleted or renamed its instance variable `role`
  - Model `ClusterPrincipalAssignment` deleted or renamed its instance variable `tenant_id`
  - Model `ClusterPrincipalAssignment` deleted or renamed its instance variable `principal_type`
  - Model `ClusterPrincipalAssignment` deleted or renamed its instance variable `tenant_name`
  - Model `ClusterPrincipalAssignment` deleted or renamed its instance variable `principal_name`
  - Model `ClusterPrincipalAssignment` deleted or renamed its instance variable `provisioning_state`
  - Model `ClusterPrincipalAssignment` deleted or renamed its instance variable `aad_object_id`
  - Model `ClusterUpdate` deleted or renamed its instance variable `state`
  - Model `ClusterUpdate` deleted or renamed its instance variable `provisioning_state`
  - Model `ClusterUpdate` deleted or renamed its instance variable `uri`
  - Model `ClusterUpdate` deleted or renamed its instance variable `data_ingestion_uri`
  - Model `ClusterUpdate` deleted or renamed its instance variable `state_reason`
  - Model `ClusterUpdate` deleted or renamed its instance variable `trusted_external_tenants`
  - Model `ClusterUpdate` deleted or renamed its instance variable `optimized_autoscale`
  - Model `ClusterUpdate` deleted or renamed its instance variable `enable_disk_encryption`
  - Model `ClusterUpdate` deleted or renamed its instance variable `enable_streaming_ingest`
  - Model `ClusterUpdate` deleted or renamed its instance variable `virtual_network_configuration`
  - Model `ClusterUpdate` deleted or renamed its instance variable `key_vault_properties`
  - Model `ClusterUpdate` deleted or renamed its instance variable `enable_purge`
  - Model `ClusterUpdate` deleted or renamed its instance variable `language_extensions`
  - Model `ClusterUpdate` deleted or renamed its instance variable `enable_double_encryption`
  - Model `ClusterUpdate` deleted or renamed its instance variable `public_network_access`
  - Model `ClusterUpdate` deleted or renamed its instance variable `allowed_ip_range_list`
  - Model `ClusterUpdate` deleted or renamed its instance variable `engine_type`
  - Model `ClusterUpdate` deleted or renamed its instance variable `accepted_audiences`
  - Model `ClusterUpdate` deleted or renamed its instance variable `enable_auto_stop`
  - Model `ClusterUpdate` deleted or renamed its instance variable `restrict_outbound_network_access`
  - Model `ClusterUpdate` deleted or renamed its instance variable `allowed_fqdn_list`
  - Model `ClusterUpdate` deleted or renamed its instance variable `callout_policies`
  - Model `ClusterUpdate` deleted or renamed its instance variable `public_ip_type`
  - Model `ClusterUpdate` deleted or renamed its instance variable `virtual_cluster_graduation_properties`
  - Model `ClusterUpdate` deleted or renamed its instance variable `private_endpoint_connections`
  - Model `ClusterUpdate` deleted or renamed its instance variable `migration_cluster`
  - Model `ClusterUpdate` deleted or renamed its instance variable `zone_status`
  - Model `DatabasePrincipalAssignment` deleted or renamed its instance variable `principal_id`
  - Model `DatabasePrincipalAssignment` deleted or renamed its instance variable `role`
  - Model `DatabasePrincipalAssignment` deleted or renamed its instance variable `tenant_id`
  - Model `DatabasePrincipalAssignment` deleted or renamed its instance variable `principal_type`
  - Model `DatabasePrincipalAssignment` deleted or renamed its instance variable `tenant_name`
  - Model `DatabasePrincipalAssignment` deleted or renamed its instance variable `principal_name`
  - Model `DatabasePrincipalAssignment` deleted or renamed its instance variable `provisioning_state`
  - Model `DatabasePrincipalAssignment` deleted or renamed its instance variable `aad_object_id`
  - Model `EventGridDataConnection` deleted or renamed its instance variable `storage_account_resource_id`
  - Model `EventGridDataConnection` deleted or renamed its instance variable `event_grid_resource_id`
  - Model `EventGridDataConnection` deleted or renamed its instance variable `event_hub_resource_id`
  - Model `EventGridDataConnection` deleted or renamed its instance variable `consumer_group`
  - Model `EventGridDataConnection` deleted or renamed its instance variable `table_name`
  - Model `EventGridDataConnection` deleted or renamed its instance variable `mapping_rule_name`
  - Model `EventGridDataConnection` deleted or renamed its instance variable `data_format`
  - Model `EventGridDataConnection` deleted or renamed its instance variable `ignore_first_record`
  - Model `EventGridDataConnection` deleted or renamed its instance variable `blob_storage_event_type`
  - Model `EventGridDataConnection` deleted or renamed its instance variable `managed_identity_resource_id`
  - Model `EventGridDataConnection` deleted or renamed its instance variable `managed_identity_object_id`
  - Model `EventGridDataConnection` deleted or renamed its instance variable `database_routing`
  - Model `EventGridDataConnection` deleted or renamed its instance variable `provisioning_state`
  - Model `EventGridDataConnectionWithManagedIdentity` deleted or renamed its instance variable `storage_account_resource_id_for_managed_identity`
  - Model `EventGridDataConnectionWithManagedIdentity` deleted or renamed its instance variable `event_hub_resource_id_for_managed_identity`
  - Model `EventGridDataConnectionWithManagedIdentity` deleted or renamed its instance variable `event_grid_resource_id`
  - Model `EventGridDataConnectionWithManagedIdentity` deleted or renamed its instance variable `consumer_group`
  - Model `EventGridDataConnectionWithManagedIdentity` deleted or renamed its instance variable `table_name`
  - Model `EventGridDataConnectionWithManagedIdentity` deleted or renamed its instance variable `mapping_rule_name`
  - Model `EventGridDataConnectionWithManagedIdentity` deleted or renamed its instance variable `data_format`
  - Model `EventGridDataConnectionWithManagedIdentity` deleted or renamed its instance variable `ignore_first_record`
  - Model `EventGridDataConnectionWithManagedIdentity` deleted or renamed its instance variable `blob_storage_event_type`
  - Model `EventGridDataConnectionWithManagedIdentity` deleted or renamed its instance variable `managed_identity_resource_id`
  - Model `EventGridDataConnectionWithManagedIdentity` deleted or renamed its instance variable `managed_identity_object_id`
  - Model `EventGridDataConnectionWithManagedIdentity` deleted or renamed its instance variable `database_routing`
  - Model `EventGridDataConnectionWithManagedIdentity` deleted or renamed its instance variable `provisioning_state`
  - Model `EventHubDataConnection` deleted or renamed its instance variable `event_hub_resource_id`
  - Model `EventHubDataConnection` deleted or renamed its instance variable `consumer_group`
  - Model `EventHubDataConnection` deleted or renamed its instance variable `table_name`
  - Model `EventHubDataConnection` deleted or renamed its instance variable `mapping_rule_name`
  - Model `EventHubDataConnection` deleted or renamed its instance variable `data_format`
  - Model `EventHubDataConnection` deleted or renamed its instance variable `event_system_properties`
  - Model `EventHubDataConnection` deleted or renamed its instance variable `compression`
  - Model `EventHubDataConnection` deleted or renamed its instance variable `provisioning_state`
  - Model `EventHubDataConnection` deleted or renamed its instance variable `managed_identity_resource_id`
  - Model `EventHubDataConnection` deleted or renamed its instance variable `managed_identity_object_id`
  - Model `EventHubDataConnection` deleted or renamed its instance variable `database_routing`
  - Model `EventHubDataConnection` deleted or renamed its instance variable `retrieval_start_date`
  - Model `EventHubDataConnectionWithManagedIdentity` deleted or renamed its instance variable `event_hub_resource_id_for_managed_identity`
  - Model `EventHubDataConnectionWithManagedIdentity` deleted or renamed its instance variable `consumer_group`
  - Model `EventHubDataConnectionWithManagedIdentity` deleted or renamed its instance variable `table_name`
  - Model `EventHubDataConnectionWithManagedIdentity` deleted or renamed its instance variable `mapping_rule_name`
  - Model `EventHubDataConnectionWithManagedIdentity` deleted or renamed its instance variable `data_format`
  - Model `EventHubDataConnectionWithManagedIdentity` deleted or renamed its instance variable `event_system_properties`
  - Model `EventHubDataConnectionWithManagedIdentity` deleted or renamed its instance variable `compression`
  - Model `EventHubDataConnectionWithManagedIdentity` deleted or renamed its instance variable `provisioning_state`
  - Model `EventHubDataConnectionWithManagedIdentity` deleted or renamed its instance variable `managed_identity_resource_id`
  - Model `EventHubDataConnectionWithManagedIdentity` deleted or renamed its instance variable `managed_identity_object_id`
  - Model `EventHubDataConnectionWithManagedIdentity` deleted or renamed its instance variable `database_routing`
  - Model `EventHubDataConnectionWithManagedIdentity` deleted or renamed its instance variable `retrieval_start_date`
  - Model `FollowerDatabaseDefinitionGet` deleted or renamed its instance variable `cluster_resource_id`
  - Model `FollowerDatabaseDefinitionGet` deleted or renamed its instance variable `attached_database_configuration_name`
  - Model `FollowerDatabaseDefinitionGet` deleted or renamed its instance variable `database_name`
  - Model `FollowerDatabaseDefinitionGet` deleted or renamed its instance variable `table_level_sharing_properties`
  - Model `FollowerDatabaseDefinitionGet` deleted or renamed its instance variable `database_share_origin`
  - Model `IotHubDataConnection` deleted or renamed its instance variable `iot_hub_resource_id`
  - Model `IotHubDataConnection` deleted or renamed its instance variable `consumer_group`
  - Model `IotHubDataConnection` deleted or renamed its instance variable `table_name`
  - Model `IotHubDataConnection` deleted or renamed its instance variable `mapping_rule_name`
  - Model `IotHubDataConnection` deleted or renamed its instance variable `data_format`
  - Model `IotHubDataConnection` deleted or renamed its instance variable `event_system_properties`
  - Model `IotHubDataConnection` deleted or renamed its instance variable `shared_access_policy_name`
  - Model `IotHubDataConnection` deleted or renamed its instance variable `database_routing`
  - Model `IotHubDataConnection` deleted or renamed its instance variable `retrieval_start_date`
  - Model `IotHubDataConnection` deleted or renamed its instance variable `provisioning_state`
  - Deleted or renamed model `FollowerDatabaseListResultGet`
  - Deleted or renamed model `IssueType`
  - Deleted or renamed model `ListResourceSkusResult`
  - Deleted or renamed model `NetworkSecurityPerimeter`
  - Deleted or renamed model `NetworkSecurityPerimeterConfiguration`
  - Deleted or renamed model `NetworkSecurityPerimeterConfigurationList`
  - Deleted or renamed model `NetworkSecurityPerimeterConfigurationPropertiesProfile`
  - Deleted or renamed model `NetworkSecurityPerimeterConfigurationPropertiesResourceAssociation`
  - Deleted or renamed model `NetworkSecurityPerimeterConfigurationProvisioningState`
  - Deleted or renamed model `NspAccessRule`
  - Deleted or renamed model `NspAccessRuleDirection`
  - Deleted or renamed model `NspAccessRuleProperties`
  - Deleted or renamed model `NspAccessRulePropertiesSubscriptionsItem`
  - Deleted or renamed model `ProvisioningIssue`
  - Deleted or renamed model `ProvisioningIssueProperties`
  - Deleted or renamed model `ResourceAssociationAccessMode`
  - Deleted or renamed model `Severity`
  - Deleted or renamed model `SkuDescriptionList`
  - Method `ClustersOperations.begin_create_or_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `ClustersOperations.begin_create_or_update` deleted or renamed its parameter `if_none_match` of kind `positional_or_keyword`
  - Method `ClustersOperations.begin_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DatabasesOperations.begin_create_or_update` parameter `caller_role` changed default value from `str` to `none`
  - Method `DatabasesOperations.begin_create_or_update` changed its parameter `caller_role` from `positional_or_keyword` to `keyword_only`
  - Method `DatabasesOperations.begin_update` parameter `caller_role` changed default value from `str` to `none`
  - Method `DatabasesOperations.begin_update` changed its parameter `caller_role` from `positional_or_keyword` to `keyword_only`
  - Method `DatabasesOperations.list_by_cluster` changed its parameter `skiptoken` from `positional_or_keyword` to `keyword_only`
  - Method `ClustersOperations.begin_create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'cluster_name', 'parameters', 'if_match', 'if_none_match', 'kwargs']` to `['self', 'resource_group_name', 'cluster_name', 'parameters', 'etag', 'match_condition', 'kwargs']`

## 3.4.0 (2024-01-24)

### Features Added

  - Model `Cluster` added property `callout_policies`
  - Model `Cluster` added property `zone_status`
  - Enum `ClusterPrincipalRole` added member `ALL_DATABASES_MONITOR`
  - Model `ClusterUpdate` added property `callout_policies`
  - Model `ClusterUpdate` added property `zone_status`
  - Enum `LanguageExtensionImageName` added member `PYTHON3_11_7`
  - Enum `LanguageExtensionImageName` added member `PYTHON3_11_7_DL`
  - Model `SandboxCustomImage` added property `base_image_name`
  - Model `Script` added property `script_level`
  - Model `Script` added property `principal_permissions_action`
  - Added model `CalloutPoliciesList`
  - Added model `CalloutPolicy`
  - Added model `CalloutPolicyToRemove`
  - Added enum `CalloutType`
  - Added model `FollowerDatabaseDefinitionGet`
  - Added model `FollowerDatabaseListResultGet`
  - Added enum `OutboundAccess`
  - Added enum `PrincipalPermissionsAction`
  - Added enum `ScriptLevel`
  - Added enum `ZoneStatus`
  - Model `ClustersOperations` added method `begin_add_callout_policies`
  - Model `ClustersOperations` added method `begin_remove_callout_policy`
  - Model `ClustersOperations` added method `list_callout_policies`
  - Model `ClustersOperations` added method `list_follower_databases_get`

## 3.3.0 (2023-10-23)

### Features Added

  - Added operation group SandboxCustomImagesOperations
  - Model ClusterUpdate has a new parameter zones
  - Model EndpointDetail has a new parameter ip_address
  - Model LanguageExtension has a new parameter language_extension_custom_image_name
  - Model VirtualNetworkConfiguration has a new parameter state

## 3.2.0 (2023-07-21)

### Features Added

  - Added operation ClustersOperations.begin_migrate
  - Added operation group DatabaseOperations
  - Model Cluster has a new parameter migration_cluster
  - Model ClusterUpdate has a new parameter migration_cluster
  - Model DatabaseListResult has a new parameter next_link
  - Model ReadOnlyFollowingDatabase has a new parameter suspension_details
  - Model ReadWriteDatabase has a new parameter key_vault_properties
  - Model ReadWriteDatabase has a new parameter suspension_details
  - Operation DatabasesOperations.list_by_cluster has a new optional parameter skiptoken
  - Operation DatabasesOperations.list_by_cluster has a new optional parameter top

## 3.1.0 (2023-02-15)

### Features Added

  - Added operation group SkusOperations
  - Model LanguageExtension has a new parameter language_extension_image_name
  - Model SkuLocationInfoItem has a new parameter zone_details
  - Model TableLevelSharingProperties has a new parameter functions_to_exclude
  - Model TableLevelSharingProperties has a new parameter functions_to_include

## 3.1.0b1 (2022-12-27)

### Features Added

  - Added operation group SkusOperations
  - Model LanguageExtension has a new parameter language_extension_image_name
  - Model SkuLocationInfoItem has a new parameter zone_details

## 3.0.0 (2022-09-15)

### Features Added

  - Model AttachedDatabaseConfiguration has a new parameter database_name_override
  - Model AttachedDatabaseConfiguration has a new parameter database_name_prefix
  - Model EventHubDataConnection has a new parameter retrieval_start_date
  - Model FollowerDatabaseDefinition has a new parameter database_share_origin
  - Model FollowerDatabaseDefinition has a new parameter table_level_sharing_properties
  - Model IotHubDataConnection has a new parameter retrieval_start_date
  - Model ReadOnlyFollowingDatabase has a new parameter database_share_origin
  - Model ReadOnlyFollowingDatabase has a new parameter original_database_name
  - Model ReadOnlyFollowingDatabase has a new parameter table_level_sharing_properties

### Breaking Changes

  - Operation DatabasesOperations.begin_create_or_update has a new parameter caller_role
  - Operation DatabasesOperations.begin_update has a new parameter caller_role

## 2.2.0 (2022-02-22)

**Features**

  - Added operation group OperationsResultsLocationOperations
  - Model Cluster has a new parameter private_endpoint_connections
  - Model Cluster has a new parameter public_ip_type
  - Model Cluster has a new parameter virtual_cluster_graduation_properties
  - Model ClusterPrincipalAssignment has a new parameter aad_object_id
  - Model ClusterUpdate has a new parameter private_endpoint_connections
  - Model ClusterUpdate has a new parameter public_ip_type
  - Model ClusterUpdate has a new parameter virtual_cluster_graduation_properties
  - Model DatabasePrincipalAssignment has a new parameter aad_object_id
  - Model EventGridDataConnection has a new parameter database_routing
  - Model EventGridDataConnection has a new parameter event_grid_resource_id
  - Model EventGridDataConnection has a new parameter managed_identity_object_id
  - Model EventGridDataConnection has a new parameter managed_identity_resource_id
  - Model EventHubDataConnection has a new parameter database_routing
  - Model EventHubDataConnection has a new parameter managed_identity_object_id
  - Model IotHubDataConnection has a new parameter database_routing
  - Model OperationResult has a new parameter provisioning_state
  - Model Script has a new parameter script_content

## 2.1.0 (2021-09-22)

**Features**

  - Model Cluster has a new parameter accepted_audiences
  - Model Cluster has a new parameter allowed_fqdn_list
  - Model Cluster has a new parameter enable_auto_stop
  - Model Cluster has a new parameter allowed_ip_range_list
  - Model Cluster has a new parameter system_data
  - Model Cluster has a new parameter restrict_outbound_network_access
  - Model Cluster has a new parameter public_network_access
  - Model ClusterUpdate has a new parameter accepted_audiences
  - Model ClusterUpdate has a new parameter allowed_fqdn_list
  - Model ClusterUpdate has a new parameter enable_auto_stop
  - Model ClusterUpdate has a new parameter allowed_ip_range_list
  - Model ClusterUpdate has a new parameter restrict_outbound_network_access
  - Model ClusterUpdate has a new parameter public_network_access
  - Added operation AttachedDatabaseConfigurationsOperations.check_name_availability
  - Added operation ClustersOperations.list_outbound_network_dependencies_endpoints
  - Added operation group PrivateEndpointConnectionsOperations
  - Added operation group ManagedPrivateEndpointsOperations
  - Added operation group PrivateLinkResourcesOperations

## 2.0.0 (2021-04-26)

**Features**

  - Model EventHubDataConnection has a new parameter managed_identity_resource_id
  - Model Cluster has a new parameter etag
  - Model AttachedDatabaseConfiguration has a new parameter table_level_sharing_properties
  - Added operation group ScriptsOperations
  - Added operation group OperationsResultsOperations

**Breaking changes**

  - Operation ClustersOperations.begin_update has a new signature
  - Operation ClustersOperations.begin_create_or_update has a new signature

## 1.0.0 (2021-02-04)

- GA release

## 1.0.0b1 (2020-11-30)

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

## 0.7.0 (2020-03-20)

**Features**

- Model ClusterUpdate has a new parameter enable_purge
- Model ClusterUpdate has a new parameter language_extensions
- Model Cluster has a new parameter enable_purge
- Model Cluster has a new parameter language_extensions
- Added operation ClustersOperations.add_language_extensions
- Added operation ClustersOperations.remove_language_extensions
- Added operation ClustersOperations.list_language_extensions

## 0.6.0 (2020-01-31)

**Features**

- Model Cluster has a new parameter state_reason
- Model ReadWriteDatabase has a new parameter is_followed
- Model EventHubDataConnection has a new parameter compression
- Model ClusterUpdate has a new parameter state_reason
- Added operation ClustersOperations.diagnose_virtual_network
- Added operation group DatabasePrincipalAssignmentsOperations
- Added operation group ClusterPrincipalAssignmentsOperations

## 0.5.0 (2019-11-11)

**Features**

  - Model ClusterUpdate has a new parameter key_vault_properties
  - Model ClusterUpdate has a new parameter identity
  - Model Cluster has a new parameter key_vault_properties
  - Model Cluster has a new parameter identity
  - Added operation ClustersOperations.detach_follower_databases
  - Added operation ClustersOperations.list_follower_databases
  - Added operation group AttachedDatabaseConfigurationsOperations

**Breaking changes**

  - Operation DatabasesOperations.check_name_availability has a new
    signature
  - Model Database no longer has parameter soft_delete_period
  - Model Database no longer has parameter hot_cache_period
  - Model Database no longer has parameter statistics
  - Model Database no longer has parameter provisioning_state
  - Model Database has a new required parameter kind

## 0.4.0 (2019-08-27)

**Features**

  - Model Cluster has a new parameter enable_disk_encryption
  - Model Cluster has a new parameter zones
  - Model Cluster has a new parameter optimized_autoscale
  - Model Cluster has a new parameter virtual_network_configuration
  - Model Cluster has a new parameter enable_streaming_ingest
  - Model EventHubDataConnection has a new parameter
    event_system_properties
  - Model CheckNameResult has a new parameter reason
  - Model DatabasePrincipal has a new parameter tenant_name
  - Model ClusterUpdate has a new parameter enable_disk_encryption
  - Model ClusterUpdate has a new parameter optimized_autoscale
  - Model ClusterUpdate has a new parameter enable_streaming_ingest
  - Model ClusterUpdate has a new parameter
    virtual_network_configuration
  - Added operation DataConnectionsOperations.check_name_availability

**General breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if from some import. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - KustoManagementClient cannot be imported from
    `azure.mgmt.kusto.kusto_management_client` anymore (import from
    `azure.mgmt.kusto` works like before)
  - KustoManagementClientConfiguration import has been moved from
    `azure.mgmt.kusto.kusto_management_client` to
    `azure.mgmt.kusto`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.kusto.models.my_class` (import from
    `azure.mgmt.kusto.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.kusto.operations.my_class_operations` (import from
    `azure.mgmt.kusto.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.3.0 (2019-02-06)

**Features**

  - Model DatabaseUpdate has a new parameter hot_cache_period
  - Model DatabaseUpdate has a new parameter soft_delete_period
  - Model Database has a new parameter hot_cache_period
  - Model Database has a new parameter soft_delete_period
  - Added operation group DataConnectionsOperations

**Breaking changes**

  - Model DatabaseUpdate no longer has parameter
    hot_cache_period_in_days
  - Model DatabaseUpdate no longer has parameter etag
  - Model DatabaseUpdate no longer has parameter
    soft_delete_period_in_days
  - Model Database no longer has parameter tags
  - Model Database no longer has parameter etag
  - Model Database no longer has parameter hot_cache_period_in_days
  - Model Database no longer has parameter
    soft_delete_period_in_days
  - Model Cluster no longer has parameter etag
  - Model ClusterUpdate no longer has parameter etag
  - Removed operation group EventHubConnectionsOperations

## 0.2.0 (2018-11-27)

**Features**

  - Model Cluster has a new parameter uri
  - Model Cluster has a new parameter state
  - Model Cluster has a new parameter data_ingestion_uri
  - Model Cluster has a new parameter trusted_external_tenants
  - Model DatabaseUpdate has a new parameter etag
  - Model DatabaseUpdate has a new parameter statistics
  - Model DatabaseUpdate has a new parameter
    hot_cache_period_in_days
  - Model Database has a new parameter statistics
  - Model Database has a new parameter hot_cache_period_in_days
  - Model ClusterUpdate has a new parameter uri
  - Model ClusterUpdate has a new parameter etag
  - Model ClusterUpdate has a new parameter state
  - Model ClusterUpdate has a new parameter sku
  - Model ClusterUpdate has a new parameter tags
  - Model ClusterUpdate has a new parameter data_ingestion_uri
  - Model ClusterUpdate has a new parameter trusted_external_tenants
  - Added operation DatabasesOperations.list_principals
  - Added operation DatabasesOperations.check_name_availability
  - Added operation DatabasesOperations.add_principals
  - Added operation DatabasesOperations.remove_principals
  - Added operation ClustersOperations.list_skus
  - Added operation ClustersOperations.list_skus_by_resource
  - Added operation ClustersOperations.start
  - Added operation ClustersOperations.check_name_availability
  - Added operation ClustersOperations.stop
  - Added operation group EventHubConnectionsOperations

**Breaking changes**

  - Operation DatabasesOperations.update has a new signature
  - Operation ClustersOperations.update has a new signature
  - Operation DatabasesOperations.update has a new signature
  - Operation ClustersOperations.create_or_update has a new signature
  - Model Cluster has a new required parameter sku

## 0.1.0 (2018-08-09)

  - Initial Release
